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

# 2. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM (IMPERIAL MODERNO · ART DÉCO)
PASTA_APP = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(PASTA_APP, "logo_imperial.png")
ICONE_PATH = os.path.join(PASTA_APP, "icone_imperial.png")

st.set_page_config(
    page_title="Barbearia Imperial - Agendamento & Portfólio",
    page_icon=ICONE_PATH if os.path.exists(ICONE_PATH) else "👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta: Esmeralda #081F19 · Esmeralda profunda #04120E · Champanhe #C9A86A · Champanhe claro #E6CF9E · Marfim #EFE8DA
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Antonio:wght@200;300;400;600&family=Montserrat:wght@300;400;500;600&display=swap');

    :root {
        --esmeralda: #081F19;
        --esmeralda-profunda: #04120E;
        --esmeralda-card: #0D2A22;
        --esmeralda-campo: #102F27;
        --borda: rgba(201, 168, 106, 0.22);
        --borda-forte: rgba(201, 168, 106, 0.55);
        --champanhe: #C9A86A;
        --champanhe-claro: #E6CF9E;
        --champanhe-escuro: #8F7444;
        --marfim: #EFE8DA;
        --cinza: #9DB0A7;
        --gradiente-champanhe: linear-gradient(135deg, #8F7444 0%, #C9A86A 40%, #E6CF9E 55%, #C9A86A 70%, #8F7444 100%);
        --sombra: 0 24px 48px -28px rgba(0, 0, 0, 0.9);
    }

    /* Base */
    html, body, [data-testid="stAppViewContainer"], .main {
        background:
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(201,168,106,0.10), transparent 60%),
            linear-gradient(180deg, var(--esmeralda) 0%, var(--esmeralda-profunda) 100%) fixed !important;
        color: var(--marfim);
        font-family: 'Montserrat', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2.5rem !important; max-width: 1200px; }
    p, li, label { font-family: 'Montserrat', sans-serif; }
    h1 span, h2 span, h3 span { font-family: inherit !important; }

    h1, h2, h3 {
        font-family: 'Antonio', sans-serif !important;
        color: var(--champanhe) !important;
        text-transform: uppercase;
        font-weight: 300 !important;
        letter-spacing: 0.12em;
    }
    div.imp-hero h1.imp-titulo { font-family: 'Antonio', sans-serif !important; padding: 0 !important; }
    h3 span { border: none !important; }
    h3 {
        font-size: 1.15rem !important;
        letter-spacing: 0.32em !important;
        display: flex; align-items: center; gap: 0.9rem;
        margin-top: 1.4rem !important;
    }
    h3::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, var(--borda-forte), transparent); }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background: var(--esmeralda) !important;
        border-right: 1px solid var(--borda);
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img { border: none !important; box-shadow: none !important; border-radius: 0 !important; aspect-ratio: auto !important; padding: 0 !important; background: transparent !important; mix-blend-mode: lighten; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: 0.5rem; display: flex; flex-direction: column; align-items: stretch; }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent;
        border: 1px solid var(--borda);
        border-radius: 4px;
        padding: 0.8rem 0.9rem !important;
        width: 100% !important;
        box-sizing: border-box;
        margin: 0 !important;
        transition: all 0.25s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { border-color: var(--champanhe); background: rgba(201,168,106,0.05); }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        border-color: var(--champanhe);
        background: linear-gradient(90deg, rgba(201,168,106,0.18), rgba(201,168,106,0.03));
        box-shadow: inset 3px 0 0 var(--champanhe);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        font-size: 0.72rem;
        color: var(--marfim);
    }
    .imp-side-label {
        font-family: 'Montserrat', sans-serif; color: var(--champanhe); font-size: 0.66rem;
        letter-spacing: 0.4em; text-transform: uppercase; margin: 0.6rem 0 0.7rem;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .imp-side-label::after { content: ""; flex: 1; height: 1px; background: var(--borda); }
    .imp-side-rodape {
        margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--borda);
        color: var(--cinza); font-size: 0.75rem; text-align: center; line-height: 1.8; letter-spacing: 0.05em;
    }

    /* Cabeçalho art déco */
    .imp-hero {
        position: relative;
        display: flex; align-items: center; justify-content: space-between; gap: 2rem;
        padding: 2.6rem 2.6rem;
        margin-bottom: 2rem;
        border: 1px solid var(--borda-forte);
        background:
            linear-gradient(135deg, rgba(201,168,106,0.09), transparent 50%),
            var(--esmeralda-card);
        box-shadow: var(--sombra);
    }
    .imp-hero::before {
        content: ""; position: absolute; inset: 7px;
        border: 1px solid var(--borda);
        pointer-events: none;
    }
    .imp-hero::after {
        content: "◆"; position: absolute; left: 50%; bottom: -0.62rem; transform: translateX(-50%);
        color: var(--champanhe); font-size: 0.8rem; background: var(--esmeralda); padding: 0 0.6rem;
    }
    .imp-kicker {
        font-family: 'Montserrat', sans-serif; color: var(--champanhe); letter-spacing: 0.45em;
        font-size: 0.68rem; font-weight: 500; text-transform: uppercase; margin-bottom: 0.7rem;
    }
    .imp-titulo {
        font-family: 'Antonio', sans-serif; font-weight: 300 !important; font-size: 3.2rem; line-height: 1.05;
        letter-spacing: 0.1em; text-transform: uppercase;
        background: var(--gradiente-champanhe); -webkit-background-clip: text; background-clip: text;
        color: transparent !important; margin: 0;
    }
    .imp-sub { color: var(--cinza); font-size: 0.98rem; margin-top: 0.9rem; max-width: 620px; line-height: 1.6; }
    .imp-ornamento { display: flex; align-items: center; gap: 0.6rem; color: var(--champanhe); margin: 1.1rem 0 0; font-size: 0.6rem; }
    .imp-ornamento span { height: 1px; width: 70px; background: var(--gradiente-champanhe); }
    .imp-brasao { mix-blend-mode: lighten; height: 150px; width: auto; flex-shrink: 0; opacity: 0.95; position: relative; z-index: 1; }

    /* Cartões */
    .imp-card {
        position: relative;
        background: var(--esmeralda-card);
        border: 1px solid var(--borda);
        padding: 1.6rem 1.5rem;
        margin-bottom: 1rem;
    }
    .imp-card::before {
        content: ""; position: absolute; top: -1px; left: 1.5rem; width: 48px; height: 2px; background: var(--champanhe);
    }
    .imp-card-titulo {
        font-family: 'Antonio', sans-serif; color: var(--champanhe); letter-spacing: 0.3em;
        font-size: 1.05rem; text-transform: uppercase; margin-bottom: 1rem; font-weight: 400;
    }
    .imp-linha { display: flex; gap: 0.9rem; padding: 0.75rem 0; border-top: 1px solid var(--borda); }
    .imp-linha:first-of-type { border-top: none; }
    .imp-linha .rot { color: var(--champanhe); font-size: 0.64rem; letter-spacing: 0.3em; text-transform: uppercase; }
    .imp-linha .val { color: var(--marfim); font-size: 0.95rem; margin-top: 0.2rem; }
    .imp-icone {
        color: var(--champanhe); font-size: 0.95rem; width: 2rem; height: 2rem; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        border: 1px solid var(--borda-forte); transform: rotate(45deg);
    }
    .imp-icone > i { transform: rotate(-45deg); font-style: normal; }
    .imp-selo {
        text-align: center; padding: 1.3rem 1.2rem;
        border-top: 1px solid var(--borda-forte); border-bottom: 1px solid var(--borda-forte);
        color: var(--champanhe-claro);
        font-family: 'Antonio', sans-serif; font-weight: 300; letter-spacing: 0.2em; text-transform: uppercase;
        font-size: 1.05rem; line-height: 1.6;
    }

    /* Portfólio */
    [data-testid="stColumn"] [data-testid="stImage"] img { aspect-ratio: 4 / 5; object-fit: cover; width: 100%; }
    [data-testid="stImage"] img { border-radius: 2px; border: 1px solid var(--borda-forte); padding: 6px; background: var(--esmeralda-card); box-shadow: var(--sombra); }
    .imp-legenda { padding: 0.9rem 0.2rem 1.6rem; border-bottom: 1px solid var(--borda); margin-bottom: 1.2rem; }
    .imp-legenda .nome { font-family: 'Antonio', sans-serif; color: var(--champanhe); font-size: 1.3rem; letter-spacing: 0.14em; text-transform: uppercase; }
    .imp-legenda .serv { color: var(--marfim); font-size: 0.9rem; margin-top: 0.2rem; }
    .imp-legenda .data { color: var(--cinza); font-size: 0.68rem; letter-spacing: 0.25em; text-transform: uppercase; margin-top: 0.5rem; }

    /* Campos */
    .stTextInput input, .stDateInput input, [data-baseweb="select"] > div, .stNumberInput input {
        background: var(--esmeralda-campo) !important;
        border: 1px solid var(--borda) !important;
        border-radius: 3px !important;
        color: var(--marfim) !important;
        min-height: 46px;
    }
    .stTextInput input:focus, .stDateInput input:focus, [data-baseweb="select"] > div:focus-within {
        border-color: var(--champanhe) !important;
        box-shadow: 0 0 0 1px var(--champanhe) !important;
    }
    [data-testid="stWidgetLabel"] p, .stTextInput label, .stSelectbox label, .stDateInput label {
        color: var(--champanhe) !important; font-size: 0.68rem !important; font-weight: 500;
        letter-spacing: 0.25em; text-transform: uppercase;
    }
    [data-baseweb="popover"] ul { background: var(--esmeralda-card) !important; }
    [data-baseweb="popover"] li:hover { background: rgba(201,168,106,0.15) !important; }

    /* Botões */
    .stButton>button {
        background: var(--gradiente-champanhe) !important;
        background-size: 200% 100% !important;
        color: var(--esmeralda) !important;
        border-radius: 3px !important;
        border: none !important;
        padding: 0.85rem 2rem !important;
        box-shadow: 0 14px 30px -14px rgba(201, 168, 106, 0.55);
        transition: all 0.35s ease !important;
    }
    .stButton>button p {
        color: var(--esmeralda) !important; font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important; letter-spacing: 0.28em; text-transform: uppercase; font-size: 0.78rem;
    }
    .stButton>button:hover {
        background-position: 100% 0 !important;
        transform: translateY(-1px);
        box-shadow: 0 18px 36px -12px rgba(201, 168, 106, 0.75) !important;
    }

    /* Agenda do barbeiro */
    [data-testid="stExpander"] {
        background: var(--esmeralda-card) !important;
        border: 1px solid var(--borda) !important;
        border-left: 3px solid var(--champanhe) !important;
        border-radius: 3px !important;
        margin-bottom: 0.8rem;
        overflow: hidden;
    }
    [data-testid="stExpander"] details { border: none !important; }
    [data-testid="stExpander"] summary:hover { color: var(--champanhe) !important; }
    [data-testid="stExpander"] summary p { font-family: 'Montserrat', sans-serif; font-weight: 500; letter-spacing: 0.05em; }
    [data-testid="stFileUploader"] section {
        background: var(--esmeralda-campo) !important;
        border: 1px dashed var(--champanhe-escuro) !important;
        border-radius: 3px !important;
    }
    code { color: var(--champanhe-claro) !important; background: rgba(201,168,106,0.12) !important; }

    /* Avisos */
    [data-testid="stAlert"] { border-radius: 3px !important; }
    hr { border-color: var(--borda) !important; }

    @media (max-width: 768px) {
        .imp-titulo { font-size: 2.2rem; }
        .imp-hero { padding: 1.8rem 1.4rem; }
        .imp-brasao { display: none; }
    }
