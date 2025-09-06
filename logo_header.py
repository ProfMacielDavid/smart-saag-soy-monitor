
"""
logo_header.py
----------------
Injeta a LOGO no topo da página do Streamlit, posicionada de forma fixa (top-left),
sem depender de caminhos relativos no HTML. Usa data URI (base64) para garantir exibição
mesmo com caminhos locais.

Como usar no seu app Streamlit (no topo do arquivo principal):
    from logo_header import inject_logo
    inject_logo()  # usa o caminho padrão informado por você

Opcionalmente, você pode passar um caminho diferente e ajustar o tamanho:
    inject_logo(r"E:\Projeto_Smart_SAAG_2025_GitHub\smart-saag-soy-monitor\LOGO.jpg", height_px=72)
"""
from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st

# Caminho padrão informado pelo usuário
_DEFAULT_ABS_PATH = Path(r"E:\Projeto_Smart_SAAG_2025_GitHub\smart-saag-soy-monitor\LOGO.jpg")

# Candidatos adicionais (caso mova o projeto mantendo a logo na raiz)
_DEFAULT_CANDIDATES = [
    _DEFAULT_ABS_PATH,
    Path("LOGO.jpg"),
    Path("./LOGO.jpg"),
    Path("./assets/LOGO.jpg"),
]

def _detect_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".png"}:
        return "image/png"
    if ext in {".jpg", ".jpeg", ".jpe"}:
        return "image/jpeg"
    # escolha segura padrão
    return "image/jpeg"

def _read_logo_bytes(logo_path: str | Path | None) -> tuple[bytes, str]:
    candidates = []
    if logo_path:
        candidates.append(Path(logo_path))
    candidates.extend(_DEFAULT_CANDIDATES)
    for p in candidates:
        if p.is_file():
            return p.read_bytes(), _detect_mime(p)
    raise FileNotFoundError(
        "LOGO não encontrada. Verifique se 'LOGO.jpg' está na raiz do projeto "
        "ou ajuste o caminho absoluto em inject_logo(...)."
    )

def inject_logo(logo_path: str | Path | None = None, *, height_px: int = 64, pad_top_px: int = 96) -> None:
    """Injeta a logo fixa no topo-esquerda da página.

    Args:
        logo_path: Caminho para a imagem. Se None, tenta os caminhos padrão.
        height_px: Altura da logo, em pixels.
        pad_top_px: Padding adicionado no container principal para não sobrepor o conteúdo.
    """
    # Lê bytes e define MIME
    img_bytes, mime = _read_logo_bytes(logo_path)
    b64 = base64.b64encode(img_bytes).decode("ascii")

    # CSS: fixa a logo e ajusta o padding do container principal
    css = f"""
    <style>
    .app-logo-fixed {{
        position: fixed;
        top: 10px;
        left: 16px;
        z-index: 1000;
    }}
    /* Ajusta o padding do container principal para evitar sobreposição */
    [data-testid="block-container"] {{
        padding-top: {pad_top_px}px !important;
    }}
    </style>
    """
    html = f"""
    <div class="app-logo-fixed">
        <img src="data:{mime};base64,{b64}" height="{height_px}" />
    </div>
    """
    st.markdown(css + html, unsafe_allow_html=True)
