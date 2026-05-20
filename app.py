"""
NEDOCS — Instituto Central do Hospital das Clínicas · FMUSP
Calculadora de Superlotação do Serviço de Urgência
Lean nas Emergências
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEDOCS · ICHC",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CSS INSTITUCIONAL ICHC
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}

/* Header institucional */
.header-ichc {
    background: white;
    border-bottom: 3px solid #0077C8;
    padding: 16px 0 12px 0;
    margin: -1rem -1rem 2rem -1rem;
}
.header-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 2rem;
}
.header-title {
    text-align: right;
}
.header-title h1 {
    font-size: 22px;
    font-weight: 700;
    color: #0077C8;
    margin: 0;
    letter-spacing: -0.3px;
}
.header-title p {
    font-size: 12px;
    color: #009CA6;
    margin: 2px 0 0 0;
}

/* Seções */
.sec-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 2rem 0 1rem 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #0077C815;
}
.sec-num {
    background: #0077C8;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    flex-shrink: 0;
}
.sec-title {
    font-size: 17px;
    font-weight: 700;
    color: #0077C8;
    margin: 0;
}

/* Cards de variáveis */
.var-card {
    background: #F0F7FF;
    border: 1px solid #0077C820;
    border-left: 4px solid #0077C8;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.var-card-letter {
    font-size: 28px;
    font-weight: 800;
    color: #0077C8;
    line-height: 1;
    float: left;
    margin-right: 14px;
    margin-top: 2px;
}
.var-card-title { font-size: 14px; font-weight: 700; color: #1A1A2E; margin: 0 0 3px 0; }
.var-card-desc  { font-size: 12px; color: #555; margin: 0; line-height: 1.4; }
.clearfix { clear: both; }

/* Resultado NEDOCS */
.resultado-box {
    border-radius: 12px;
    padding: 28px 24px;
    text-align: center;
    margin-bottom: 16px;
}
.res-hora   { font-size: 12px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px; }
.res-score  { font-size: 72px; font-weight: 800; line-height: 1; margin-bottom: 8px; }
.res-nivel  { font-size: 16px; font-weight: 700; padding: 4px 16px; border-radius: 20px; display: inline-block; }
.res-vars   { font-size: 11px; margin-top: 14px; color: #555; line-height: 1.8; text-align: left; }

/* FG cards */
.fg-box {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 18px 20px;
    height: 100%;
}
.fg-letter { font-size: 36px; font-weight: 800; line-height: 1; margin-bottom: 2px; }
.fg-desc   { font-size: 11px; color: #888; margin-bottom: 12px; }
.fg-pac    { font-size: 14px; font-weight: 600; color: #1A1A2E; margin-bottom: 4px; }
.fg-val    { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.fg-det    { font-size: 11px; color: #888; line-height: 1.6; }

/* Escala */
.escala-item {
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
}
.escala-range { font-weight: 700; }
.escala-nome  { font-weight: 400; }

/* Fórmula */
.formula-box {
    background: #0077C808;
    border: 1px dashed #0077C840;
    border-radius: 8px;
    padding: 12px 18px;
    text-align: center;
    font-size: 14px;
    color: #0077C8;
    font-weight: 600;
    letter-spacing: 0.3px;
    margin-bottom: 1.5rem;
}

/* Stickers de variável calculada */
.badge-auto {
    background: #009CA615;
    color: #009CA6;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 10px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-manual {
    background: #FAB72115;
    color: #CE5E2A;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 10px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Divider */
hr { border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────
UNIDADES_PS_ORIGEM = ['E04AA','E4AF','E4FF','E4SA','U04AA','SAGUAO','SALA ESPERA']
BLOQUEIO_G         = UNIDADES_PS_ORIGEM + ['SCC','E4AB','E04CC','U04GN']

ESCALA = [
    (0,   20,  "Normal",                     "#4ade80", "#f0fdf4"),
    (21,  60,  "Pouco movimentado",          "#86efac", "#f0fdf4"),
    (61,  100, "Movimentado",                "#facc15", "#fefce8"),
    (101, 140, "Superlotado",                "#fb923c", "#fff7ed"),
    (141, 180, "Muito superlotado",          "#f87171", "#fef2f2"),
    (181, 9999,"Perigosamente superlotado",  "#c026d3", "#fdf4ff"),
]

# ─────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────
def eh_ps(texto):
    if pd.isna(texto): return False
    t = str(texto).upper()
    return any(c in t for c in UNIDADES_PS_ORIGEM)

def eh_bloq_g(texto):
    if pd.isna(texto): return False
    t = str(texto).upper()
    return any(c in t for c in BLOQUEIO_G)

def parse_senha(valor):
    if pd.isna(valor): return pd.NaT
    s = str(valor).strip()
    s2 = re.sub(r'\s+[A-Z]{2,4}\s+(\d{4})\s*$', r' \1', s)
    try: return pd.to_datetime(s2, format='%a %b %d %H:%M:%S %Y')
    except: pass
    try: return pd.to_datetime(s, dayfirst=True)
    except: return pd.NaT

def fmt_hms(minutos):
    if not minutos or minutos <= 0: return "—"
    h = int(minutos // 60)
    m = int(minutos % 60)
    s = int((minutos * 60) % 60)
    return f"{h}:{m:02d}:{s:02d}"

def fmt_dt(ts):
    if pd.isna(ts): return "—"
    return pd.Timestamp(ts).strftime('%d/%m/%Y %H:%M')

def nivel_nedocs(score):
    for lo, hi, nome, cor, bg in ESCALA:
        if lo <= score <= hi:
            return nome, cor, bg
    return "—", "#999", "#f5f5f5"

def calcular_nedocs(A, B, C, D, E, F, G):
    if B == 0 or D == 0: return None
    return 85.8*(A/B) + 600*(C/D) + 13.4*E + 0.93*F + 5.64*G - 20

def detectar_data_nome(nome_arquivo):
    m = re.search(r'(?<!\d)(\d{2})[_](\d{2})[_](\d{2,4})(?!\d)', nome_arquivo)
    if m:
        d, mo, a = m.group(1), m.group(2), m.group(3)
        if len(a) == 2: a = '20' + a
        try: return datetime(int(a), int(mo), int(d))
        except: pass
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', nome_arquivo)
    if m:
        a, mo, d = m.group(1), m.group(2), m.group(3)
        try: return datetime(int(a), int(mo), int(d))
        except: pass
    return None

# ─────────────────────────────────────────────────────────────
# PROCESSAMENTO DAS PLANILHAS
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def processar_passagens(conteudo_bytes):
    import io
    df = pd.read_excel(io.BytesIO(conteudo_bytes), engine='openpyxl')
    df['DT_HR_ENTRADA'] = pd.to_datetime(df['DT_HR_ENTRADA'], dayfirst=True, errors='coerce')
    df['DT_HR_SAIDA']   = pd.to_datetime(df['DT_HR_SAIDA'],   dayfirst=True, errors='coerce')
    df['DT_INTERNACAO'] = pd.to_datetime(df['DT_INTERNACAO'],  dayfirst=True, errors='coerce')
    df['REGHC']         = df['REGHC'].astype(str).str.strip().str.upper()
    df = df[~df['TIPO'].astype(str).str.contains('AVISO', na=False, case=False)]
    df = df[~df['LEITO'].astype(str).str.contains('HD|TECIDO|ORGAO', na=False, case=False)]
    df = df.sort_values(['REGHC','ATENDIMENTO','DT_HR_ENTRADA'])
    df['UNID_ANTERIOR'] = df.groupby(['REGHC','ATENDIMENTO'])['UNID_INTERNACAO'].shift(1)
    return df

@st.cache_data(show_spinner=False)
def processar_ps(conteudo_bytes):
    import io
    df = pd.read_csv(io.BytesIO(conteudo_bytes), sep=';', encoding='latin1')
    df['SENHA_DT'] = df['DH_SENHA_INI'].apply(parse_senha)
    df['REGHC']    = df['nr_rghc'].astype(str).str.strip().str.upper()
    return df

def calcular_fg(df_pass, df_ps, data_ref):
    # Merge de senha: mais recente <= DT_INTERNACAO
    df_ps_s   = df_ps[['REGHC','SENHA_DT']].dropna(subset=['SENHA_DT']).sort_values('SENHA_DT')
    df_pass_s = df_pass.sort_values('DT_INTERNACAO')
    df_ps_s['REGHC']   = df_ps_s['REGHC'].astype(str)
    df_pass_s['REGHC'] = df_pass_s['REGHC'].astype(str)

    df = pd.merge_asof(
        df_pass_s, df_ps_s,
        by='REGHC',
        left_on='DT_INTERNACAO',
        right_on='SENHA_DT',
        direction='backward'
    )

    dia_ant = data_ref - timedelta(days=1)
    janelas = {
        '10h': (
            pd.Timestamp(dia_ant.replace(hour=16, minute=0, second=0)),
            pd.Timestamp(data_ref.replace(hour=9, minute=59, second=59)),
        ),
        '16h': (
            pd.Timestamp(data_ref.replace(hour=10, minute=0, second=0)),
            pd.Timestamp(data_ref.replace(hour=15, minute=59, second=59)),
        ),
    }

    resultados = {}
    for coleta, (ini, fim) in janelas.items():
        base = df[
            (df['DT_HR_ENTRADA'] >= ini) &
            (df['DT_HR_ENTRADA'] <= fim) &
            df['UNID_ANTERIOR'].apply(eh_ps)
        ].copy()

        # G
        g_res = None
        cand_g = base[~base['UNID_INTERNACAO'].apply(eh_bloq_g)]
        if not cand_g.empty:
            g = cand_g.sort_values('DT_HR_ENTRADA').iloc[-1]
            g_res = {
                'paciente':   g.get('PACIENTE','—'),
                'reghc':      g.get('REGHC','—'),
                'chegada':    g['DT_HR_ENTRADA'],
                'unid_dest':  g.get('UNID_INTERNACAO','—'),
                'unid_orig':  g.get('UNID_ANTERIOR','—'),
            }

        # F
        f_res = None
        base_f = base[base['SENHA_DT'].notna()].copy()
        base_f['DIFF'] = (base_f['DT_HR_ENTRADA'] - base_f['SENHA_DT']).dt.total_seconds() / 60
        base_f = base_f[(base_f['DIFF'] > 0) & (base_f['DIFF'] <= 45*24*60)]
        if not base_f.empty:
            f = base_f.loc[base_f['DIFF'].idxmax()]
            f_res = {
                'paciente':    f.get('PACIENTE','—'),
                'reghc':       f.get('REGHC','—'),
                'diff_min':    f['DIFF'],
                'diff_h':      f['DIFF'] / 60,
                'senha':       f['SENHA_DT'],
                'chegada':     f['DT_HR_ENTRADA'],
                'unid_dest':   f.get('UNID_INTERNACAO','—'),
                'dt_intern':   f.get('DT_INTERNACAO', pd.NaT),
            }

        resultados[coleta] = {'F': f_res, 'G': g_res}

    return resultados

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────

# ── HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="header-ichc">
  <div class="header-inner">
    <img src="app/static/logo_ichc.jpg" height="56" alt="ICHC FMUSP" />
    <div class="header-title">
      <h1>NEDOCS</h1>
      <p>Calculadora de Superlotação · Lean nas Emergências</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="formula-box">85.8(A/B) + 600(C/D) + 13.4(E) + 0.93(F) + 5.64(G) − 20</div>',
            unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ETAPA 1 — UPLOAD E DATA
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-header">
  <div class="sec-num">1</div>
  <p class="sec-title">Carregar Planilhas</p>
</div>
""", unsafe_allow_html=True)

