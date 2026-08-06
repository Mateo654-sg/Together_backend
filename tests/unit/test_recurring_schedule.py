"""
Tests unitarios del programador de recurrencias (FR-033).
"""

from datetime import date

import pytest

from app.core.exceptions import ValidationException
from app.use_cases.recurring.schedule import next_execution_date


class TestNextExecutionDate:
    def test_daily(self):
        assert next_execution_date("daily", date(2026, 8, 5)) == date(2026, 8, 6)

    def test_daily_crosses_month(self):
        assert next_execution_date("daily", date(2026, 8, 31)) == date(2026, 9, 1)

    def test_weekly(self):
        assert next_execution_date("weekly", date(2026, 8, 5)) == date(2026, 8, 12)

    def test_monthly(self):
        assert next_execution_date("monthly", date(2026, 8, 10)) == date(2026, 9, 10)

    def test_monthly_crosses_year(self):
        assert next_execution_date("monthly", date(2026, 12, 10)) == date(2027, 1, 10)

    def test_monthly_clamps_invalid_day(self):
        # 31 de enero -> 28 de febrero
        assert next_execution_date("monthly", date(2026, 1, 31)) == date(2026, 2, 28)

    def test_annual(self):
        assert next_execution_date("annual", date(2026, 8, 5)) == date(2027, 8, 5)

    def test_annual_leap_day_clamped(self):
        assert next_execution_date("annual", date(2024, 2, 29)) == date(2025, 2, 28)

    def test_invalid_frequency(self):
        with pytest.raises(ValidationException):
            next_execution_date("hourly", date(2026, 8, 5))
