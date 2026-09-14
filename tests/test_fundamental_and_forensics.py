"""Tests for Fundamental and Forensic Accounting Engines."""

import pytest
from stock_analyzer.engine.fundamental import FundamentalEngine
from stock_analyzer.engine.forensics import ForensicsEngine

def test_fundamental_ratios():
    engine = FundamentalEngine()
    metrics = engine.compute_metrics(
        revenue_current=391035000000,
        revenue_prior=383285000000,
        net_income=93736000000,
        operating_cash_flow=118265000000,
        capex=9450000000,
        total_debt=85750000000,
        cash_and_equiv=29943000000,
        total_equity=66782000000,
        operating_income=123216000000,
    )
    
    assert "revenue_growth_yoy" in metrics
    assert metrics["revenue_growth_yoy"] > 0
    assert "free_cash_flow" in metrics
    # FCF = CFO - CapEx = 118.265B - 9.45B = 108.815B
    assert abs(metrics["free_cash_flow"] - 108815000000) < 1e6
    assert "roic" in metrics
    assert metrics["roic"] > 0.30

def test_piotroski_f_score_and_altman_z():
    forensics = ForensicsEngine()
    data = {
        "net_income": 93736000000,
        "operating_cash_flow": 118265000000,
        "total_assets_current": 364980000000,
        "total_assets_prior": 352583000000,
        "long_term_debt_current": 85750000000,
        "long_term_debt_prior": 95281000000,
        "current_assets": 153000000000,
        "current_liabilities": 145000000000,
        "retained_earnings": -15000000000,
        "ebit": 123216000000,
        "market_cap": 3000000000000,
        "total_liabilities": 298000000000,
        "sales": 391035000000,
        "shares_current": 15200000000,
        "shares_prior": 15500000000,
        "gross_margin_current": 0.46,
        "gross_margin_prior": 0.44,
        "current_ratio_current": 1.05,
        "current_ratio_prior": 0.98,
    }

    f_score, breakdown = forensics.compute_piotroski_f_score(data)
    assert 0 <= f_score <= 9
    assert isinstance(breakdown, dict)

    z_score, status = forensics.compute_altman_z_score(data)
    assert z_score > 0
    assert status in ["Safe Zone", "Grey Zone", "Distress Zone"]

    accruals = forensics.compute_sloan_accruals(
        net_income=data["net_income"],
        operating_cash_flow=data["operating_cash_flow"],
        total_assets=data["total_assets_current"],
    )
    assert isinstance(accruals, float)
