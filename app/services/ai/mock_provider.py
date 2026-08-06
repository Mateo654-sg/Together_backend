"""
Proveedor de IA mock para desarrollo y testing.

Genera respuestas basadas en el contexto real del usuario sin consumir
tokens de ningún proveedor externo. Indica explícitamente que la respuesta
proviene de un modo demo.
"""

import random
import re

from app.services.ai.base import AIProvider


def _find_value(context: str, label: str) -> float | None:
    """Extrae el valor numérico de una línea del contexto: 'Etiqueta: $X COP'."""
    pattern = rf"^{re.escape(label)}[^:]*: \$([\d.,]+) COP"
    for line in context.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            return float(match.group(1).replace(".", "").replace(",", ""))
    return None


def _first_matching_line(context: str, prefix: str) -> str | None:
    for line in context.splitlines():
        if line.strip().startswith(prefix):
            return line.strip()
    return None


class MockAIProvider(AIProvider):
    """Proveedor mock que genera respuestas basadas en reglas y contexto real."""

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-v1"

    async def generate(self, prompt: str, context: str = "") -> dict:
        prompt_lower = prompt.lower()
        demo_note = (
            "\n\n[Modo demo: respuesta generada localmente, no por un modelo de IA.]"
        )

        total_expense = _find_value(context, "Gastos totales")
        total_income = _find_value(context, "Ingresos totales")
        balance = _find_value(context, "Saldo")
        savings_rate_line = _first_matching_line(context, "Tasa de ahorro")

        top_expense = None
        for line in context.splitlines():
            if re.match(r"^- \$[\d.,]+ COP en ", line.strip()):
                top_expense = line.strip()
                break

        goal_lines = [
            line.strip()
            for line in context.splitlines()
            if line.strip().startswith("- ") and "% completado" in line
        ]

        if any(w in prompt_lower for w in ["cuánto", "cuanto", "gasté", "gaste"]):
            if total_expense is not None:
                answer = f"Según tus registros, tus gastos totales ascienden a ${total_expense:,.0f} COP."
                if top_expense:
                    answer += f" Un ejemplo de gasto reciente: {top_expense[2:]}."
            else:
                answer = "Aún no registras gastos. Registra tus primeros gastos para que pueda analizarlos."
        elif any(w in prompt_lower for w in ["ahorr", "saldo"]):
            if balance is not None and total_income is not None:
                answer = f"Tu saldo actual es ${balance:,.0f} COP."
                if savings_rate_line:
                    answer += f" {savings_rate_line.capitalize()}."
            else:
                answer = "No tengo suficientes datos para calcular tu saldo. Registra ingresos y gastos primero."
        elif any(w in prompt_lower for w in ["meta", "objetivo"]):
            if goal_lines:
                answer = f"Tienes {len(goal_lines)} meta(s) activa(s):"
                for line in goal_lines:
                    answer += f"\n- {line[2:]}"
            else:
                answer = "Aún no tienes metas registradas. Puedes crear una meta de ahorro para empezar."
        elif any(w in prompt_lower for w in ["consejo", "recomendar", "ayuda"]):
            if total_income and total_expense is not None:
                answer = (
                    f"Tus gastos representan el "
                    f"{total_expense / total_income * 100:.0f}% de tus ingresos "
                    f"(${total_expense:,.0f} COP de ${total_income:,.0f} COP). "
                    f"Considera reducir gastos en categorías no esenciales para mejorar tu ahorro."
                )
            else:
                answer = "Registra tus ingresos y gastos para que pueda darte recomendaciones personalizadas."
        elif any(w in prompt_lower for w in ["comparar", "comparación"]):
            if total_expense is not None:
                answer = (
                    f"Este mes tus gastos totales son ${total_expense:,.0f} COP. "
                    "Registra gastos de meses anteriores para comparar tendencias."
                )
            else:
                answer = "Aún no hay datos suficientes para hacer una comparación."
        else:
            answer = "He revisado tu situación financiera general."
            if total_expense is not None:
                answer += f" Tus gastos totales son ${total_expense:,.0f} COP."
            if total_income is not None:
                answer += f" Tus ingresos totales son ${total_income:,.0f} COP."
            answer += " ¿Te gustaría que profundice en algún aspecto específico?"

        return {
            "answer": answer + demo_note,
            "tokens_input": len(prompt.split()) + len(context.split()),
            "tokens_output": len(answer.split()),
        }

    async def embeddings(self, text: str) -> list[float]:
        return [random.random() for _ in range(384)]
