"""
Motor 13: Financial Health.

Evalúa liquidez, ahorro, presupuesto, deudas y metas para producir
un estado de salud financiera: Excelente, Bueno, Regular o Crítico.
"""

from decimal import Decimal

from app.financial_engine.scores import (
    WEIGHTS,
    budget_control_component,
    cash_flow_component,
    financial_score,
    liquidity_component,
    saving_rate_component,
    score_grade,
)


def financial_health(
    savings_rate: Decimal,
    budget_consumption: Decimal,
    debt: Decimal,
    liquidity: Decimal,
    goals: Decimal,
    cash_flow: Decimal,
) -> dict:
    """Calcula la salud financiera con score (0-100) y estado.

    Returns:
        dict con "score", "status" y "components".
    """
    score = financial_score(
        savings_rate,
        budget_consumption,
        debt,
        liquidity,
        goals,
        cash_flow,
    )
    return {
        "score": score,
        "status": score_grade(score),
        "components": {
            "saving_rate": saving_rate_component(savings_rate),
            "budget_control": budget_control_component(budget_consumption),
            "debt": debt,
            "liquidity": liquidity_component(liquidity),
            "goals": goals,
            "cash_flow": cash_flow_component(cash_flow),
            "weights": {key: float(weight) for key, weight in WEIGHTS.items()},
        },
    }
