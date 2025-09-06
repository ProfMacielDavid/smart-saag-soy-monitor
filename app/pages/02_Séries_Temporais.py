
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from typing import Tuple
import numpy as np

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
        items = list(search.items())
        if len(items) == 0:
            s.update(label="Sem cenas no período/BBOX.", state="error")
            st.warning("Nenhuma cena Sentinel-2 L2A encontrada no período e área selecionados.")
            st.stop()

        # Assinar URLs e detectar bandas
        items = [pc.sign(item) for item in items]
        asset_keys = set(items[0].assets.keys())
        candidates = [("B04","B08"), ("B04_10m","B08_10m"), ("red","nir")]
        chosen = None
        for a1, a2 in candidates:
            if a1 in asset_keys and a2 in asset_keys:
                chosen = (a1, a2)
                break
        if chosen is None:
            raise RuntimeError(f"Não encontrei bandas RED/NIR nos assets: {sorted(asset_keys)}")

        # Carrega em UTM nativo, resolução em metros
        ds = stac_load(
            items,
            assets=list(chosen),
            bbox=(minx, miny, maxx, maxy),
            crs=None,
            resolution=res_m,
            chunks={"time": 1, "x": 1024, "y": 1024},
        )

        red = ds[chosen[0]].astype("float32")
        nir = ds[chosen[1]].astype("float32")
        # Escala 0..1, se necessário
        try:
            mx = max(float(red.max().compute()), float(nir.max().compute()))
        except Exception:
            mx = 1.0
        if mx > 1.5:
            red = red / 10000.0
            nir = nir / 10000.0

        ndvi = (nir - red) / (nir + red + 1e-6)
        ndvi_t = ndvi.median(dim=("y","x")).compute()
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

# ---------- Gráfico (série temporal) ----------
chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("date:T", title="date"),
    y=alt.Y("NDVI:Q", scale=alt.Scale(domain=[0,1])),
    tooltip=[alt.Tooltip("date:T", title="Data"), alt.Tooltip("NDVI:Q", format=".3f")]
).properties(width="container", height=420)

with st.expander("Cenas carregadas e NDVI calculado.", expanded=True):
    st.altair_chart(chart, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV", csv, "serie_temporal_ndvi.csv", "text/csv")

# ---------- Box de imagens NDVI (pré-visualizações) ----------
st.markdown("### Mapas NDVI da área (pré-visualizações)")

# Controles do box
cmin, cmax, nshots = st.columns([1,1,1])
with cmin:
    vmin = st.number_input("NDVI mínimo (legenda)", 0.0, 1.0, 0.3, 0.05)
with cmax:
    vmax = st.number_input("NDVI máximo (legenda)", 0.0, 1.0, 0.9, 0.05)
with nshots:
    n_imgs = st.slider("Qtde de imagens", 1, 6, 4)

# Seleção de datas distribuídas
time_len = ndvi.time.size
idxs = np.linspace(0, time_len - 1, n_imgs, dtype=int) if time_len > 0 else np.array([], dtype=int)
sel_times = [ndvi.time.values[i] for i in idxs]

from io import BytesIO
import matplotlib.pyplot as plt

def ndvi_slice_png(arr, vmin=0.3, vmax=0.9):
    """Gera PNG do NDVI com legenda (colormap RdYlGn)."""
    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=160)
    im = ax.imshow(arr, vmin=vmin, vmax=vmax, cmap="RdYlGn")
    ax.axis("off")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("NDVI", rotation=270, labelpad=8)
    buf = BytesIO()
    fig.tight_layout(pad=0.1)
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    buf.seek(0)
    return buf

if len(sel_times) == 0:
    st.info("Nenhuma cena disponível para gerar os mapas NDVI.")
else:
    per_row = 4
    rows = (len(sel_times) + per_row - 1) // per_row
    for r in range(rows):
        cols = st.columns(min(per_row, len(sel_times) - r*per_row))
        for j, col in enumerate(cols, start=0):
            t = sel_times[r*per_row + j]
            arr = ndvi.sel(time=t).clip(vmin, vmax).compute().values
            arr = np.where(np.isfinite(arr), arr, vmin)
            png = ndvi_slice_png(arr, vmin=vmin, vmax=vmax)
            with col:
                st.image(png, use_container_width=True, caption=pd.to_datetime(str(t)).strftime("%Y-%m-%d"))