col_up1, col_up2 = st.columns(2)
with col_up1:
    arq_passagens = st.file_uploader(
        "📋 Passagens (.xlsx)",
        type=['xlsx'],
        help="Planilha de passagens exportada do sistema"
    )
with col_up2:
    arq_ps = st.file_uploader(
        "🏥 Pronto Socorro (.csv)",
        type=['csv'],
        help="Arquivo CSV do Pronto Socorro"
    )

# Data de referência com autodetecção
data_sugerida = datetime.now() - timedelta(days=1)
if arq_passagens:
    det = detectar_data_nome(arq_passagens.name)
    if det:
        data_sugerida = det

col_data, col_btn = st.columns([2, 3])
with col_data:
    data_ref = st.date_input(
        "📅 Data de referência",
        value=data_sugerida.date(),
        help="Normalmente ontem — o dia dos arquivos carregados"
    )

# ─────────────────────────────────────────────────────────────
# PROCESSAMENTO
# ─────────────────────────────────────────────────────────────
fg_resultados = None

if arq_passagens and arq_ps:
    with st.spinner("Processando planilhas…"):
        try:
            df_pass = processar_passagens(arq_passagens.getvalue())
            df_ps_  = processar_ps(arq_ps.getvalue())
            data_dt = datetime.combine(data_ref, datetime.min.time())
            fg_resultados = calcular_fg(df_pass, df_ps_, data_dt)
            st.success(f"✅ Planilhas carregadas com sucesso! Referência: {data_ref.strftime('%d/%m/%Y')}")
        except Exception as e:
            st.error(f"Erro ao processar os arquivos: {e}")

