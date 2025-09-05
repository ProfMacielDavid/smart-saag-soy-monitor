from dataclasses import dataclass
import os

# Optional: install sentinelhub before using this helper
try:
    from sentinelhub import (
        MimeType,
        CRS,
        BBox,
        SentinelHubRequest,
        DataCollection,
        bbox_to_dimensions,
    )
except Exception:  # sentinelhub not installed in dev
    MimeType = CRS = BBox = SentinelHubRequest = DataCollection = bbox_to_dimensions = (
        None
    )


@dataclass
class SenHubConfig:
    client_id: str = os.getenv("SH_CLIENT_ID", "")
    client_secret: str = os.getenv("SH_CLIENT_SECRET", "")
    resolution: int = 10
    collection: str = "SENTINEL2_L2A"


class SenHub:
    """Minimal helper for Sentinel Hub requests used in the prototype."""

    def __init__(self, cfg: SenHubConfig):
        self.cfg = cfg
        self.collection = (
            getattr(DataCollection, cfg.collection, None) if DataCollection else None
        )

    def ndvi_evalscript(self) -> str:
        return """
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
