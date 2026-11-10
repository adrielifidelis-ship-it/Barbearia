import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. CARREGAR VARIÁVEIS DE AMBIENTE (.env LOCAL OU SECRETS NA NUVEM)
load_dotenv()

# Tenta ler do .env local; se não encontrar, busca nos Secrets do Streamlit Cloud
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

@st.cache_resource
def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("⚠️ As chaves SUPABASE_URL e SUPABASE_KEY não foram encontradas! Configure-as no .env ou nos Secrets do Streamlit.")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# 2. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM (CSS PREMIUM)
st.set_page_config(
    page_title="Barbearia Imperial - Agendamento & Portfólio",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização em CSS customizado (Preto, Grafite, Dourado #D4AF37)
st.markdown("""
<style>
    .main { background-color: #0F0F0F; color: #F5F5F5; }
    .stCard { background-color: #1A1A1A; border: 1px solid #333333; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #D4AF37 !important; color: #000000 !important; font-weight: bold !important; border-radius: 8px !important; border: none !important; padding: 10px 24px !important; }
    .stButton>button:hover { background-color: #F1C40F !important; box-shadow: 0 0 10px rgba(212, 175, 55, 0.5) !important; }
</style>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO LATERAL
st.sidebar.title("💈 Barbearia Imperial")
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["📅 Agendamento de Serviços", "💈 Portfólio dos Barbeiros", "🔐 Painel do Barbeiro"]
)

# FUNÇÕES AUXILIARES DE CONSULTA AO SUPABASE
def obter_barbeiros():
    try:
        res = supabase.table('barbeiros').select('*').eq('ativo', True).order('id').execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao buscar barbeiros: {e}")
        return []

def obter_servicos():
    try:
        res = supabase.table('servicos').select('*').order('id').execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao buscar serviços: {e}")
        return []

def obter_agendamentos_barbeiro_data(barbeiro_id, data_str):
    try:
        res = supabase.table('agendamentos') \
            .select('*') \
            .eq('barbeiro_id', barbeiro_id) \
            .eq('data_agendamento', data_str) \
            .neq('status', 'CANCELADO') \
            .execute()
        return res.data if res.data else []
    except Exception:
        return []

# ==============================================================================
# 1. MÓDULO DE AGENDAMENTO DE SERVIÇOS
# ==============================================================================
if menu == "📅 Agendamento de Serviços":
    st.title("💈 Faça o Seu Agendamento")
    st.write("Escolha o serviço, selecione seu barbeiro de preferência e garanta seu horário exclusivo.")
    
    col_form, col_info = st.columns([2, 1])
    
    with col_form:
        st.subheader("1. Seus Dados e Escolha do Atendimento")
        
        nome_cliente = st.text_input("Seu Nome Completo:")
        telefone_cliente = st.text_input("WhatsApp / Telefone de Contato:")
        
        servicos = obter_servicos()
        barbeiros = obter_barbeiros()
        
        if not servicos or not barbeiros:
            st.warning("⚠️ Carregando barbeiros e serviços...")
            st.stop()
            
        dict_servicos = {f"{s['nome']} - R$ {s['preco']:.2f} ({s['duracao_minutos']} min)": s for s in servicos}
        servico_selecionado_str = st.selectbox("Selecione o Serviço:", list(dict_servicos.keys()))
        obj_servico = dict_servicos[servico_selecionado_str]
        
        dict_barbeiros = {f"{b['nome']} ({b['especialidade']})": b for b in barbeiros}
        barbeiro_selecionado_str = st.selectbox("Selecione o Barbeiro de Escolha:", list(dict_barbeiros.keys()))
        obj_barbeiro = dict_barbeiros[barbeiro_selecionado_str]
        
        st.subheader("2. Escolha a Data e Horário Disponível")
        
        data_escolhida = st.date_input("Data do Atendimento:", min_value=date.today())
        data_str = data_escolhida.strftime("%Y-%m-%d")
        
        # Grade de Horários (09:00 às 19:00)
        horarios_possiveis = []
        hora_atual = datetime.strptime("09:00", "%H:%M")
        hora_fim = datetime.strptime("19:00", "%H:%M")
        
        while hora_atual <= hora_fim:
            horarios_possiveis.append(hora_atual.strftime("%H:%M"))
            hora_atual += timedelta(minutes=30)
            
        agendamentos_existentes = obter_agendamentos_barbeiro_data(obj_barbeiro['id'], data_str)
        horarios_ocupados = [a['horario'][:5] for a in agendamentos_existentes]
        horarios_livres = [h for h in horarios_possiveis if h not in horarios_ocupados]
        
        if horarios_livres:
            # Substituído por selectbox para facilitar a troca de horários
            horario_escolhido = st.selectbox("Horários Disponíveis para Seleção:", options=horarios_livres)
            
            if st.button("🚀 CONFIRMAR AGENDAMENTO"):
                if not nome_cliente or not telefone_cliente:
                    st.error("Preencha seu nome e telefone antes de confirmar!")
                else:
                    try:
                        novo_agendamento = {
                            'cliente_nome': nome_cliente,
                            'cliente_telefone': telefone_cliente,
                            'barbeiro_id': obj_barbeiro['id'],
                            'servico_id': obj_servico['id'],
                            'data_agendamento': data_str,
                            'horario': horario_escolhido,
                            'status': 'AGENDADO'
                        }
                        supabase.table('agendamentos').insert(novo_agendamento).execute()
                        st.balloons()
                        st.success(f"🎉 Agendamento confirmado para **{nome_cliente}** com **{obj_barbeiro['nome']}** às **{horario_escolhido}** ({data_escolhida.strftime('%d/%m/%Y')})!")
                    except Exception as e:
                        st.error(f"Erro ao salvar agendamento: {str(e)}")
        else:
            st.error("❌ Não há horários livres para este barbeiro nesta data. Selecione outro dia.")

    with col_info:
        st.subheader("📍 Barbearia Imperial")
        st.write("**Endereço:** Av. Principal, 1000 - Centro")
        st.write("**Horário:** Terça a Sábado - 09:00 às 19:00")
        st.write("**Contato:** (19) 99999-8888")

# ==============================================================================
# 2. MÓDULO DE PORTFÓLIO DOS BARBEIROS
# ==============================================================================
elif menu == "💈 Portfólio dos Barbeiros":
    st.title("💈 Portfólio de Trabalhos dos Barbeiros")
    st.write("Selecione um profissional da nossa equipe para visualizar a galeria de cortes realizados.")
    
    barbeiros = obter_barbeiros()
    lista_nomes_barbeiros = ["Todos os Barbeiros"] + [b['nome'] for b in barbeiros]
    
    barbeiro_filtro_nome = st.selectbox("Selecione o Barbeiro de Escolha:", lista_nomes_barbeiros)
    
    query = supabase.table('agendamentos') \
        .select('*, barbeiros(nome), servicos(nome)') \
        .eq('status', 'FINALIZADO') \
        .not_.is_('foto_corte_url', 'null')
        
    if barbeiro_filtro_nome != "Todos os Barbeiros":
        b_obj = next(b for b in barbeiros if b['nome'] == barbeiro_filtro_nome)
        query = query.eq('barbeiro_id', b_obj['id'])
        
    res = query.order('id', desc=True).execute()
    portfólio_itens = res.data if res.data else []
    
    if portfólio_itens:
        cols = st.columns(3)
        for idx, item in enumerate(portfólio_itens):
            with cols[idx % 3]:
                st.image(item['foto_corte_url'], use_column_width=True)
                st.write(f"**Barbeiro:** {item['barbeiros']['nome']}")
                st.write(f"**Serviço:** {item['servicos']['nome']}")
                st.caption(f"Data: {item['data_agendamento']}")
                st.divider()
    else:
        st.info(f"Nenhum corte publicado no portfólio para **{barbeiro_filtro_nome}** até o momento.")

# ==============================================================================
# 3. MÓDULO DO PAINEL DO BARBEIRO
# ==============================================================================
elif menu == "🔐 Painel do Barbeiro":
    st.title("🔐 Painel Restrito do Barbeiro")
    
    barbeiros = obter_barbeiros()
    if not barbeiros:
        st.warning("Carregando barbeiros...")
        st.stop()
        
    dict_b = {b['nome']: b for b in barbeiros}
    
    col_auth1, col_auth2 = st.columns(2)
    with col_auth1:
        barbeiro_login = st.selectbox("Selecione o seu nome:", list(dict_b.keys()))
    with col_auth2:
        pin_ingresso = st.text_input("Digite sua Senha/PIN de Acesso (Padrão: 123456):", type="password")
        
    if pin_ingresso:
        obj_b = dict_b[barbeiro_login]
        if pin_ingresso == obj_b.get('pin_acesso', '123456'):
            st.success(f"Bem-vindo(a) ao painel, **{obj_b['nome']}**!")
            
            data_filtro = st.date_input("Agenda do Dia:", value=date.today())
            data_str = data_filtro.strftime("%Y-%m-%d")
            
            res = supabase.table('agendamentos') \
                .select('*, servicos(nome, preco)') \
                .eq('barbeiro_id', obj_b['id']) \
                .eq('data_agendamento', data_str) \
                .order('horario') \
                .execute()
                
            agenda = res.data if res.data else []
            st.subheader(f"📋 Sua Agenda ({data_filtro.strftime('%d/%m/%Y')})")
            
            if agenda:
                for a in agenda:
                    with st.expander(f"⏰ {a['horario'][:5]} - {a['cliente_nome']} ({a['servicos']['nome']}) | Status: {a['status']}"):
                        st.write(f"**Cliente:** {a['cliente_nome']}")
                        st.write(f"**Contato:** {a['cliente_telefone']}")
                        st.write(f"**Serviço:** {a['servicos']['nome']} (R$ {a['servicos']['preco']:.2f})")
                        st.write(f"**Status Atual:** `{a['status']}`")
                        
                        if a['status'] == 'AGENDADO':
                            if st.button(f"▶️ Iniciar Corte", key=f"init_{a['id']}"):
                                supabase.table('agendamentos').update({'status': 'EM ANDAMENTO'}).eq('id', a['id']).execute()
                                st.rerun()
                                
                        elif a['status'] == 'EM ANDAMENTO':
                            st.info("📸 **REGRA OBRIGATÓRIA**: Envie a foto do corte para finalizar e publicar no seu portfólio.")
                            foto_file = st.file_uploader(f"Foto do Resultado (Corte #{a['id']}):", type=['png', 'jpg', 'jpeg'], key=f"file_{a['id']}")
                            
                            if foto_file is not None:
                                if st.button(f"✅ Enviar Foto & Finalizar Corte", key=f"fin_{a['id']}"):
                                    try:
                                        file_ext = foto_file.name.split('.')[-1]
                                        file_path = f"corte_{a['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                                        bytes_data = foto_file.getvalue()
                                        
                                        supabase.storage.from_('cortes-portfolio').upload(
                                            path=file_path,
                                            file=bytes_data,
                                            file_options={"content-type": foto_file.type}
                                        )
                                        
                                        public_url = supabase.storage.from_('cortes-portfolio').get_public_url(file_path)
                                        
                                        supabase.table('agendamentos').update({
                                            'status': 'FINALIZADO',
                                            'foto_corte_url': public_url
                                        }).eq('id', a['id']).execute()
                                        
                                        st.success("🎉 Atendimento finalizado e foto adicionada ao seu portfólio!")
                                        st.rerun()
                                    except Exception as ex:
                                        st.error(f"Erro ao enviar foto: {str(ex)}")
                                        
                        elif a['status'] == 'FINALIZADO':
                            st.success("✅ Atendimento Finalizado")
                            if a.get('foto_corte_url'):
                                st.image(a['foto_corte_url'], caption="Foto no Portfólio", width=250)
            else:
                st.info("Nenhum agendamento encontrado para você nesta data.")
        else:
            st.error("Senha/PIN incorreto! A senha padrão é `123456`.")