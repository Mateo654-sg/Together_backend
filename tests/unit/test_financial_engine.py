"""
Tests unitarios del Financial Rules Engine.

Verifica que cada motor sea exacto, determinístico y auditable.
"""

from datetime import date
from decimal import Decimal


from app.financial_engine import (
    budget_alert_level,
    budget_consumption,
    burn_rate,
    category_dominance,
    classify_cash_flow,
    classify_liquidity,
    classify_savings_rate,
    couple_balance_index,
    debt_score,
    expense_ratio,
    financial_health,
    financial_score,
    forecast_balance,
    goal_completion_forecast,
    goal_forecast_months,
    goal_on_track,
    goal_progress,
    liquidity_ratio,
    monthly_average,
    net_cash_flow,
    personal_balance,
    savings_forecast,
    savings_rate,
    score_grade,
    shared_balance,
    spending_trend,
    top_categories,
    weekly_average,
    year_projection,
)


class TestBalances:
    def test_personal_balance_basic(self):
        assert personal_balance(4000000, 2300000) == Decimal("1700000")

    def test_personal_balance_negative(self):
        assert personal_balance(1000000, 1500000) == Decimal("-500000")

    def test_personal_balance_zero_expense(self):
        assert personal_balance(2000000, 0) == Decimal("2000000")

    def test_shared_balance(self):
        assert shared_balance(1300000, 500000) == Decimal("800000")

    def test_shared_balance_zero(self):
        assert shared_balance(0, 0) == Decimal("0")


class TestCashFlow:
    def test_net_cash_flow(self):
        assert net_cash_flow(3000000, 2100000) == Decimal("900000")

    def test_classify_positive(self):
        assert classify_cash_flow(Decimal("500")) == "Positivo"

    def test_classify_negative(self):
        assert classify_cash_flow(Decimal("-500")) == "Negativo"

    def test_classify_neutral(self):
        assert classify_cash_flow(Decimal("0")) == "Neutro"

    def test_burn_rate(self):
        assert burn_rate(3000000, 30) == Decimal("100000")

    def test_burn_rate_zero_days(self):
        assert burn_rate(1000, 0) == Decimal("0")


class TestKpis:
    def test_savings_rate(self):
        assert savings_rate(4000000, 2300000) == Decimal("42.5")

    def test_savings_rate_zero_income(self):
        assert savings_rate(0, 1000) == Decimal("0")

    def test_savings_rate_exceeded_spend(self):
        assert savings_rate(1000, 2000) == Decimal("0")

    def test_classify_savings_excellent(self):
        assert classify_savings_rate(Decimal("35")) == "Excelente"

    def test_classify_savings_good(self):
        assert classify_savings_rate(Decimal("25")) == "Buena"

    def test_classify_savings_regular(self):
        assert classify_savings_rate(Decimal("15")) == "Regular"

    def test_classify_savings_critical(self):
        assert classify_savings_rate(Decimal("5")) == "Crítica"

    def test_expense_ratio(self):
        assert expense_ratio(1500000, 3000000) == Decimal("50")

    def test_weekly_average(self):
        assert weekly_average(700000, 2) == Decimal("350000")

    def test_monthly_average(self):
        assert monthly_average(3000000, 3) == Decimal("1000000")

    def test_monthly_average_zero_months(self):
        assert monthly_average(1000, 0) == Decimal("0")


class TestLiquidity:
    def test_liquidity_ratio(self):
        assert liquidity_ratio(5000000, 1000000) == Decimal("5")

    def test_liquidity_zero_expense(self):
        assert liquidity_ratio(5000000, 0) == Decimal("0")

    def test_classify_excellent(self):
        assert classify_liquidity(Decimal("7")) == "Excelente"

    def test_classify_good(self):
        assert classify_liquidity(Decimal("4")) == "Buena"

    def test_classify_acceptable(self):
        assert classify_liquidity(Decimal("2")) == "Aceptable"

    def test_classify_critical(self):
        assert classify_liquidity(Decimal("0.5")) == "Crítica"


class TestBudgets:
    def test_budget_consumption(self):
        assert budget_consumption(160000, 200000) == Decimal("80")

    def test_budget_consumption_exceeded(self):
        assert budget_consumption(300000, 200000) == Decimal("100")

    def test_budget_alert_level_none(self):
        assert budget_alert_level(Decimal("50")) == 0

    def test_budget_alert_level_80(self):
        assert budget_alert_level(Decimal("85")) == 80

    def test_budget_alert_level_90(self):
        assert budget_alert_level(Decimal("95")) == 90

    def test_budget_alert_level_100(self):
        assert budget_alert_level(Decimal("100")) == 100

    def test_budget_alert_level_120(self):
        assert budget_alert_level(Decimal("130")) == 120


class TestGoals:
    def test_goal_progress(self):
        assert goal_progress(4500000, 10000000) == Decimal("45")

    def test_goal_progress_zero_target(self):
        assert goal_progress(1000, 0) == Decimal("0")

    def test_goal_progress_over(self):
        assert goal_progress(12000, 10000) == Decimal("100")

    def test_goal_forecast_months(self):
        assert goal_forecast_months(4500000, 10000000, 500000) == 11

    def test_goal_forecast_months_completed(self):
        assert goal_forecast_months(10000000, 10000000, 500000) == 0

    def test_goal_forecast_months_no_savings(self):
        assert goal_forecast_months(0, 1000000, 0) == -1

    def test_goal_on_track_on_schedule(self):
        created = date(2026, 1, 1)
        target = date(2026, 12, 31)
        today = date(2026, 7, 1)
        # Mitad del tiempo con 60% de progreso -> en curso
        assert goal_on_track(600000, 1000000, target, created, today) is True

    def test_goal_on_track_behind(self):
        created = date(2026, 1, 1)
        target = date(2026, 12, 31)
        today = date(2026, 7, 1)
        # Mitad del tiempo con 10% de progreso -> atrasada
        assert goal_on_track(100000, 1000000, target, created, today) is False

    def test_goal_on_track_no_target_date_passes(self):
        # Sin fecha objetivo, se considera en curso si ya alcanzó
        assert goal_on_track(1000000, 1000000, date(2026, 1, 1), date(2025, 1, 1)) is True


