"""
Motor 11 y 12: Debt Score y Financial Score.

Debt Score (0-100): evalúa número de deudas, monto y tiempo pendiente.
Financial Score (0-100):

- Saving Rate 25%
- Budget Control 20%
- Debt 20%
- Liquidity 15%
- Goals 10%
- Cash Flow 10%
"""

from decimal import Decimal

from app.financial_engine.utils import ZERO, as_decimal, clamp, safe_percentage

WEIGHTS = {
    "saving_rate": Decimal("0.25"),
    "budget_control": Decimal("0.20"),
    "debt": Decimal("0.20"),
    "liquidity": Decimal("0.15"),
    "goals": Decimal("0.10"),
    "cash_flow": Decimal("0.10"),
}


# ─── Debt Score (Motor 11) ─────────────────────────────────────────────────────

def debt_score(num_debts: int, total_debt, pending_days: int = 0) -> Decimal:
    """Calcula el Debt Score (0-100).

    A mayor deuda (número, monto y tiempo pendiente) menor score.
    """
    amount_penalty = safe_percentage(as_decimal(total_debt), Decimal("10000000"))
    time_penalty = clamp(as_decimal(pending_days) / 30, ZERO, Decimal("10")) * 3
    count_penalty = clamp(as_decimal(num_debts), ZERO, Decimal("10")) * 4

    score = Decimal("100") - amount_penalty - time_penalty - count_penalty
    return clamp(score, ZERO, Decimal("100"))


# ─── Financial Score (Motor 12) ────────────────────────────────────────────────

def saving_rate_component(rate: Decimal) -> Decimal:
    """Convierte la tasa de ahorro en un componente 0-100."""
    return clamp(rate, ZERO, Decimal("100"))


def budget_control_component(consumption: Decimal) -> Decimal:
    """Convierte el consumo de presupuesto en control (100 - consumo)."""
    return clamp(Decimal("100") - consumption, ZERO, Decimal("100"))


def liquidity_component(ratio: Decimal) -> Decimal:
    """Convierte el índice de liquidez en un componente 0-100."""
    return clamp(ratio * 15, ZERO, Decimal("100"))


def cash_flow_component(flow: Decimal) -> Decimal:
    """Convierte el flujo de caja neto en un componente 0-100."""
    if flow >= ZERO:
        return Decimal("100")
    return clamp(Decimal("50") + flow / Decimal("100000"), ZERO, Decimal("100"))


def goals_component(progresses: list[Decimal]) -> Decimal:
    """Promedia el progreso de las metas (0-100)."""
    if not progresses:
        return ZERO
    return clamp(sum(progresses) / len(progresses), ZERO, Decimal("100"))


def financial_score(
    savings_rate: Decimal,
    budget_consumption: Decimal,
    debt: Decimal,
    liquidity: Decimal,
    goals: Decimal,
    cash_flow: Decimal,
) -> Decimal:
    """Calcula el Financial Score ponderado (0-100)."""
    components = {
        "saving_rate": saving_rate_component(savings_rate),
        "budget_control": budget_control_component(budget_consumption),
        "debt": debt,
        "liquidity": liquidity_component(liquidity),
        "goals": goals,
        "cash_flow": cash_flow_component(cash_flow),
    }
    total = sum(
        components[key] * weight for key, weight in WEIGHTS.items()
    )
    return clamp(total, ZERO, Decimal("100"))


def score_grade(score: Decimal) -> str:
    """Clasifica el score: Excelente >= 90, Bueno 75-89, Regular 60-74, Crítico < 60."""
    if score >= Decimal("90"):
        return "Excelente"
    if score >= Decimal("75"):
        return "Bueno"
    if score >= Decimal("60"):
        return "Regular"
    return "Crítico"


def score_grade_en(score: Decimal) -> str:
    """Clasifica el score con etiquetas en inglés (contrato de API)."""
    if score >= Decimal("90"):
        return "Excellent"
    if score >= Decimal("75"):
        return "Good"
    if score >= Decimal("60"):
        return "Fair"
    return "Poor"


def health_status_en(score: Decimal) -> str:
    """Estado de salud financiera en inglés: Excellent, Good, Fair, Critical."""
    if score >= Decimal("90"):
        return "Excellent"
    if score >= Decimal("75"):
        return "Good"
    if score >= Decimal("60"):
        return "Fair"
    return "Critical"