st.markdown('<hr>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ETAPA 2 — F e G CALCULADOS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-header">
  <div class="sec-num">2</div>
  <p class="sec-title">Variáveis F e G — calculadas automaticamente <span class="badge-auto">AUTO</span></p>
</div>
""", unsafe_allow_html=True)

if fg_resultados is None:
    st.info("⬆️ Carregue as duas planilhas acima para calcular F e G automaticamente.")
    fg_resultados = {'10h': {'F': None, 'G': None}, '16h': {'F': None, 'G': None}}

tab_10, tab_16 = st.tabs(["🕙 Coleta 10h", "🕓 Coleta 16h"])

def renderizar_fg(coleta):
    r = fg_resultados[coleta]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="fg-box">
          <div class="fg-letter" style="color:#CE5E2A">F</div>
          <div class="fg-desc">Maior tempo senha → leito</div>
          <div class="fg-pac">{r['F']['paciente'] if r['F'] else '—'}</div>
          <div class="fg-val" style="color:#CE5E2A">{fmt_hms(r['F']['diff_min']) if r['F'] else '—'}</div>
          <div class="fg-det">
            {'Senha: ' + fmt_dt(r['F']['senha']) + '<br>Chegada leito: ' + fmt_dt(r['F']['chegada']) + '<br>Destino: ' + str(r['F']['unid_dest']) if r['F'] else 'Sem resultado para este período'}
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="fg-box">
          <div class="fg-letter" style="color:#009CA6">G</div>
          <div class="fg-desc">Último a sair do PS</div>
          <div class="fg-pac">{r['G']['paciente'] if r['G'] else '—'}</div>
          <div class="fg-val" style="color:#009CA6">{fmt_dt(r['G']['chegada']) if r['G'] else '—'}</div>
          <div class="fg-det">
            {'Origem: ' + str(r['G']['unid_orig']) + '<br>Destino: ' + str(r['G']['unid_dest']) if r['G'] else 'Sem resultado para este período'}
          </div>
        </div>
        """, unsafe_allow_html=True)

