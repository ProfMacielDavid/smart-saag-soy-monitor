import streamlit as st

st.title("Áreas e Períodos")
st.caption("Defina talhões, BBOX e janelas temporais")

with st.form("area"):
    bbox = st.text_input("BBOX (EPSG:4326)", "-63.95,-8.85,-63.80,-8.75")
    uploaded = st.file_uploader("GeoJSON/GPKG de talhões (opcional)")
    submitted = st.form_submit_button("Salvar parâmetros")
if submitted:
    st.session_state["bbox"] = bbox
    st.success("Parâmetros salvos.")
