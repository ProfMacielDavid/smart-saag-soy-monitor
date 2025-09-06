
import streamlit as st
from PIL import Image
from pathlib import Path
import base64

st.set_page_config(
    page_title="SMART SAAG • Monitoramento de Soja",
    page_icon="🌱",
    layout="wide",
)

# CSS (mantido do original)
css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# HEADER (apenas modificação da LOGO: maior e mais baixa)
# Mantemos os títulos e o divisor exatamente como no original,
# mas trocamos o bloco de colunas por um cabeçalho flex para
# não limitar o tamanho da logo.
# ---------------------------------------------------------------

def _find_logo_path() -> Path | None:
    base = Path(__file__).parent.parent
    candidates = [
        base / "assets" / "logo.jpg",
        base / "assets" / "LOGO.jpg",
        base / "logo.jpg",
        base / "LOGO.jpg",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def _to_data_uri(p: Path) -> str:
    mime = "image/jpeg" if p.suffix.lower() in {".jpg", ".jpeg", ".jpe"} else "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

_logo_path = _find_logo_path()
_logo_src = _to_data_uri(_logo_path) if _logo_path else ""

st.markdown(
    f'''
    <style>
      /* desce um pouco o topo para a logo não encostar/cortar */
      [data-testid="block-container"] {{
          padding-top: 40px !important;
      }}
      .saag-header-flex {{
          display: flex;
          align-items: center;
          gap: 28px;
          margin: 6px 0 4px 0;
      }}
      .saag-header-flex .saag-logo {{
          width: 320px;   /* tamanho da logo conforme a 1ª imagem */
          height: auto;
          border-radius: 12px;
      }}
      .saag-muted {{
          opacity: 0.8;
      }}
    </style>
    <div class="saag-header-flex">
      <img class="saag-logo" src="{_logo_src}" alt="SMART SAAG Logo" />
      <div class="saag-titles">
        <h3 style="margin:0;">SMART SAAG</h3>
        <h4 style="margin:0 0 6px 0;">Monitoramento de Soja – Protótipo (Centelha II)</h4>
        <p class="saag-muted" style="margin:0;">Ingestão Sentinel-2 • NDVI/EVI/NDRE • Séries por talhão • Exportações</p>
      </div>
    </div>
    ''',
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------------------
# Painel principal (original)
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
