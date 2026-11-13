"""Las cuatro configuraciones del artículo, una clase por cada una.

Todas comparten la misma interfaz; lo único que cambia entre mediciones es
qué clase atiende el pedido. `crear` elige la clase a partir del código.
"""
import asyncio
from abc import ABC, abstractmethod

from demostrador.services.origen import PAQUETES, Contexto, Paquete


class Entrega(ABC):
    codigo: str

    @abstractmethod
    async def entregar(self, paquete: Paquete, ctx: Contexto) -> bool:
        """Entrega el paquete. Devuelve True si se sirvió desde la LAN."""

    def sincronizacion(self) -> int:
        """Descargas que el mirror hace fuera de la sesión."""
        return 0


class Directo(Entrega):
    """Línea base: cada pedido sale a internet."""
    codigo = "base"

    async def entregar(self, paquete, ctx):
        await ctx.enlace.descargar(paquete)
        return False


class ConCache(Entrega):
    """Caché bajo demanda: el primer pedido sale; los demás esperan y reciben la copia."""
    codigo = "cache"

    async def entregar(self, paquete, ctx):
        candado = ctx.candados.setdefault(paquete.nombre, asyncio.Lock())
        async with candado:
            if paquete.nombre not in ctx.cache:
                await ctx.enlace.descargar(paquete)
                ctx.cache.add(paquete.nombre)
                return False
        await ctx.enlace.entregar_local(paquete)
        return True


class ConMirror(Entrega):
    """Mirror sincronizado: lo espejado se sirve local; el resto sale a internet."""
    codigo = "mirror"

    async def entregar(self, paquete, ctx):
        if paquete.espejable:
            await ctx.enlace.entregar_local(paquete)
            return True
        await ctx.enlace.descargar(paquete)
        return False

    def sincronizacion(self):
        return sum(p.espejable for p in PAQUETES)


class Ambos(ConMirror):
    """Lo espejado va al mirror; el resto, al caché."""
    codigo = "ambos"

    def __init__(self):
        self._cache = ConCache()

    async def entregar(self, paquete, ctx):
        if paquete.espejable:
            await ctx.enlace.entregar_local(paquete)
            return True
        return await self._cache.entregar(paquete, ctx)


_CLASES = {c.codigo: c for c in (Directo, ConCache, ConMirror, Ambos)}


def crear(codigo: str) -> Entrega:
    if codigo not in _CLASES:
        raise ValueError(f"configuración desconocida: {codigo}")
    return _CLASES[codigo]()
