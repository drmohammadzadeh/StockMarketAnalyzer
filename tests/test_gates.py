"""Tests for Data Quality Gates (Gate 1 to Gate 4) and Veto Logic."""

import pandas as pd
import pytest
from stock_analyzer.core.models import SecurityIdentity
from stock_analyzer.pipeline.gates import QualityGateEngine

def test_gate1_identity_verification():
    engine = QualityGateEngine()
    valid_sec = SecurityIdentity(
        canonical_ticker="AAPL",
        exchange="NASDAQ",
        country="US",
        currency="USD",
        company_name="Apple Inc.",
    )
    res = engine.evaluate_gate1_identity(valid_sec)
    assert res.passed is True
    assert res.gate_id == "GATE_1_IDENTITY"

def test_gate2_market_data_bar_count():
    engine = QualityGateEngine()
    # Less than required 252 bars
    short_df = pd.DataFrame({"close": [150.0] * 50, "volume": [1000] * 50})
    res_short = engine.evaluate_gate2_market_data(short_df, required_bars=252)
    assert res_short.passed is False
    assert "insufficient" in res_short.details.lower()

    # Sufficient bars
    good_df = pd.DataFrame({"close": [150.0] * 252, "volume": [1000] * 252})
    res_good = engine.evaluate_gate2_market_data(good_df, required_bars=252)
    assert res_good.passed is True

def test_gate3_fundamentals_integrity():
    engine = QualityGateEngine()
    complete_facts = {
        "Revenues": [{"val": 1000000}],
        "NetIncomeLoss": [{"val": 200000}],
        "Assets": [{"val": 5000000}],
    }
    res = engine.evaluate_gate3_fundamentals(complete_facts)
    assert res.passed is True

    missing_facts = {"Revenues": [{"val": 1000000}]}
    res_fail = engine.evaluate_gate3_fundamentals(missing_facts)
    assert res_fail.passed is False

def test_gate4_data_quality_veto_negative_values():
    engine = QualityGateEngine()
    bad_df = pd.DataFrame({"close": [-10.0, 150.0], "volume": [1000, 2000]})
    res = engine.evaluate_gate4_data_quality(bad_df, filing_days_old=30)
    assert res.passed is False
    assert "negative" in res.details.lower()

def test_gate4_freshness_check():
    engine = QualityGateEngine()
    good_df = pd.DataFrame({"close": [150.0, 152.0], "volume": [1000, 2000]})
    # Stale fundamentals (> 120 days)
    res_stale = engine.evaluate_gate4_data_quality(good_df, filing_days_old=150)
    assert res_stale.passed is False
    assert "freshness" in res_stale.details.lower() or "stale" in res_stale.details.lower()
