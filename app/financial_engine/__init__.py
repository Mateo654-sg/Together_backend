"""
Financial Rules Engine (FRE).

Núcleo matemático de Together. Toda decisión financiera se calcula aquí.

Principios:
- Exacto, reproducible, auditable, determinístico y testeable.
- La IA nunca realiza cálculos; solo interpreta resultados del motor.
- El Frontend nunca calcula indicadores.
- La Base de Datos nunca contiene lógica.
"""

from decimal import Decimal

from app.financial_engine.balances import personal_balance, shared_balance
from app.financial_engine.budgets import budget_alert_level, budget_consumption
from app.financial_engine.cashflow import (
    burn_rate,
    classify_cash_flow,
    net_cash_flow,
)
from app.financial_engine.couple import couple_balance_index
from app.financial_engine.forecasts import forecast_balance, year_projection
from app.financial_engine.goals import (
    goal_days_remaining,
    goal_forecast_date,
    goal_forecast_months,
    goal_on_track,
    goal_predicted_completion,
    goal_progress,
)
from app.financial_engine.health import financial_health
from app.financial_engine.kpis import (
    classify_savings_rate,
    expense_ratio,
    monthly_average,
    savings_rate,
    weekly_average,
)
from app.financial_engine.liquidity import classify_liquidity, liquidity_ratio
from app.financial_engine.predictions import (
    balance_forecast,
    cash_flow_forecast,
    goal_completion_forecast,
    savings_forecast,
)
from app.financial_engine.scores import (
    debt_score,
    financial_score,
    goals_component,
    health_status_en,
    score_grade,
    score_grade_en,
)
from app.financial_engine.trends import (
    category_dominance,
    spending_trend,
    top_categories,
)

__version__ = "1.0.0"
version = __version__

__all__ = [
    "Decimal",
    "__version__",
    "personal_balance",
    "shared_balance",
    "budget_alert_level",
    "budget_consumption",
    "burn_rate",
    "classify_cash_flow",
    "net_cash_flow",
    "couple_balance_index",
    "forecast_balance",
    "year_projection",
    "goal_forecast_date",
    "goal_forecast_months",
    "goal_on_track",
    "goal_predicted_completion",
    "goal_progress",
    "goal_days_remaining",
    "financial_health",
    "classify_savings_rate",
    "expense_ratio",
    "monthly_average",
    "savings_rate",
    "weekly_average",
    "classify_liquidity",
    "liquidity_ratio",
    "balance_forecast",
    "cash_flow_forecast",
    "goal_completion_forecast",
    "savings_forecast",
    "debt_score",
    "financial_score",
    "goals_component",
    "health_status_en",
    "score_grade",
    "score_grade_en",
    "category_dominance",
    "spending_trend",
    "top_categories",
    "version",
]
