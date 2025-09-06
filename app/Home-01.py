
import streamlit as st
from PIL import Image
from pathlib import Path

st.set_page_config(
    page_title="SMART SAAG • Monitoramento de Soja",
    page_icon="🌱",
    layout="wide",
)

# CSS
css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Header com logo e texto (corrigido: controla tamanho e evita estourar layout)
col1, col2 = st.columns([1, 3])
with col1:
    logo_path = Path(__file__).parent.parent / "assets" / "logo.jpg"
    if logo_path.exists():
        # Define largura fixa da logo para manter proporção e evitar ocupar a coluna inteira
        st.image(str(logo_path), width=180)
with col2:
    st.markdown("### SMART SAAG")
    st.markdown("#### Monitoramento de Soja – Protótipo (Centelha II)")
    st.markdown('<p class="saag-muted">Ingestão Sentinel-2 • NDVI/EVI/NDRE • Séries por talhão • Exportações</p>', unsafe_allow_html=True)

st.markdown("---")

# Painel principal
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
