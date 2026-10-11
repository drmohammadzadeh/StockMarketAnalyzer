import numpy as np
import pandas as pd
from pathlib import Path
import pytest

from stock_analyzer.engine.charts import generate_price_action_chart


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
