import streamlit as st

# Pagina de Ajuda - Guia rapido (somente textos; sem set_page_config para evitar conflito com Home)

st.markdown("# Ajuda - Guia rapido")

# Estilo simples para caixa de destaque
st.markdown(
    """
    <style>
    .help-box {
        padding: 12px 16px;
        border-radius: 10px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        margin: 8px 0 18px 0;
    }
    .muted { opacity: .85; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="help-box muted">
      Este guia explica a sequencia completa de operacao do app. Leia os passos e execute na ordem.
    </div>
    """,
    unsafe_allow_html=True
)

st.header("Fluxo recomendado")

with st.expander("1) Home - parametros iniciais", expanded=True):
    st.markdown(
        """
1. Resolucao (m): escolha 10, 20, 30 ou 60 m. Quanto menor, maior o detalhe.
2. Datas: selecione Data inicial e Data final do periodo de interesse.
3. BBOX (EPSG:4326): informe minx,miny,maxx,maxy (graus decimais, com ponto).
4. Executar exemplo NDVI: clique para validar o pipeline e conferir retorno rapido.
        """
    )
    st.caption("Dica: use a faixa 'Como comecar - instrucoes rapidas' na Home para exemplos.")

with st.expander("2) Areas e Periodos - talhao e metadados", expanded=True):
    st.markdown(
        """
1. Cliente / Campo / Cultura / Ano: preencha todos os campos obrigatorios.
2. Area do talhao: desenhe ou importe a geometria (ou informe BBOX) e salve.
3. Periodo: confirme ou ajuste as datas.
4. Validar area no mapa: confira se a geometria coincide com o alvo.
        """
    )
    st.caption("Resultado: area definida e metadados prontos para consultas de imagens.")

with st.expander("3) Series Temporais - NDVI / EVI / NDRE", expanded=True):
    st.markdown(
        """
1. Indice: selecione NDVI, EVI, NDRE, etc.
2. Filtros (ex.: nuvens): ajuste o limite conforme a necessidade.
3. Gerar serie: execute para obter grafico e tabela.
4. Download: exporte a serie em CSV (e, quando disponivel, imagens de apoio).
        """
    )
    st.caption("Resultado: curvas temporais por talhao/area, com estatisticas por data.")

with st.expander("4) Exportacoes - rasters e relatorios", expanded=True):
    st.markdown(
        """
1. Produto de saida: escolha (ex.: mosaico NDVI, recorte por talhao, composicoes).
2. Formato: GeoTIFF para GIS; PNG/JPEG para visualizacao rapida.
3. Gerar: execute e aguarde o processamento.
4. Baixar: salve o arquivo; o nome inclui cliente, campo, cultura, ano.
        """
    )
    st.caption("Resultado: arquivos prontos para QGIS/ArcGIS ou relatorios.")

st.header("Erros comuns e solucoes")
st.markdown(
    """
- Sem saida ou mapa vazio: verifique BBOX (ordem minx,miny,maxx,maxy) e CRS EPSG:4326.
- Sem imagens no periodo: ajuste as datas; sensores podem nao ter passagem no intervalo.
- Nuvens altas: reduza o limite de nuvens ou mude a janela de datas.
- Exportacao com NoData: valide o NoData e CRS no seu GIS (defina simbologia adequada).
    """
)

st.header("FAQ rapido")
st.markdown(
    """
**Qual resolucao escolher?** 10-20 m para talhoes pequenos; 30-60 m para visao geral.
**Como digitar o BBOX?** Ex.: -63.95,-8.85,-63.80,-8.75 (use ponto).
**Qual formato para analise GIS?** GeoTIFF.
**Como compartilhar resultados?** Exporte CSV/PNG e anexe em relatorios.
    """
)

st.caption("Se algo nao gerar saida, retorne ao passo anterior e revise entradas obrigatorias.")
