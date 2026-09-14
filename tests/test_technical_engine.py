"""Tests for Technical Indicator and Volatility Engine."""

import numpy as np
import pandas as pd
import pytest
from stock_analyzer.engine.technical import TechnicalEngine

def test_technical_engine_all_indicators():
    engine = TechnicalEngine()
    
    # 260 bars of synthetic trend
    dates = pd.date_range("2025-01-01", periods=260, freq="B")
    prices = np.linspace(150, 220, 260)
    df = pd.DataFrame({
        "open": prices * 0.99,
        "high": prices * 1.02,
        "low": prices * 0.98,
        "close": prices,
        "volume": np.full(260, 50000000),
    }, index=dates)

    indicators = engine.compute_all_indicators(df)
    
    # Check trend indicators
    assert "SMA_20" in indicators
    assert "SMA_50" in indicators
    assert "SMA_200" in indicators
    assert "EMA_20" in indicators
    assert "ADX_14" in indicators

    # Check momentum
    assert "RSI_14" in indicators
    assert 0 <= indicators["RSI_14"] <= 100
    assert "MACD_line" in indicators
    assert "MACD_signal" in indicators
    assert "MACD_hist" in indicators
    assert "ROC_20" in indicators

    # Check volatility
    assert "ATR_14" in indicators
    assert "BB_upper" in indicators
    assert "BB_lower" in indicators
    assert "BB_middle" in indicators
    assert "realized_vol_20" in indicators

    # Check volume
    assert "RVOL_20" in indicators
    assert "VWAP" in indicators
    assert "OBV" in indicators

def test_support_and_resistance():
    engine = TechnicalEngine()
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    prices = 100 + 10 * np.sin(np.linspace(0, 10, 100))
    df = pd.DataFrame({
        "high": prices + 2,
        "low": prices - 2,
        "close": prices,
        "volume": np.full(100, 1000000),
    }, index=dates)

    levels = engine.detect_support_resistance(df)
    assert "support_level" in levels
    assert "resistance_level" in levels
    assert levels["resistance_level"] >= levels["support_level"]
