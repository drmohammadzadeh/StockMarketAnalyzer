"""Tests for Valuation Models (DCF, Reverse DCF, Graham, Relative)."""

import pytest
from stock_analyzer.engine.valuation import ValuationEngine

def test_graham_number():
    engine = ValuationEngine()
    graham = engine.compute_graham_number(eps=6.5, bvps=25.0)
    # sqrt(22.5 * 6.5 * 25) = sqrt(3656.25) ~ 60.46
    assert abs(graham - 60.47) < 0.1

def test_dcf_model_and_sensitivity():
    engine = ValuationEngine()
    res = engine.compute_dcf(
        base_fcf=108000000000,
        growth_rate=0.07,
        wacc=0.085,
        terminal_growth=0.025,
        shares_outstanding=15200000000,
        net_debt=55000000000,
    )
    assert res["intrinsic_value_per_share"] > 0
    assert "sensitivity_matrix" in res
    assert len(res["sensitivity_matrix"]) == 5
    assert len(res["sensitivity_matrix"][0]) == 5

def test_reverse_dcf():
    engine = ValuationEngine()
    implied_g = engine.compute_reverse_dcf(
        current_price=220.0,
        base_fcf=108000000000,
        wacc=0.085,
        shares_outstanding=15200000000,
        net_debt=55000000000,
    )
    assert -0.20 <= implied_g <= 0.50

def test_relative_valuation_peer_percentiles():
    engine = ValuationEngine()
    # Mock peer P/E multiples
    peers = [18.0, 22.0, 25.0, 28.0, 30.0, 35.0, 42.0, 50.0]
    percentile, discount = engine.compute_peer_percentile(company_multiple=24.0, peer_multiples=peers)
    assert 0 <= percentile <= 100
    assert discount > 0  # 24 is below median of ~29
