"""Origen y enlace simulados.

Supuesto del modelo: el enlace de salida reparte su capacidad por igual entre
las descargas simultáneas. Una descarga sola tarda retardo x peso; con k a la
vez, cada una avanza a 1/k de esa velocidad. Todo lo que muestra el
demostrador es consecuencia de este supuesto, no una medición.
"""
import asyncio
from dataclasses import dataclass, field

from demostrador import config


@dataclass(frozen=True)
class Paquete:
    nombre: str
    peso: float       # tamaño relativo de la descarga
    espejable: bool   # True si un mirror de repositorios lo contiene


# Lista versionada (variable de control). Las imágenes de contenedor no están
# en un mirror de repositorios de paquetes: solo las cubre el caché.
PAQUETES = (
    Paquete("compilador", 1.0, True),
    Paquete("interprete", 0.8, True),
    Paquete("librerias-base", 0.6, True),
    Paquete("gestor-paquetes", 0.3, True),
    Paquete("imagen-contenedor", 1.5, False),
)

_PASO_S = 0.005


@dataclass
class Enlace:
    """Enlace de salida compartido por todas las estaciones de una sesión."""
    retardo_s: float
    activas: int = 0
    salidas: int = 0

    async def descargar(self, paquete: Paquete) -> None:
        self.salidas += 1
        self.activas += 1
        try:
            pendiente = self.retardo_s * paquete.peso
            while pendiente > 0:
                await asyncio.sleep(_PASO_S)
                pendiente -= _PASO_S / self.activas
        finally:
            self.activas -= 1

    async def entregar_local(self, paquete: Paquete) -> None:
        """Entrega desde la LAN: no usa el enlace de salida."""
        await asyncio.sleep(self.retardo_s * paquete.peso * config.FRACCION_LOCAL)


@dataclass
class Contexto:
    """Estado de una sesión. Se crea nuevo cada vez: el caché parte frío."""
    enlace: Enlace
    cache: set = field(default_factory=set)
    candados: dict = field(default_factory=dict)