</style>
""", unsafe_allow_html=True)

# COMPONENTES VISUAIS
def imagem_larga(origem, alvo=st):
    """Mostra a imagem ocupando toda a largura (compatível com versões novas e antigas do Streamlit)."""
    try:
        alvo.image(origem, width="stretch")
    except Exception:
        alvo.image(origem, use_container_width=True)

@st.cache_data
def brasao_base64():
    """Ícone do brasão embutido no cabeçalho (lido uma vez só)."""
    if not os.path.exists(ICONE_PATH):
        return ""
    import base64
    with open(ICONE_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()

def cabecalho(kicker, titulo, subtitulo=""):
    sub = f'<div class="imp-sub">{subtitulo}</div>' if subtitulo else ""
    b64 = brasao_base64()
    brasao = f'<img class="imp-brasao" src="data:image/png;base64,{b64}" alt="Brasão Imperial">' if b64 else ""
    st.markdown(f"""
    <div class="imp-hero">
        <div style="position:relative; z-index:1;">
            <div class="imp-kicker">{kicker}</div>
            <h1 class="imp-titulo">{titulo}</h1>
            {sub}
            <div class="imp-ornamento"><span></span>◆<span></span></div>
        </div>
        {brasao}
    </div>
    """, unsafe_allow_html=True)

# 3. NAVEGAÇÃO LATERAL
if os.path.exists(LOGO_PATH):
    imagem_larga(LOGO_PATH, st.sidebar)
else:
    st.sidebar.title("👑 Barbearia Imperial")
st.sidebar.markdown('<div class="imp-side-label">Navegação</div>', unsafe_allow_html=True)
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["Agendar Horário", "Portfólio dos Barbeiros", "Painel do Barbeiro"],
    label_visibility="collapsed"
)
st.sidebar.markdown('''
<div class="imp-side-rodape">
    Terça a Sábado · 09:00 às 19:00<br>
    Av. Principal, 1000 - Centro
</div>
''', unsafe_allow_html=True)

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
if menu == "Agendar Horário":
    cabecalho("Reserve sua experiência", "Faça o Seu Agendamento",
              "Escolha o serviço, selecione seu barbeiro de preferência e garanta seu horário exclusivo.")
    
    col_form, col_info = st.columns([2, 1])
    
    with col_form:
        st.subheader("I · Seus Dados e Atendimento")
        
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
        
        st.subheader("II · Data e Horário")
        
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
            
            if st.button("CONFIRMAR AGENDAMENTO"):
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
        st.markdown("""
        <div class="imp-card">
            <div class="imp-card-titulo">Barbearia Imperial</div>
            <div class="imp-linha"><div class="imp-icone"><i>⌖</i></div><div><div class="rot">Endereço</div><div class="val">Av. Principal, 1000 - Centro</div></div></div>
            <div class="imp-linha"><div class="imp-icone"><i>◷</i></div><div><div class="rot">Horário</div><div class="val">Terça a Sábado · 09:00 às 19:00</div></div></div>
            <div class="imp-linha"><div class="imp-icone"><i>✆</i></div><div><div class="rot">Contato</div><div class="val">(19) 99999-8888</div></div></div>
        </div>
        <div class="imp-selo">“Tradição, precisão e o cuidado que um rei merece.”</div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 2. MÓDULO DE PORTFÓLIO DOS BARBEIROS
