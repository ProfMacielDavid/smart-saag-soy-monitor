
import streamlit as st
from pathlib import Path
import base64
from datetime import date

st.set_page_config(
    page_title="SMART SAAG • Monitoramento de Soja",
    page_icon="🌱",
    layout="wide",
)

# CSS externo (se existir)
css_path = Path(__file__).parent.parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ----------------------
# HEADER com logo (flex)
# ----------------------
def _find_logo_path() -> Path | None:
    base = Path(__file__).parent.parent
    for p in [
        base / "assets" / "logo.jpg",
        base / "assets" / "LOGO.jpg",
        base / "logo.jpg",
        base / "LOGO.jpg",
    ]:
        if p.exists():
            return p
    return None

def _to_data_uri(p: Path) -> str:
    if p.suffix.lower() in {".jpg", ".jpeg", ".jpe"}:
        mime = "image/jpeg"
    else:
        mime = "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

_logo_path = _find_logo_path()
_logo_src = _to_data_uri(_logo_path) if _logo_path else ""

st.markdown(
    f'''
    <style>
      [data-testid="block-container"] {{ padding-top: 40px !important; }}
      .saag-header-flex {{ display: flex; align-items: center; gap: 28px; margin: 6px 0 4px 0; }}
      .saag-logo {{ width: 360px; height: auto; border-radius: 12px; }}
      .saag-title h3 {{ margin: 0; }}
      .saag-title h4 {{ margin: 2px 0 6px 0; font-weight: 600; }}
      .saag-muted {{ opacity: 0.8; margin: 0; }}
      .saag-howto {{
          margin: 14px 0 18px 0; width: 100%; border-radius: 12px; padding: 12px 16px;
          background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
          box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
      }}
      .saag-howto b {{ opacity: .95; }}
      .saag-howto ol {{ margin: 6px 0 0 18px; padding: 0; }}
      .saag-howto li {{ margin: 2px 0; }}
      @media (max-width: 1200px) {{ .saag-logo {{ width: 320px; }} }}
      @media (max-width: 992px)  {{ .saag-logo {{ width: 280px; }} }}
      @media (max-width: 768px)  {{
        [data-testid="block-container"] {{ padding-top: 24px !important; }}
        .saag-header-flex {{ flex-direction: column; align-items: flex-start; gap: 12px; }}
        .saag-logo {{ width: 240px; }}
        .saag-title h3 {{ font-size: 1.25rem; }}
        .saag-title h4 {{ font-size: 1.05rem; }}
      }}
      @media (max-width: 992px)  {{
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
          width: 100% !important; flex: 1 0 100% !important;
        }}
        div[data-testid="stHorizontalBlock"] {{ gap: 0.5rem !important; }}
      }}
    </style>
    <div class="saag-header-flex">
      <img class="saag-logo" src="{_logo_src}" alt="SMART SAAG Logo" />
      <div class="saag-title">
        <h3>SMART SAAG</h3>
        <h4>Monitoramento de Soja - Protótipo (Centelha II)</h4>
        <p class="saag-muted">Ingestão Sentinel-2 • NDVI/EVI/NDRE • Séries por talhão • Exportações</p>
      </div>
    </div>
    ''',
    unsafe_allow_html=True
)

st.markdown("---")

# Banner de instruções
st.markdown(
    '''
    <div class="saag-howto">
      <b>Como começar - instruções rápidas</b>
      <ol>
        <li><b>Resolução (m):</b> escolha 10-20 m para maior detalhe.</li>
        <li><b>Datas:</b> selecione <em>Data inicial</em> e <em>Data final</em> do período de interesse.</li>
        <li><b>Área de interesse:</b> desenhe no mapa abaixo (retângulo ou polígono).</li>
        <li><b>Executar exemplo NDVI:</b> clique para processar e visualizar os resultados.</li>
      </ol>
    </div>
    ''',
    unsafe_allow_html=True
)

