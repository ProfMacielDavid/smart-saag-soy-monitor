# pages/03_Exportacoes.py
# Exportações: CSV / Parquet (séries NDVI) e GeoPackage (AOI do BBOX).
# Se não houver série em memória, recalcula a partir dos parâmetros salvos (Home).

from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Tuple

st.markdown("# Exportações")
st.caption("Gere GeoPackage / CSV / Parquet para dashboards")

# ---------------------------------------------------------------------
# Utilidades

def _parse_bbox(bbox_str: str) -> Tuple[float, float, float, float]:
    parts = [p.strip() for p in str(bbox_str).split(",")]
    if len(parts) != 4:
        raise ValueError("BBOX inválido (esperado: minx,miny,maxx,maxy).")
    return tuple(float(x) for x in parts)  # type: ignore

def _install_hint():
    st.info(
        "Para cálculo real do NDVI / exportações geoespaciais, garanta as dependências:\n\n"
        "```bash\n"
        "conda install -y -c conda-forge rasterio rioxarray xarray dask odc-stac geopandas pyproj shapely\n"
        "pip install planetary-computer pystac-client\n"
        "```\n"
        "Se aparecer aviso do PROJ/GDAL, execute `setx PROJ_NETWORK ON` e reabra o terminal."
    )

# ---------------------------------------------------------------------
# Entrada (parâmetros salvos na sessão pela Home)

inputs = st.session_state.get("saag_inputs", {})
if not inputs:
    st.warning("Nenhum parâmetro encontrado. Volte à **Home** e execute novamente.")
    st.stop()

col1, col2, col3 = st.columns([1,1,2], vertical_alignment="center")
col1.metric("Resolução (m)", inputs.get("resolution_m", "-"))
col2.metric("Início", inputs.get("start_date", "-"))
col3.metric("Final", inputs.get("end_date", "-"))
st.code(f"BBOX (EPSG:4326): {inputs.get('bbox_wgs84','-')}", language="text")

# Saída
out_dir = Path.cwd() / "outputs"
out_dir.mkdir(parents=True, exist_ok=True)

csv_path = out_dir / "ts_ndvi.csv"
parquet_path = out_dir / "ts_ndvi.parquet"
gpkg_path = out_dir / "aoi.gpkg"

# ---------------------------------------------------------------------
# Obtém/gera a série NDVI (reusa se já existir na sessão)

def get_timeseries_df() -> pd.DataFrame | None:
    # Se outra página já deixou em memória, aproveita:
    df = st.session_state.get("saag_ndvi_df")
    if isinstance(df, pd.DataFrame) and not df.empty:
        return df.copy()

    # Caso contrário, tenta calcular aqui para exportar
    try:
        import planetary_computer as pc
        from pystac_client import Client
        from odc.stac import stac_load
    except Exception:
        st.error("Dependências para leitura do Sentinel-2 não encontradas.")
        _install_hint()
        return None

    try:
        minx, miny, maxx, maxy = _parse_bbox(inputs["bbox_wgs84"])
        start = pd.to_datetime(inputs["start_date"]).strftime("%Y-%m-%d")
        end   = pd.to_datetime(inputs["end_date"]).strftime("%Y-%m-%d")
        res_m = int(inputs.get("resolution_m", 10))
    except Exception as e:
        st.error(f"Parâmetros inválidos: {e}")
        return None

    with st.status("Consultando Sentinel-2 e calculando NDVI para exportação...", expanded=False) as s:
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
                return None

            items = [pc.sign(item) for item in items]
            asset_keys = set(items[0].assets.keys())
            candidates = [("B04", "B08"), ("B04_10m", "B08_10m"), ("red", "nir")]
            chosen = None
            for a1, a2 in candidates:
                if a1 in asset_keys and a2 in asset_keys:
                    chosen = (a1, a2)
                    break
            if chosen is None:
                s.update(label="Bandas RED/NIR não encontradas na coleção.", state="error")
                return None

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

            # Escala para 0..1, se necessário
            try:
                mx = max(float(red.max().compute()), float(nir.max().compute()))
            except Exception:
                mx = 1.0
            if mx > 1.5:
                red = red / 10000.0
                nir = nir / 10000.0

            ndvi = (nir - red) / (nir + red + 1e-6)
            ndvi_t = ndvi.median(dim=("y", "x")).compute()
            df = ndvi_t.to_series().reset_index()
            df.columns = ["date", "NDVI"]
            df = df.sort_values("date")
            if df.empty:
                s.update(label="Sem dados NDVI após processamento.", state="error")
                return None

            # Guarda em sessão p/ outras abas
            st.session_state["saag_ndvi_df"] = df.copy()
            s.update(label="Série NDVI pronta para exportação.", state="complete")
            return df
        except Exception as e:
            s.update(label="Erro ao calcular série NDVI.", state="error")
            st.error("Falha ao obter/calcular NDVI.")
            st.code(str(e))
            _install_hint()
            return None

# ---------------------------------------------------------------------
# Botões

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Exportar CSV", type="primary"):
        df = get_timeseries_df()
        if df is None:
            st.warning("Não foi possível gerar a série NDVI para exportar.")
        else:
            df.to_csv(csv_path, index=False, encoding="utf-8")
            st.success(f"CSV salvo em: {csv_path}")
            st.download_button("Baixar CSV gerado", data=csv_path.read_bytes(),
                               file_name=csv_path.name, mime="text/csv")

with c2:
    if st.button("Exportar Parquet"):
        df = get_timeseries_df()
        if df is None:
            st.warning("Não foi possível gerar a série NDVI para exportar.")
        else:
            try:
                df.to_parquet(parquet_path, index=False)
                st.success(f"Parquet salvo em: {parquet_path}")
                st.download_button("Baixar Parquet gerado", data=parquet_path.read_bytes(),
                                   file_name=parquet_path.name, mime="application/octet-stream")
            except Exception as e:
                st.error("Erro ao salvar Parquet.")
                st.code(str(e))

with c3:
    if st.button("Exportar GeoPackage"):
        # Exporta o AOI (BBOX) em EPSG:4326 num GeoPackage.
        try:
            import geopandas as gpd
            from shapely.geometry import box
        except Exception:
            st.error("geopandas/shapely não instalados.")
            _install_hint()
        else:
            try:
                minx, miny, maxx, maxy = _parse_bbox(inputs["bbox_wgs84"])
                gdf = gpd.GeoDataFrame(
                    {
                        "name": ["AOI"],
                        "start": [inputs.get("start_date")],
                        "end": [inputs.get("end_date")],
                        "resolution_m": [int(inputs.get("resolution_m", 10))],
                    },
                    geometry=[box(minx, miny, maxx, maxy)],
                    crs="EPSG:4326",
                )
                # Se já existir, sobrescreve a camada 'aoi'
                gdf.to_file(gpkg_path, layer="aoi", driver="GPKG")
                st.success(f"GeoPackage salvo em: {gpkg_path} (camada 'aoi').")
                st.download_button("Baixar GeoPackage gerado", data=gpkg_path.read_bytes(),
                                   file_name=gpkg_path.name, mime="application/geopackage+sqlite3")
            except Exception as e:
                st.error("Erro ao salvar GeoPackage.")
                st.code(str(e))

# Aviso útil quando nada foi gerado ainda
from pathlib import Path as _P
if not any(p.exists() for p in [_P(csv_path), _P(parquet_path), _P(gpkg_path)]):
    st.info("Nenhum arquivo exportado ainda. Clique em um dos botões acima para gerar.")
