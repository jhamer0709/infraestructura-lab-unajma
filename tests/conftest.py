import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Base de datos temporal y origen rápido: las pruebas no tocan datos reales.
_carpeta = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_carpeta}/pruebas.db"
os.environ["ORIGEN_RETARDO_MS"] = "20"
os.environ["ENTORNO"] = "pruebas"
os.environ.pop("CONFIGURACION", None)
