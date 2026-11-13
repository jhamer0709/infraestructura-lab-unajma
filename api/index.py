"""Punto de entrada para Vercel y para uvicorn (api.index:app)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demostrador.app import crear_app  # noqa: E402

app = crear_app()
