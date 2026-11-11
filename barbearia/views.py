import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from supabase import create_client
from django.shortcuts import render, redirect
from django.http import JsonResponse

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. TELA DE AGENDAMENTO (CLIENTE)
def agendamento(request):
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        # Novo Agendamento
        if acao == 'agendar' or not acao:
            cliente_nome = request.POST.get('nome')
            cliente_telefone = request.POST.get('telefone')
            barbeiro_id = request.POST.get('barbeiro_id')
            servico_id = request.POST.get('servico_id')
            data_agendamento = request.POST.get('data')
            horario = request.POST.get('horario')

            supabase.table('agendamentos').insert({
                'cliente_nome': cliente_nome,
                'cliente_telefone': cliente_telefone,
                'barbeiro_id': barbeiro_id,
                'servico_id': servico_id,
                'data_agendamento': data_agendamento,
                'horario': horario,
                'status': 'AGENDADO'
            }).execute()

            return render(request, 'agendamento_sucesso.html', {
                'nome': cliente_nome, 'horario': horario, 'data': data_agendamento
            })

        # Cancelar Agendamento pelo Cliente
        elif acao == 'cancelar_cliente':
            agendamento_id = request.POST.get('agendamento_id')
            supabase.table('agendamentos').update({'status': 'CANCELADO'}).eq('id', agendamento_id).execute()
            
        # Reagendar pelo Cliente
        elif acao == 'reagendar_cliente':
            agendamento_id = request.POST.get('agendamento_id')
            nova_data = request.POST.get('nova_data')
            novo_horario = request.POST.get('novo_horario')
            supabase.table('agendamentos').update({
                'data_agendamento': nova_data,
                'horario': novo_horario,
                'status': 'AGENDADO'
            }).eq('id', agendamento_id).execute()

    # Busca agendamentos do cliente por telefone se informado
    telefone_busca = request.GET.get('telefone_busca')
    meus_agendamentos = []
    if telefone_busca:
        meus_agendamentos = supabase.table('agendamentos').select('*, barbeiros(nome), servicos(nome)').eq('cliente_telefone', telefone_busca).neq('status', 'CANCELADO').order('data_agendamento', desc=True).execute().data

    barbeiros = supabase.table('barbeiros').select('*').eq('ativo', True).order('id').execute().data
    servicos = supabase.table('servicos').select('*').order('id').execute().data
    return render(request, 'agendamento.html', {
        'barbeiros': barbeiros, 
        'servicos': servicos,
        'meus_agendamentos': meus_agendamentos,
        'telefone_busca': telefone_busca
    })

# API DE HORÁRIOS LIVRES
def buscar_horarios(request):
    barbeiro_id = request.GET.get('barbeiro_id')
    data_str = request.GET.get('data')

    horarios_possiveis = []
    hora_atual = datetime.strptime("09:00", "%H:%M")
    hora_fim = datetime.strptime("19:00", "%H:%M")
    while hora_atual <= hora_fim:
        horarios_possiveis.append(hora_atual.strftime("%H:%M"))
        hora_atual += timedelta(minutes=30)

    agendamentos = supabase.table('agendamentos').select('horario').eq('barbeiro_id', barbeiro_id).eq('data_agendamento', data_str).neq('status', 'CANCELADO').execute().data
    ocupados = [a['horario'][:5] for a in agendamentos]
    livres = [h for h in horarios_possiveis if h not in ocupados]

    return JsonResponse({'horarios': livres})

# 2. PORTFÓLIO
def portfolio(request):
    barbeiro_id = request.GET.get('barbeiro_id')
    barbeiros = supabase.table('barbeiros').select('*').eq('ativo', True).execute().data

    query = supabase.table('agendamentos').select('*, barbeiros(nome), servicos(nome)').eq('status', 'FINALIZADO').not_.is_('foto_corte_url', 'null')
    if barbeiro_id and barbeiro_id != "todos":
        query = query.eq('barbeiro_id', barbeiro_id)
    
    cortes = query.order('id', desc=True).execute().data
    return render(request, 'portfolio.html', {'cortes': cortes, 'barbeiros': barbeiros, 'barbeiro_selecionado': barbeiro_id})

# 3. PAINEL DO BARBEIRO
def painel_barbeiro(request):
    barbeiros = supabase.table('barbeiros').select('*').eq('ativo', True).execute().data
    agendamentos = []
    barbeiro_logado = None
    erro_pin = False
    data_filtro = request.GET.get('data_filtro') or request.POST.get('data_filtro') or date.today().strftime("%Y-%m-%d")

    if request.method == 'POST':
        barbeiro_id = request.POST.get('barbeiro_id')
        pin = request.POST.get('pin')
        acao = request.POST.get('acao')

        barbeiro_obj = next((b for b in barbeiros if str(b['id']) == str(barbeiro_id)), None)
        if barbeiro_obj and pin == barbeiro_obj.get('pin_acesso', '123456'):
            barbeiro_logado = barbeiro_obj
            agendamento_id = request.POST.get('agendamento_id')

            if acao == 'aceitar':
                supabase.table('agendamentos').update({'status': 'ACEITO'}).eq('id', agendamento_id).execute()
            elif acao == 'cancelar':
                supabase.table('agendamentos').update({'status': 'CANCELADO'}).eq('id', agendamento_id).execute()
            elif acao == 'reagendar':
                nova_data = request.POST.get('nova_data')
                novo_horario = request.POST.get('novo_horario')
                supabase.table('agendamentos').update({
                    'data_agendamento': nova_data,
                    'horario': novo_horario,
                    'status': 'REAGENDADO'
                }).eq('id', agendamento_id).execute()
            elif acao == 'iniciar':
                supabase.table('agendamentos').update({'status': 'EM ANDAMENTO'}).eq('id', agendamento_id).execute()
            elif acao == 'finalizar':
                foto = request.FILES.get('foto')
                if foto:
                    file_ext = foto.name.split('.')[-1]
                    file_path = f"corte_{agendamento_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                    bytes_data = foto.read()
                    supabase.storage.from_('cortes-portfolio').upload(file_path, bytes_data, {"content-type": foto.content_type})
                    public_url = supabase.storage.from_('cortes-portfolio').get_public_url(file_path)
                    supabase.table('agendamentos').update({'status': 'FINALIZADO', 'foto_corte_url': public_url}).eq('id', agendamento_id).execute()

            agendamentos = supabase.table('agendamentos').select('*, servicos(nome, preco)').eq('barbeiro_id', barbeiro_id).eq('data_agendamento', data_filtro).order('horario').execute().data
        else:
            erro_pin = True

    return render(request, 'painel.html', {
        'barbeiros': barbeiros, 
        'agendamentos': agendamentos, 
        'barbeiro_logado': barbeiro_logado, 
        'erro_pin': erro_pin,
        'data_filtro': data_filtro
    })