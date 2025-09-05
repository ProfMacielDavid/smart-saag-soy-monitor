# SMART SAAG – Soy Monitoring (Centelha II)

<p align="center">
  <img src="assets/logo.jpg" alt="Smart SAAG logo" width="280">
</p>

**Prototype software** developed under the Centelha II program for soybean crop monitoring using satellite imagery and AI-assisted analytics.

## Highlights
- Sentinel-2 ingestion via **Sentinel Hub** API (tiling, cloud masking, rate limiting handling)
- Vegetation indices (NDVI, EVI, NDRE), bare-soil/vegetation masks and anomaly detection
- Time-series features at plot-level (mean, p25/p50/p75, std, valid-pixels)
- Export to GeoPackage/CSV and **dashboards-ready** parquet
- Modular pipeline with `pydantic` configs and `hydra`-style overrides
- Ready for GitHub Actions (lint + tests) and Docker packaging

> ⚠️ This is a prototype and will evolve. For the FAPERON report, see `docs/ONE-PAGER_FAPERON.md`.

## Quickstart
```bash
# 1) Create env
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -U pip

# 2) Install package in editable mode
pip install -e .

# 3) Configure credentials (see examples/config.example.json)
export SH_CLIENT_ID=YOUR_ID
export SH_CLIENT_SECRET=YOUR_SECRET

# 4) Run minimal example
python -m saag_soy_monitor.examples.fetch_and_ndvi --bbox -63.95,-8.85,-63.80,-8.75 --crs EPSG:4326 --start 2025-05-01 --end 2025-09-01
```

## CLI (coming with prototype)
```bash
saag-soy fetch --bbox <minx,miny,maxx,maxy> --start YYYY-MM-DD --end YYYY-MM-DD
saag-soy index --method ndvi --out data/ndvi.gpkg
saag-soy timeseries --talhao ./examples/talhao_01.geojson --out outputs/ts_talhao_01.csv
```

## Folder structure
```
.
├── assets/                 # Branding and figures
├── docs/
│   └── ONE-PAGER_FAPERON.md
├── examples/
│   └── config.example.json
├── src/saag_soy_monitor/
│   ├── __init__.py
│   ├── senhub.py           # Sentinel Hub helper
│   └── examples/
│       └── fetch_and_ndvi.py
├── tests/
├── LICENSE
├── pyproject.toml
└── README.md
```

## License
MIT (see `LICENSE`)

## Acknowledgements
Developed by **Smart SAAG** with support from **FAPERON – Centelha II**.