with tab_10: renderizar_fg('10h')
with tab_16: renderizar_fg('16h')

st.markdown('<hr>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ETAPA 3 — VARIÁVEIS MANUAIS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-header">
  <div class="sec-num">3</div>
  <p class="sec-title">Variáveis Manuais <span class="badge-manual">COLETA PRESENCIAL</span></p>
</div>
""", unsafe_allow_html=True)

st.markdown("Preencha com os dados coletados presencialmente no momento da medição (10h e 16h).")

# B e D são fixos
col_b, col_d = st.columns(2)
with col_b:
    st.markdown("""<div class="var-card">
      <div class="var-card-letter">B</div>
      <div class="var-card-title">Pontos de Cuidado no PS</div>
      <div class="var-card-desc">Total de espaços dedicados ao cuidado (consultórios, macas, poltronas). Número fixo — capacidade instalada. Não incluir macas de corredor.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    B = st.number_input("B — Pontos de Cuidado", min_value=0, value=0,
                        key="B", label_visibility="collapsed")

with col_d:
    st.markdown("""<div class="var-card">
      <div class="var-card-letter">D</div>
      <div class="var-card-title">Leitos Efetivos de Internação disponíveis ao PS</div>
      <div class="var-card-desc">Leitos operacionais do hospital disponíveis ao PS. Descontar leitos ocupados há mais de 90 dias, em manutenção ou bloqueados.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    D = st.number_input("D — Leitos Operacionais", min_value=0, value=0,
                        key="D", label_visibility="collapsed")

st.markdown("---")

# A, C, E por coleta
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.markdown("#### 🕙 Coleta 10h")
    st.markdown("""<div class="var-card">
      <div class="var-card-letter">A</div>
      <div class="var-card-title">Pacientes no PS</div>
      <div class="var-card-desc">Total de pacientes em espera ou atendimento nas salas, corredores e consultórios. Não incluir acompanhantes.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    A_10 = st.number_input("A às 10h", min_value=0, value=0, key="A10", label_visibility="collapsed")

    st.markdown("""<div class="var-card">
      <div class="var-card-letter">C</div>
      <div class="var-card-title">Pacientes aguardando internação</div>
      <div class="var-card-desc">Pacientes com decisão de internação aguardando leito. Deve ser menor que A.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    C_10 = st.number_input("C às 10h", min_value=0, value=0, key="C10", label_visibility="collapsed")

    st.markdown("""<div class="var-card">
      <div class="var-card-letter">E</div>
      <div class="var-card-title">Pacientes no Respirador</div>
      <div class="var-card-desc">Total de pacientes intubados no PS. Deve ser ≤ C.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    E_10 = st.number_input("E às 10h", min_value=0, value=0, key="E10", label_visibility="collapsed")

with col_h2:
    st.markdown("#### 🕓 Coleta 16h")
    st.markdown("""<div class="var-card">
      <div class="var-card-letter">A</div>
      <div class="var-card-title">Pacientes no PS</div>
      <div class="var-card-desc">Total de pacientes em espera ou atendimento nas salas, corredores e consultórios. Não incluir acompanhantes.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    A_16 = st.number_input("A às 16h", min_value=0, value=0, key="A16", label_visibility="collapsed")

    st.markdown("""<div class="var-card">
      <div class="var-card-letter">C</div>
      <div class="var-card-title">Pacientes aguardando internação</div>
      <div class="var-card-desc">Pacientes com decisão de internação aguardando leito. Deve ser menor que A.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    C_16 = st.number_input("C às 16h", min_value=0, value=0, key="C16", label_visibility="collapsed")

    st.markdown("""<div class="var-card">
      <div class="var-card-letter">E</div>
      <div class="var-card-title">Pacientes no Respirador</div>
      <div class="var-card-desc">Total de pacientes intubados no PS. Deve ser ≤ C.</div>
      <div class="clearfix"></div></div>""", unsafe_allow_html=True)
    E_16 = st.number_input("E às 16h", min_value=0, value=0, key="E16", label_visibility="collapsed")

st.markdown('<hr>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ETAPA 4 — RESULTADO
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-header">
  <div class="sec-num">4</div>
  <p class="sec-title">Resultado NEDOCS</p>
</div>
""", unsafe_allow_html=True)

btn_calc = st.button("🧮  Calcular NEDOCS", type="primary", use_container_width=True)

if btn_calc:
    if B == 0 or D == 0:
        st.warning("⚠️ Preencha os campos B (Pontos de Cuidado) e D (Leitos Operacionais) antes de calcular.")
    else:
        col_r1, col_r2 = st.columns(2)

        for col_res, coleta, A, C, E, sufixo in [
            (col_r1, '10h', A_10, C_10, E_10, "10:00"),
            (col_r2, '16h', A_16, C_16, E_16, "16:00"),
        ]:
            fg = fg_resultados[coleta]
            F_h = fg['F']['diff_h'] if fg['F'] else 0
            G_h = 0  # G em horas não é diretamente disponível sem dado extra
            score = calcular_nedocs(A, B, C, D, E, F_h, G_h)

            if score is None:
                with col_res:
                    st.error("Erro no cálculo — verifique B e D.")
                continue

            nome, cor, bg = nivel_nedocs(score)
            f_pac  = fg['F']['paciente'] if fg['F'] else '—'
            f_tmp  = fmt_hms(fg['F']['diff_min']) if fg['F'] else '—'
            g_pac  = fg['G']['paciente'] if fg['G'] else '—'
            g_chg  = fmt_dt(fg['G']['chegada']) if fg['G'] else '—'

            with col_res:
                st.markdown(f"""
                <div class="resultado-box" style="background:{bg}; border:2px solid {cor}40">
                  <div class="res-hora" style="color:{cor}">{sufixo}</div>
                  <div class="res-score" style="color:{cor}">{score:.0f}</div>
                  <div class="res-nivel" style="background:{cor}20;color:{cor}">{nome}</div>
                  <div class="res-vars">
                    A={A} &nbsp; B={B} &nbsp; C={C} &nbsp; D={D} &nbsp; E={E}<br>
                    F={f_tmp} → {f_pac}<br>
                    G={g_chg} → {g_pac}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Escala de referência
        st.markdown("#### Escala NEDOCS")
        cols_esc = st.columns(6)
        for i, (lo, hi, nome, cor, bg) in enumerate(ESCALA):
            with cols_esc[i]:
                faixa = f"{lo}–{hi}" if hi < 9999 else f"> {lo}"
                st.markdown(f"""
                <div class="escala-item" style="background:{bg};border-left:4px solid {cor}">
                  <div>
                    <div class="escala-range" style="color:{cor}">{faixa}</div>
                    <div class="escala-nome">{nome}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#888; font-size:12px; padding:8px 0 20px">
  NEDOCS · Instituto Central do Hospital das Clínicas · FMUSP ·
  Lean nas Emergências · 85.8(A/B) + 600(C/D) + 13.4(E) + 0.93(F) + 5.64(G) − 20
</div>
""", unsafe_allow_html=True)
