from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Tuple

import numpy as np
import pandas as pd

# Sentinel Hub é opcional; o pipeline funciona em modo "demo" se faltar
try:
    from sentinelhub import (
        BBox,
        CRS,
        DataCollection,
        MimeType,
        SentinelHubRequest,
        bbox_to_dimensions,
        SHConfig,
    )

    _HAS_SH = True
except Exception:
    _HAS_SH = False


@dataclass
class RunParams:
    bbox_xyxy: Tuple[float, float, float, float]  # minx, miny, maxx, maxy (EPSG:4326)
    start: date
    end: date
    resolution: int = 10
    collection: str = "SENTINEL2_L2A"


def _parse_bbox(bbox_str: str) -> Tuple[float, float, float, float]:
    parts = [p.strip() for p in bbox_str.split(",")]
    if len(parts) != 4:
        raise ValueError("BBOX deve ter 4 números: minx,miny,maxx,maxy")
    return tuple(map(float, parts))  # type: ignore[return-value]


def _ensure_outputs() -> Path:
    out = Path("outputs")
    out.mkdir(parents=True, exist_ok=True)
    return out


def _demo_timeseries(params: RunParams) -> pd.DataFrame:
    """Gera uma série NDVI fictícia (para funcionar sem credenciais)."""
    idx = pd.date_range(params.start, params.end, freq="7D")
    vals = np.clip(np.sin(np.linspace(0, 3, len(idx))) * 0.3 + 0.6, 0, 1)
    return pd.DataFrame({"date": idx, "NDVI": vals})


def _real_timeseries_with_sentinelhub(params: RunParams) -> pd.DataFrame:
    """Exemplo minimalista usando Sentinel Hub. Requer variáveis de ambiente:
    SH_CLIENT_ID e SH_CLIENT_SECRET.
    """
    client_id = os.getenv("SH_CLIENT_ID", "")
    client_secret = os.getenv("SH_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise RuntimeError("Credenciais Sentinel Hub ausentes (defina SH_CLIENT_ID e SH_CLIENT_SECRET).")

    cfg = SHConfig()
    cfg.sh_client_id = client_id
    cfg.sh_client_secret = client_secret

    bbox = BBox(list(params.bbox_xyxy), crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=params.resolution)

    evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 2, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(s) {
  let ndvi = (s.B08 - s.B04) / (s.B08 + s.B04);
  return [ndvi, s.dataMask];
}
"""

    # Para série temporal, montamos uma requisição por data (simples e robusto)
    dates = list(pd.date_range(params.start, params.end, freq="7D"))
    rows = []
    for d in dates:
        req = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=getattr(DataCollection, params.collection),
                    time_interval=(d.date().isoformat(), d.date().isoformat()),
                    mosaicking_order="mostRecent",
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=cfg,
        )
        try:
            data = req.get_data()[0]  # (H,W,2) -> NDVI, mask
            ndvi = data[:, :, 0]
            mask = data[:, :, 1]
            valid = mask > 0
            if valid.any():
                mean_ndvi = float(np.nanmean(ndvi[valid]))
            else:
                mean_ndvi = np.nan
        except Exception:
            # Falha pontual (sem cena na data, etc.): mantemos NaN
            mean_ndvi = np.nan
        rows.append({"date": d, "NDVI": mean_ndvi})

    df = pd.DataFrame(rows).drop_duplicates(subset=["date"]).sort_values("date")
    return df


def run_example_ndvi(
    bbox: str,
    start: date,
    end: date,
    resolution: int = 10,
    prefer_demo_when_no_creds: bool = True,
) -> Path:
    """Executa a pipeline exemplo e salva CSV em outputs/ts_ndvi.csv.
    Retorna o caminho do CSV.
    """
    params = RunParams(_parse_bbox(bbox), start, end, resolution)

    if _HAS_SH:
        try:
            df = _real_timeseries_with_sentinelhub(params)
        except Exception as exc:
            if not prefer_demo_when_no_creds:
                raise
            # Fallback: série fictícia para não quebrar a UX
            df = _demo_timeseries(params)
            df["note"] = f"fallback_demo: {exc}"
    else:
        df = _demo_timeseries(params)
        df["note"] = "fallback_demo: sentinelhub ausente"

    out_dir = _ensure_outputs()
    out_csv = out_dir / "ts_ndvi.csv"
    df.to_csv(out_csv, index=False)
    return out_csv
