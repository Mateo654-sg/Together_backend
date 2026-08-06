"""
Motor 14: Couple Balance Index.

Mide el equilibrio financiero entre ambos integrantes de la pareja (0-100).

Variables: participación, deudas, aportes y cumplimiento.
"""

from decimal import Decimal

from app.financial_engine.utils import ZERO, as_decimal, clamp, safe_percentage


def couple_balance_index(
    contributions_mateo, contributions_laura, debts_mateo, debts_laura
) -> Decimal:
    """Calcula el índice de equilibrio financiero de la pareja (0-100)."""
    total_contributions = as_decimal(contributions_mateo) + as_decimal(contributions_laura)
    if total_contributions <= ZERO:
        return Decimal("50")

    mateo_share = as_decimal(contributions_mateo) / total_contributions
    balance_component = Decimal("100") - abs(mateo_share - Decimal("0.5")) * 200

    debt_penalty = (
        safe_percentage(as_decimal(debts_mateo), total_contributions)
        + safe_percentage(as_decimal(debts_laura), total_contributions)
    ) / 2
    debt_component = clamp(Decimal("100") - debt_penalty * 5, ZERO, Decimal("100"))

    return clamp(
        balance_component * Decimal("0.7") + debt_component * Decimal("0.3"),
        ZERO,
        Decimal("100"),
    )