# ==============================================================================
elif menu == "Portfólio dos Barbeiros":
    cabecalho("Galeria Imperial", "Portfólio dos Barbeiros",
              "Selecione um profissional da nossa equipe para visualizar a galeria de cortes realizados.")
    
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
                imagem_larga(item['foto_corte_url'])
                st.markdown(f"""
                <div class="imp-legenda">
                    <div class="nome">{item['barbeiros']['nome']}</div>
                    <div class="serv">{item['servicos']['nome']}</div>
                    <div class="data">{item['data_agendamento']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"Nenhum corte publicado no portfólio para **{barbeiro_filtro_nome}** até o momento.")

# ==============================================================================
# 3. MÓDULO DO PAINEL DO BARBEIRO
# ==============================================================================
elif menu == "Painel do Barbeiro":
    cabecalho("Área restrita", "Painel do Barbeiro", "Acesse sua agenda do dia e finalize seus atendimentos.")
    
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
            st.subheader(f"Sua Agenda · {data_filtro.strftime('%d/%m/%Y')}")
            
            if agenda:
                for a in agenda:
                    with st.expander(f"{a['horario'][:5]}  ·  {a['cliente_nome']}  ·  {a['servicos']['nome']}  —  {a['status']}"):
                        st.write(f"**Cliente:** {a['cliente_nome']}")
                        st.write(f"**Contato:** {a['cliente_telefone']}")
                        st.write(f"**Serviço:** {a['servicos']['nome']} (R$ {a['servicos']['preco']:.2f})")
                        st.write(f"**Status Atual:** `{a['status']}`")
                        
                        if a['status'] == 'AGENDADO':
                            if st.button(f"INICIAR CORTE", key=f"init_{a['id']}"):
                                supabase.table('agendamentos').update({'status': 'EM ANDAMENTO'}).eq('id', a['id']).execute()
                                st.rerun()
                                
                        elif a['status'] == 'EM ANDAMENTO':
                            st.info("📸 **REGRA OBRIGATÓRIA**: Envie a foto do corte para finalizar e publicar no seu portfólio.")
                            foto_file = st.file_uploader(f"Foto do Resultado (Corte #{a['id']}):", type=['png', 'jpg', 'jpeg'], key=f"file_{a['id']}")
                            
                            if foto_file is not None:
                                if st.button(f"ENVIAR FOTO E FINALIZAR", key=f"fin_{a['id']}"):
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