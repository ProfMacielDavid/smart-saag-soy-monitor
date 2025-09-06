
import streamlit as st
from pathlib import Path
import base64

st.set_page_config(
    page_title="SMART SAAG • Monitoramento de Soja",
    page_icon="🌱",
    layout="wide",
)

# Mantém CSS externo (se existir)
css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ----------------------
# HEADER com logo (flex)
# ----------------------

def _find_logo_path() -> Path | None:
    base = Path(__file__).parent.parent
    for p in [
        base / "assets" / "logo.jpg",
        base / "assets" / "LOGO.jpg",
        base / "logo.jpg",
        base / "LOGO.jpg",
    ]:
        if p.exists():
            return p
    return None

def _to_data_uri(p: Path) -> str:
    if p.suffix.lower() in {".jpg", ".jpeg", ".jpe"}:
        mime = "image/jpeg"
    else:
        mime = "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

_logo_path = _find_logo_path()
_logo_src = _to_data_uri(_logo_path) if _logo_path else ""

# CSS responsivo: mantém o visual atual em desktop e adapta em telas menores
st.markdown(
    f'''
    <style>
      /* Espaço superior p/ não colar no topo */
      [data-testid="block-container"] {{
          padding-top: 40px !important;
      }}

      .saag-header-flex {{
          display: flex;
          align-items: center;
          gap: 28px;
          margin: 6px 0 4px 0;
      }}
      .saag-logo {{
          width: 360px;          /* tamanho base (desktop grande) */
          height: auto;
          border-radius: 12px;
      }}
      .saag-title h3 {{
          margin: 0;
      }}
      .saag-title h4 {{
          margin: 2px 0 6px 0;
          font-weight: 600;
      }}
      .saag-muted {{
          opacity: 0.8;
          margin: 0;
      }}

      /* Ajustes progressivos (tablets e notebooks menores) */
      @media (max-width: 1200px) {{
        .saag-logo {{ width: 320px; }}
      }}
      @media (max-width: 992px) {{
        .saag-logo {{ width: 280px; }}
      }}
      /* Empilha o cabeçalho em telas pequenas (mobile) e reduz títulos */
      @media (max-width: 768px) {{
        [data-testid="block-container"] {{ padding-top: 24px !important; }}
        .saag-header-flex {{
          flex-direction: column;
          align-items: flex-start;
          gap: 12px;
        }}
        .saag-logo {{ width: 240px; }}
        .saag-title h3 {{ font-size: 1.25rem; }}   /* ~20px */
        .saag-title h4 {{ font-size: 1.05rem; }}   /* ~16-17px */
      }}

      /* Força colunas do Streamlit a empilharem quando a tela estiver estreita */
      @media (max-width: 992px) {{
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
          width: 100% !important;
          flex: 1 0 100% !important;
        }}
        div[data-testid="stHorizontalBlock"] {{ gap: 0.5rem !important; }}
      }}
    </style>
    <div class="saag-header-flex">
      <img class="saag-logo" src="{_logo_src}" alt="SMART SAAG Logo" />
      <div class="saag-title">
        <h3>SMART SAAG</h3>
        <h4>Monitoramento de Soja – Protótipo (Centelha II)</h4>
        <p class="saag-muted">Ingestão Sentinel-2 • NDVI/EVI/NDRE • Séries por talhão • Exportações</p>
      </div>
    </div>
    ''',
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------------------
# Painel principal (mantido)
# ---------------------------
with st.container():
    st.markdown('<div class="saag-card">', unsafe_allow_html=True)
    st.markdown("#### Como começar")

    c1, c2, c3 = st.columns(3)
    with c1:
        res = st.number_input("Resolução (m)", min_value=10, max_value=60, value=10, step=10)
    with c2:
        start_date = st.date_input("Data inicial")
    with c3:
        end_date = st.date_input("Data final")

    bbox = st.text_input("BBOX (minx,miny,maxx,maxy – EPSG:4326)", "-63.95,-8.85,-63.80,-8.75")

    if st.button("Executar exemplo NDVI", type="primary"):
        st.info("Rodando *stub* do protótipo… (integração com pipeline Python)")
        st.success("Processo iniciado! Verifique a página **Séries Temporais** para visualizar resultados.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(" ")
st.caption("© Smart SAAG — 2025")
