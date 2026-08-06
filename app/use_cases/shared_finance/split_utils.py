"""
Utilidades compartidas para el cálculo de deuda de gastos compartidos.

Centraliza el cálculo de la porción que debe el partner según el tipo de
split (equal, percentage, custom) para evitar drift contable entre el
create y el update de un gasto compartido.
"""

import json
from decimal import Decimal

from app.core.exceptions import ValidationException
from app.models.shared_expense import SplitType


def calculate_debt_amount(
    total: Decimal,
    split_type: SplitType,
    split_details: str | None,
) -> Decimal:
    """Calcula el monto que debe el partner por un gasto compartido.

    Args:
        total: Monto total del gasto compartido.
        split_type: Tipo de división (EQUAL, PERCENTAGE, CUSTOM).
        split_details: Detalles JSON del split (porcentaje o monto custom).

    Returns:
        El monto adeudado redondeado a 2 decimales.

    Raises:
        ValidationException: Si los detalles del split son inválidos.
    """
    if split_type == SplitType.EQUAL:
        return (total / 2).quantize(Decimal("0.01"))
    if split_details:
        try:
            details = json.loads(split_details)
        except (json.JSONDecodeError, TypeError):
            raise ValidationException("split_details tiene un formato JSON inválido.")
        if split_type == SplitType.PERCENTAGE:
            pct = details.get("partner_percentage", 50)
            if not isinstance(pct, (int, float)) or not (0 <= pct <= 100):
                raise ValidationException("partner_percentage debe estar entre 0 y 100.")
            return (total * Decimal(str(pct)) / 100).quantize(Decimal("0.01"))
        if split_type == SplitType.CUSTOM:
            amount = details.get("partner_amount", 0)
            if not isinstance(amount, (int, float)) or Decimal(str(amount)) < 0:
                raise ValidationException("partner_amount debe ser un monto válido.")
            if Decimal(str(amount)) > total:
                raise ValidationException("partner_amount no puede exceder el total.")
            return Decimal(str(amount)).quantize(Decimal("0.01"))
    return (total / 2).quantize(Decimal("0.01"))
