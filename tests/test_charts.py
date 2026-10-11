import numpy as np
import pandas as pd
from pathlib import Path
import pytest

from stock_analyzer.engine.charts import (
    generate_financial_waterfall_chart,
    generate_price_action_chart,
    generate_valuation_margin_chart,
)



def test_generate_price_action_chart(tmp_path: Path):
    dates = pd.date_range("2025-01-01", periods=252, freq="B")
    np.random.seed(42)
    prices = 150.0 + np.cumsum(np.random.randn(252) * 2.0)
    df = pd.DataFrame(
        {
            "close": prices,
            "volume": np.random.randint(1000000, 5000000, size=252),
        },
        index=dates,
    )

    out_file = tmp_path / "price_action_trend.png"
    result = generate_price_action_chart(df, "TEST", "Test Corp", out_file)
    assert result.exists()
    assert result == out_file
    assert result.stat().st_size > 5000


def test_generate_price_action_chart_missing_close_raises(tmp_path: Path):
    df = pd.DataFrame({"open": [1, 2, 3]})
    out_file = tmp_path / "price_action_trend.png"
    with pytest.raises(ValueError, match="DataFrame must contain 'close' column"):
        generate_price_action_chart(df, "TEST", "Test Corp", out_file)


def test_generate_price_action_chart_without_volume(tmp_path: Path):
    dates = pd.date_range("2025-01-01", periods=50, freq="B")
    df = pd.DataFrame({"close": np.linspace(100, 150, 50)}, index=dates)
    out_file = tmp_path / "no_volume.png"
    result = generate_price_action_chart(df, "TEST", "Test Corp", out_file)
    assert result.exists()
    assert result.stat().st_size > 1000


def test_generate_financial_waterfall_chart(tmp_path: Path):
    data = {
        "revenue": 716924000000.0,
        "operating_income": 79975000000.0,
        "net_income": 77670000000.0,
        "operating_cash_flow": 139514000000.0,
        "free_cash_flow": 132777000000.0,
    }
    out_file = tmp_path / "financial_conversion_bars.png"
    result = generate_financial_waterfall_chart(data, "AMZN", "Amazon.com, Inc.", out_file)
    assert result.exists()
    assert result == out_file
    assert result.stat().st_size > 5000


def test_generate_financial_waterfall_chart_zero_and_missing_values(tmp_path: Path):
    # Empty dictionary test
    data_empty: dict[str, float] = {}
    out_file_empty = tmp_path / "financial_empty.png"
    result_empty = generate_financial_waterfall_chart(data_empty, "EMPTY", "Empty Corp", out_file_empty)
    assert result_empty.exists()
    assert result_empty == out_file_empty
    assert result_empty.stat().st_size > 1000

    # Partial, zero, and negative values test
    data_partial = {
        "revenue": 10000000000.0,
        "operating_income": -2000000000.0,
        "net_income": -3000000000.0,
        "operating_cash_flow": 500000000.0,
        # free_cash_flow missing
    }
    out_file_partial = tmp_path / "financial_partial.png"
    result_partial = generate_financial_waterfall_chart(data_partial, "PART", "Partial Corp", out_file_partial)
    assert result_partial.exists()
    assert result_partial == out_file_partial
    assert result_partial.stat().st_size > 1000


def test_generate_valuation_margin_chart_premium(tmp_path: Path):
    data = {
        "current_price": 262.43,
        "intrinsic_value": 229.22,
        "graham_number": 78.60,
        "fifty_two_week_low": 165.0,
        "fifty_two_week_high": 275.0,
    }
    out_file = tmp_path / "valuation_premium.png"
    result = generate_valuation_margin_chart(data, "AMZN", "Amazon.com, Inc.", out_file)
    assert result.exists()
    assert result == out_file
    assert result.stat().st_size > 5000


def test_generate_valuation_margin_chart_discount(tmp_path: Path):
    data = {
        "current_price": 100.0,
        "intrinsic_value_per_share": 135.0,
        "graham_number": 95.0,
        "fifty_two_week_low": 80.0,
        "fifty_two_week_high": 120.0,
    }
    out_file = tmp_path / "valuation_discount.png"
    result = generate_valuation_margin_chart(data, "GOOGL", "Alphabet Inc.", out_file)
    assert result.exists()
    assert result == out_file
    assert result.stat().st_size > 5000


def test_generate_valuation_margin_chart_missing_optional_keys(tmp_path: Path):
    # Minimal data: only current_price and intrinsic_value, omitting 52w bounds and graham floor
    data_minimal = {
        "current_price": 150.0,
        "intrinsic_value": 160.0,
    }
    out_file_minimal = tmp_path / "valuation_minimal.png"
    result_minimal = generate_valuation_margin_chart(data_minimal, "AAPL", "Apple Inc.", out_file_minimal)
    assert result_minimal.exists()
    assert result_minimal == out_file_minimal
    assert result_minimal.stat().st_size > 3000

    # Completely empty dictionary
    out_file_empty = tmp_path / "valuation_empty.png"
    result_empty = generate_valuation_margin_chart({}, "EMPTY", "Empty Corp", out_file_empty)
    assert result_empty.exists()
    assert result_empty == out_file_empty
    assert result_empty.stat().st_size > 3000