class TestScores:
    def test_debt_score_no_debt(self):
        assert debt_score(0, 0) == Decimal("100")

    def test_debt_score_penalized(self):
        assert debt_score(3, 5000000, 60) < Decimal("100")

    def test_debt_score_floor(self):
        assert debt_score(100, 1000000000, 3600) >= Decimal("0")

    def test_financial_score_perfect(self):
        score = financial_score(
            savings_rate=Decimal("100"),
            budget_consumption=Decimal("0"),
            debt=Decimal("100"),
            liquidity=Decimal("10"),
            goals=Decimal("100"),
            cash_flow=Decimal("500000"),
        )
        assert score == Decimal("100")

    def test_financial_score_zero(self):
        score = financial_score(
            savings_rate=Decimal("0"),
            budget_consumption=Decimal("200"),
            debt=Decimal("0"),
            liquidity=Decimal("0"),
            goals=Decimal("0"),
            cash_flow=Decimal("-5000000"),
        )
        assert score == Decimal("0")

    def test_financial_score_deterministic(self):
        a = financial_score(Decimal("30"), Decimal("70"), Decimal("80"), Decimal("3"), Decimal("50"), Decimal("100000"))
        b = financial_score(Decimal("30"), Decimal("70"), Decimal("80"), Decimal("3"), Decimal("50"), Decimal("100000"))
        assert a == b

    def test_score_grade_excellent(self):
        assert score_grade(Decimal("95")) == "Excelente"

    def test_score_grade_good(self):
        assert score_grade(Decimal("80")) == "Bueno"

    def test_score_grade_regular(self):
        assert score_grade(Decimal("65")) == "Regular"

    def test_score_grade_critical(self):
        assert score_grade(Decimal("40")) == "Crítico"


class TestHealth:
    def test_financial_health_shape(self):
        result = financial_health(
            Decimal("30"), Decimal("70"), Decimal("80"), Decimal("3"), Decimal("50"), Decimal("100000")
        )
        assert 0 <= result["score"] <= 100
        assert result["status"] in ["Excelente", "Bueno", "Regular", "Crítico"]
        assert "components" in result

    def test_financial_health_excellent(self):
        result = financial_health(
            Decimal("100"), Decimal("0"), Decimal("100"), Decimal("10"), Decimal("100"), Decimal("500000")
        )
        assert result["status"] == "Excelente"


class TestForecasts:
    def test_year_projection(self):
        result = year_projection(6000000, 3600000, start_month=6, year=2026)
        assert result["months_remaining"] == 6
        assert result["projected_income"] > Decimal("6000000")
        assert result["projected_expense"] > Decimal("3600000")

    def test_forecast_balance(self):
        assert forecast_balance(500000, 200000, 3) == Decimal("1100000")

    def test_forecast_balance_negative_months(self):
        assert forecast_balance(500000, 200000, -1) == Decimal("0")


class TestPredictions:
    def test_savings_forecast(self):
        predictions = savings_forecast(3000000, 2500000, months_ahead=3)
        assert len(predictions) == 3
        assert predictions[0]["month"] == 1
        assert predictions[0]["predicted_savings"] == 500000.0
        assert predictions[2]["cumulative_savings"] == 1500000.0

    def test_savings_forecast_negative(self):
        assert savings_forecast(1000, 2000, months_ahead=3) == []

    def test_goal_completion_forecast(self):
        result = goal_completion_forecast(4500000, 10000000, 500000)
        assert result["months_remaining"] == 11
        assert result["estimated_date"] is not None

    def test_goal_completion_forecast_no_savings(self):
        result = goal_completion_forecast(0, 1000000, 0)
        assert result["months_remaining"] == -1
        assert result["estimated_date"] is None


class TestTrends:
    def test_spending_trend_increasing(self):
        assert spending_trend(Decimal("1300000"), Decimal("1000000")) == "Creciente"

    def test_spending_trend_stable(self):
        assert spending_trend(Decimal("1050000"), Decimal("1000000")) == "Estable"

    def test_spending_trend_decreasing(self):
        assert spending_trend(Decimal("800000"), Decimal("1000000")) == "Decreciente"

    def test_category_dominance(self):
        assert category_dominance(380000, 1000000) == Decimal("38")

    def test_top_categories(self):
        result = top_categories({"Comida": Decimal("380000"), "Transporte": Decimal("120000")})
        assert result[0]["category"] == "Comida"
        assert result[0]["percentage"] == 76.0

    def test_top_categories_empty(self):
        assert top_categories({}) == []


class TestCouple:
    def test_couple_balance_index_equal(self):
        assert couple_balance_index(500000, 500000, 0, 0) == Decimal("100")

    def test_couple_balance_index_unbalanced(self):
        assert couple_balance_index(900000, 100000, 0, 0) < Decimal("100")

    def test_couple_balance_index_no_data(self):
        assert couple_balance_index(0, 0, 0, 0) == Decimal("50")
