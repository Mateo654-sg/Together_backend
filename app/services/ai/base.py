"""
Interfaz base para proveedores de IA.

Permite desacoplar el sistema del proveedor específico.
"""
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Interfaz abstracta para proveedores de IA."""

    @abstractmethod
    async def generate(self, prompt: str, context: str = "") -> dict:
        """Genera una respuesta basada en prompt y contexto."""
        pass

    @abstractmethod
    async def embeddings(self, text: str) -> list[float]:
        """Genera embeddings para un texto."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del proveedor."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Nombre del modelo."""
        pass
