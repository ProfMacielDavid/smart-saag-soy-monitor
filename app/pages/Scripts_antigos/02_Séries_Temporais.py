
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Tuple

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

# -------- utils --------
def _parse_bbox(bbox_str: str) -> Tuple[float, float, float, float]:
    parts = [p.strip() for p in str(bbox_str).split(",")]
    if len(parts) != 4:
        raise ValueError("BBOX inválido")
    return tuple(float(x) for x in parts)  # minx, miny, maxx, maxy

def _install_hint():
    st.info(
        "Para cálculo real do NDVI, instale as dependências:\n\n"
        "```bash\n"
        "conda install -y -c conda-forge rasterio rioxarray xarray dask odc-stac\n"
        "pip install planetary-computer pystac-client\n"
        "```\n"
        "Se aparecer aviso do PROJ/GDAL, execute `setx PROJ_NETWORK ON` e reabra o terminal."
    )

# -------- main --------
try:
    import numpy as np
    import planetary_computer as pc
    from pystac_client import Client
    from odc.stac import stac_load
    import dask
    dask.config.set({"array.slicing.split_large_chunks": True})
except Exception as e:
    st.error("Dependências para leitura do Sentinel-2 não encontradas.")
    _install_hint()
    st.stop()

# Parse inputs
try:
    minx, miny, maxx, maxy = _parse_bbox(inputs["bbox_wgs84"])
except Exception as e:
    st.error(f"BBOX inválido: {e}")
    st.stop()

try:
    start = pd.to_datetime(inputs["start_date"]).strftime("%Y-%m-%d")
    end = pd.to_datetime(inputs["end_date"]).strftime("%Y-%m-%d")
except Exception:
    st.error("Datas inválidas.")
    st.stop()

res_m = int(inputs.get("resolution_m", 10))

# A resolução em graus (aproximação) para EPSG:4326
res_deg = max(res_m / 111320.0, 0.00005)  # piso ~5e-5 deg ~ 5 m

with st.status("Consultando Sentinel-2 no Planetary Computer...", expanded=False) as s:
    try:
        catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=[minx, miny, maxx, maxy],
            datetime=f"{start}/{end}",
            query={"eo:cloud_cover": {"lt": 60}},
            max_items=60,
        )
        items = list(search.get_items())
        if len(items) == 0:
            s.update(label="Sem cenas no período/BBOX.", state="error")
            st.warning("Nenhuma cena Sentinel-2 L2A encontrada no período e área selecionados.")
            st.stop()

        # Assina URLs para acesso
        items = [pc.sign(item) for item in items]

        # Tenta carregar por 'B04'/'B08' e, se falhar, por 'red'/'nir'
        bands_try = [["B04","B08"], ["red","nir"]]
        ds = None
        last_err = None
        for bands in bands_try:
            try:
                ds = stac_load(
                    items,
                    bands=bands,
                    bbox=(minx, miny, maxx, maxy),
                    crs="EPSG:4326",
                    resolution=(-res_deg, res_deg),
                    chunks={"time": 1, "x": 1024, "y": 1024},
                )
                ds = ds.rename({bands[0]:"red", bands[1]:"nir"})
                break
            except Exception as e:
                last_err = e
                ds = None
        if ds is None:
            raise last_err or RuntimeError("Falha ao carregar bandas.")

        # Converte para float reflectância 0-1 (S2 L2A normalmente 0..10000)
        red = ds["red"].astype("float32")
        nir = ds["nir"].astype("float32")
        if red.max().compute() > 1.5:  # heurística
            red = red / 10000.0
            nir = nir / 10000.0

        ndvi = (nir - red) / (nir + red + 1e-6)
        # Mediana espacial por data
        ndvi_series = ndvi.median(dim=("y","x")).to_series()
        ndvi_series.index = pd.to_datetime(ndvi_series.index)

        df = ndvi_series.reset_index()
        df.columns = ["date", "NDVI"]
        df = df.sort_values("date")

        if df.empty:
            s.update(label="Sem dados NDVI após processamento.", state="error")
            st.warning("Nenhum dado NDVI disponível após aplicar filtros.")
            st.stop()

        s.update(label="Cenas carregadas e NDVI calculado.", state="complete")
    except Exception as e:
        s.update(label="Erro ao consultar/calcular NDVI.", state="error")
        st.exception(e)
        _install_hint()
        st.stop()

# Gráfico
import altair as alt
chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("date:T", title="date"),
    y=alt.Y("NDVI:Q", scale=alt.Scale(domain=[0,1])),
    tooltip=[alt.Tooltip("date:T", title="Data"), alt.Tooltip("NDVI:Q", format=".3f")]
).properties(width="container", height=420)
st.altair_chart(chart, use_container_width=True)

# Download CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Baixar CSV", csv, "serie_temporal_ndvi.csv", "text/csv")
