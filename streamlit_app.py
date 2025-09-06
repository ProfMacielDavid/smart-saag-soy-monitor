
# streamlit_app.py
# Entrypoint para deploy (ex.: Streamlit Community Cloud).
# Redireciona para o app principal em app/Home.py.

import os, sys, runpy

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.join(ROOT, "app", "Home.py")

# Garante que a raiz esteja no sys.path (para imports relativos)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Executa o Home.py como script principal
runpy.run_path(APP_PATH, run_name="__main__")
