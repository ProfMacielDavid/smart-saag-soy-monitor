
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from typing import Tuple, List

st.markdown("# Séries Temporais (NDVI)")
st.caption("Visualize evolução por talhão / BBOX")

inputs = st.session_state.get("saag_inputs")

with st.expander("Parâmetros de entrada", expanded=True):
    if not inputs:
        st.warning("Nenhum parâmetro encontrado. Volte para **Home** e execute com a área e período selecionados.")
    else:
        col1, col2, col3 = st.columns([1,1,2])
        col1.metric("Resolução (m)", inputs.get("resolution_m", "-"))
        col2.metric("Início", inputs.get("start_date", "-"))
        col3.metric("Final", inputs.get("end_date", "-"))
        st.code(f"BBOX (EPSG:4326): {inputs.get('bbox_wgs84', '-')}", language="text")

if not inputs:
    st.stop()

def _parse_bbox(bbox_str: str) -> Tuple[float, float, float, float]:
    parts = [p.strip() for p in str(bbox_str).split(",")]
    if len(parts) != 4:
        raise ValueError("BBOX inválido")
    return tuple(float(x) for x in parts)

def _install_hint():
    st.info(
        "Para cálculo real do NDVI, instale as dependências:\n\n"
        "```bash\n"
        "conda install -y -c conda-forge rasterio rioxarray xarray dask odc-stac\n"
        "pip install planetary-computer pystac-client\n"
        "```\n"
        "Se aparecer aviso do PROJ/GDAL, execute `setx PROJ_NETWORK ON` e reabra o terminal."
    )

# ---------- Consulta Planetary Computer ----------
try:
    import numpy as np
    import planetary_computer as pc
    from pystac_client import Client
    from odc.stac import stac_load
except Exception:
    st.error("Dependências para leitura do Sentinel-2 não encontradas.")
    _install_hint()
    st.stop()

try:
    minx, miny, maxx, maxy = _parse_bbox(inputs["bbox_wgs84"])
    start = pd.to_datetime(inputs["start_date"]).strftime("%Y-%m-%d")
    end   = pd.to_datetime(inputs["end_date"]).strftime("%Y-%m-%d")
    res_m = int(inputs.get("resolution_m", 10))
except Exception as e:
    st.error(f"Parâmetros inválidos: {e}")
    st.stop()

with st.status("Consultando Sentinel-2 no Planetary Computer...", expanded=False) as s:
    try:
        catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=[minx, miny, maxx, maxy],
            datetime=f"{start}/{end}",
            query={"eo:cloud_cover": {"lt": 60}},
            max_items=100,
        )
        items = list(search.items())  # em vez de get_items()
        if len(items) == 0:
            s.update(label="Sem cenas no período/BBOX.", state="error")
            st.warning("Nenhuma cena Sentinel-2 L2A encontrada no período e área selecionados.")
            st.stop()

        # Assinar URLs para acesso
        items = [pc.sign(item) for item in items]

        # Detecta chaves de assets para RED/NIR
        asset_keys = set(items[0].assets.keys())
        candidates = [("B04","B08"), ("B04_10m","B08_10m"), ("red","nir")]
        chosen = None
        for a1, a2 in candidates:
            if a1 in asset_keys and a2 in asset_keys:
                chosen = (a1, a2)
                break
        if chosen is None:
            raise RuntimeError(f"Não encontrei bandas RED/NIR nos assets: {sorted(asset_keys)}")

        # Carrega em projeção nativa (UTM), resolução em metros
        ds = stac_load(
            items,
            assets=list(chosen),
            bbox=(minx, miny, maxx, maxy),
            crs=None,                # nativo
            resolution=res_m,        # metros
            chunks={"time": 1, "x": 1024, "y": 1024},
        )

        red = ds[chosen[0]].astype("float32")
        nir = ds[chosen[1]].astype("float32")
        # Escala para 0..1 se vier 0..10000
        try:
            mx = max(float(red.max().compute()), float(nir.max().compute()))
        except Exception:
            mx = 1.0
        if mx > 1.5:
            red = red / 10000.0
            nir = nir / 10000.0

        ndvi = (nir - red) / (nir + red + 1e-6)
        ndvi_t = ndvi.median(dim=("y","x")).compute()  # mediana espacial por data
        df = ndvi_t.to_series().reset_index()
        df.columns = ["date", "NDVI"]
        df = df.sort_values("date")

        if df.empty:
            s.update(label="Sem dados NDVI após processamento.", state="error")
            st.warning("Nenhum dado NDVI disponível após aplicar filtros.")
            st.stop()

        s.update(label="Cenas carregadas e NDVI calculado.", state="complete")
    except Exception as e:
        s.update(label="Erro ao consultar/calcular NDVI.", state="error")
        st.error("Falha ao consultar/calcular NDVI. Detalhes do erro:")
        st.code(str(e))
        _install_hint()
        st.stop()

# ---------- Gráfico e download ----------
chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("date:T", title="date"),
    y=alt.Y("NDVI:Q", scale=alt.Scale(domain=[0,1])),
    tooltip=[alt.Tooltip("date:T", title="Data"), alt.Tooltip("NDVI:Q", format=".3f")]
).properties(width="container", height=420)
st.altair_chart(chart, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Baixar CSV", csv, "serie_temporal_ndvi.csv", "text/csv")
