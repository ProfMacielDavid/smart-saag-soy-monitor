import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Exportações")
st.caption("Gere GeoPackage / CSV / Parquet para dashboards")

out_dir = Path("outputs")
out_dir.mkdir(parents=True, exist_ok=True)

csv_path = out_dir / "ts_ndvi.csv"
parquet_path = out_dir / "ts_ndvi.parquet"
gpkg_path = out_dir / "ts_ndvi.gpkg"


def load_ts():
    """Carrega a série temporal do CSV, se existir."""
    if csv_path.exists():
        try:
            return pd.read_csv(csv_path, parse_dates=["date"])
        except Exception:
            return pd.read_csv(csv_path)
    st.warning("Arquivo outputs/ts_ndvi.csv não encontrado. "
               "Vá à página **Home** e clique em **Executar exemplo NDVI**.")
    return None


col1, col2, col3 = st.columns(3)

# ---------------------- CSV ----------------------
with col1:
    if st.button("Exportar CSV"):
        if csv_path.exists():
            st.success(f"CSV já disponível em {csv_path}")
            st.download_button("Baixar CSV", csv_path.read_bytes(), "ts_ndvi.csv", "text/csv")
        else:
            df = load_ts()
            if df is not None:
                df.to_csv(csv_path, index=False)
                st.success(f"CSV salvo em {csv_path}")
                st.download_button("Baixar CSV", csv_path.read_bytes(), "ts_ndvi.csv", "text/csv")

# -------------------- Parquet --------------------
with col2:
    if st.button("Exportar Parquet"):
        df = load_ts()
        if df is not None:
            try:
                df.to_parquet(parquet_path, index=False)
                st.success(f"Parquet salvo em {parquet_path}")
                st.download_button("Baixar Parquet", parquet_path.read_bytes(),
                                   "ts_ndvi.parquet", "application/octet-stream")
            except Exception as e:
                st.error(f"Falha ao salvar Parquet: {e}\n"
                         "Dica: instale 'pyarrow' (pip install pyarrow).")

# ------------------- GeoPackage ------------------
with col3:
    if st.button("Exportar GeoPackage"):
        df = load_ts()
        if df is not None:
            try:
                import geopandas as gpd
                from shapely.geometry import Polygon

                # BBOX: tenta usar o que foi salvo na página "Áreas e Períodos"
                bbox_str = st.session_state.get("bbox", "-63.95,-8.85,-63.80,-8.75")
                parts = [float(p.strip()) for p in bbox_str.split(",")]
                minx, miny, maxx, maxy = parts
                poly = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)])

                # Estatísticas simples sobre a série
                stats = dict(
                    start=str(pd.to_datetime(df["date"]).min().date() if "date" in df else ""),
                    end=str(pd.to_datetime(df["date"]).max().date() if "date" in df else ""),
                    n_obs=int(len(df)),
                    ndvi_mean=float(df["NDVI"].mean()) if "NDVI" in df else None,
                    ndvi_min=float(df["NDVI"].min()) if "NDVI" in df else None,
                    ndvi_max=float(df["NDVI"].max()) if "NDVI" in df else None,
                )

                gdf = gpd.GeoDataFrame([stats], geometry=[poly], crs="EPSG:4326")
                # Camada vetorial simplificada: 1 polígono do BBOX + atributos
                gdf.to_file(gpkg_path, layer="ndvi_bbox", driver="GPKG")
                st.success(f"GeoPackage salvo em {gpkg_path} (camada 'ndvi_bbox').")
                st.download_button("Baixar GeoPackage", gpkg_path.read_bytes(),
                                   "ts_ndvi.gpkg", "application/octet-stream")

            except ModuleNotFoundError:
                st.error(
                    "Para exportar GeoPackage, instale os pacotes geoespaciais.\n"
                    "Conda (recomendado): conda install -c conda-forge geopandas pyogrio\n"
                    "ou pip: pip install geopandas shapely pyproj fiona pyogrio"
                )
            except Exception as e:
                st.error(f"Falha ao salvar GeoPackage: {e}")

st.divider()

# Atalhos de download rápidos se já existirem
if csv_path.exists():
    st.download_button("Baixar CSV (rápido)", csv_path.read_bytes(),
                       "ts_ndvi.csv", "text/csv")
if parquet_path.exists():
    st.download_button("Baixar Parquet (rápido)", parquet_path.read_bytes(),
                       "ts_ndvi.parquet", "application/octet-stream")
if gpkg_path.exists():
    st.download_button("Baixar GeoPackage (rápido)", gpkg_path.read_bytes(),
                       "ts_ndvi.gpkg", "application/octet-stream")
