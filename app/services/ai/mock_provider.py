"""
Proveedor de IA mock para desarrollo y testing.

Genera respuestas basadas en reglas sin consumir tokens reales.
"""
import random

from app.services.ai.base import AIProvider


class MockAIProvider(AIProvider):
    """Proveedor mock que genera respuestas predefinidas."""

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-v1"

    async def generate(self, prompt: str, context: str = "") -> dict:
        prompt_lower = prompt.lower()

        if any(w in prompt_lower for w in ["cuánto", "cuanto", "gasté", "gaste"]):
            answer = "Este mes has gastado $1.250.000 COP en total. Tu mayor categoría es alimentación con $450.000."
        elif any(w in prompt_lower for w in ["ahorr", "saldo"]):
            answer = "Tu saldo actual es $2.350.000 COP. Has ahorrado el 32% de tus ingresos este mes."
        elif any(w in prompt_lower for w in ["meta", "objetivo"]):
            answer = "Estás en camino de cumplir tu meta de vacaciones. Llevas el 45% del objetivo con 8 meses restantes."
        elif any(w in prompt_lower for w in ["consejo", "recomendar", "ayuda"]):
            answer = "Basado en tus patrones, podrías ahorrar $180.000 mensuales reduciendo gastos en restaurantes. También considera automatizar tus aportes a metas."
        elif any(w in prompt_lower for w in ["comparar", "comparación"]):
            answer = "Comparado con el mes pasado, tus gastos disminuyeron un 8%. Los ingresos se mantuvieron estables. Excelente progreso."
        else:
            answer = "He analizado tus finanzas. Tu situación financiera es estable. ¿Te gustaría que profundice en algún aspecto específico?"

        return {
            "answer": answer,
            "tokens_input": len(prompt.split()) + len(context.split()),
            "tokens_output": len(answer.split()),
        }

    async def embeddings(self, text: str) -> list[float]:
        return [random.random() for _ in range(384)]