# ---------------------------
# Painel principal
# ---------------------------
with st.container():
    st.markdown("#### Como começar")

    c1, c2, c3 = st.columns(3)
    with c1:
        res = st.number_input("Resolução (m)", min_value=10, max_value=60, value=10, step=10, key="saag_res_in")
    with c2:
        start_date = st.date_input("Data inicial", key="saag_start_in")
    with c3:
        end_date = st.date_input("Data final", key="saag_end_in")

    # Seletor da base
    base_choice = st.selectbox(
        "Base do mapa",
        options=[
            "Esri Satélite (World Imagery)",
            "Sentinel-2 Cloudless (EOX 2020)",
            "Carto Claro (Positron)",
        ],
        index=0,
        help="Escolha uma base que realce vegetação/lavoura."
    )

    st.markdown("Selecione a área de interesse no mapa (desenhe um retângulo ou polígono).")

    try:
        import folium
        from folium.plugins import Draw, Fullscreen, MousePosition
        try:
            from folium.plugins import MeasureControl
            _has_measure = True
        except Exception:
            _has_measure = False
        try:
            from folium.plugins import LocateControl
            _has_locate = True
        except Exception:
            _has_locate = False

        from streamlit_folium import st_folium

        # Centro padrão (exemplo)
        default_minx, default_miny, default_maxx, default_maxy = -63.95, -8.85, -63.80, -8.75
        center_lat = (default_miny + default_maxy) / 2.0
        center_lon = (default_minx + default_maxx) / 2.0

        m = folium.Map(location=[center_lat, center_lon], zoom_start=13, control_scale=True)

        # Bases (uma ativa de cada vez via 'show')
        folium.TileLayer(
            tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="Esri Satélite",
            overlay=False, control=True,
            show=(base_choice == "Esri Satélite (World Imagery)"),
        ).add_to(m)
        folium.TileLayer(
            tiles="https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/2020_3857/{z}/{y}/{x}.jpg",
            attr="Sentinel-2 cloudless © EOX IT Services GmbH",
            name="S2 Cloudless (2020)",
            overlay=False, control=True,
            show=(base_choice == "Sentinel-2 Cloudless (EOX 2020)"),
        ).add_to(m)
        folium.TileLayer(
            "cartodbpositron", name="Carto Positron",
            overlay=False, control=True,
            show=(base_choice == "Carto Claro (Positron)"),
        ).add_to(m)

        Fullscreen().add_to(m)
        MousePosition(position="bottomleft", separator=" , ", prefix="Lat,Lon").add_to(m)
        if _has_measure:
            try: MeasureControl(primary_length_unit="meters").add_to(m)
            except Exception: pass
        if _has_locate:
            try: LocateControl(auto_start=False).add_to(m)
            except Exception: pass

        Draw(
            export=False, position="topleft",
            draw_options={
                "polyline": False, "rectangle": True, "polygon": True,
                "circle": False, "marker": False, "circlemarker": False,
            },
            edit_options={"edit": True, "remove": True},
        ).add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)

        map_state = st_folium(m, height=520, key="map_aoi")

        def _bbox_from_geojson(features):
            xs, ys = [], []
            for f in features:
                geom = f.get("geometry", {})
                coords = geom.get("coordinates", [])
                gtype = geom.get("type", "")
                if gtype == "Polygon":
                    rings = coords[0] if coords else []
                    for x, y in rings: xs.append(x); ys.append(y)
                elif gtype == "MultiPolygon":
                    for poly in coords:
                        rings = poly[0] if poly else []
                        for x, y in rings: xs.append(x); ys.append(y)
            if xs and ys:
                return min(xs), min(ys), max(xs), max(ys)
            return None

        bbox_val = None
        if isinstance(map_state, dict) and "all_drawings" in map_state:
            drawings = map_state.get("all_drawings") or []
            bbox = _bbox_from_geojson(drawings)
            if bbox:
                minx, miny, maxx, maxy = bbox
                bbox_val = f"{minx:.5f},{miny:.5f},{maxx:.5f},{maxy:.5f}"
                st.session_state["bbox_wgs84"] = bbox_val

        if bbox_val:
            st.caption(f"BBOX selecionado (EPSG:4326): {bbox_val}")
        else:
            st.caption("Desenhe a área no mapa para obter o BBOX (EPSG:4326).")

    except Exception as e:
        st.error("Falha ao carregar o mapa. Verifique dependencias: folium e streamlit-folium.")
        st.exception(e)

    if st.button("Executar exemplo NDVI", type="primary"):
        if not st.session_state.get("bbox_wgs84"):
            st.warning("Selecione a área no mapa para continuar (BBOX ausente).")
        else:
            # Armazena entradas consolidadas para outras páginas
            st.session_state['saag_inputs'] = {
                "resolution_m": int(res),
                "start_date": str(start_date) if isinstance(start_date, date) else str(start_date),
                "end_date": str(end_date) if isinstance(end_date, date) else str(end_date),
                "bbox_wgs84": st.session_state.get("bbox_wgs84"),
            }
            st.session_state['saag_ready'] = True
            st.info("Rodando stub do protótipo...")
            st.success("Processo iniciado! Abra a página 'Séries Temporais' para visualizar os resultados.")

st.markdown(" ")
st.caption("© Smart SAAG — 2025")
