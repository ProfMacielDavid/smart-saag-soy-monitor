import streamlit as st
from logo_header import inject_logo

# Teste da logo fixa no topo-esquerda
inject_logo(r"E:\Projeto_Smart_SAAG_2025_GitHub\smart-saag-soy-monitor\LOGO.jpg", height_px=64, pad_top_px=96)

st.title("Teste de Logo")
st.write("A logo deve estar fixa no topo-esquerda desta página.")
