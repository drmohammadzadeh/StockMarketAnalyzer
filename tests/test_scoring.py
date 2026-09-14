"""Tests for Scoring Engine and Confidence Penalties."""

import pytest
from stock_analyzer.engine.scoring import ScoringEngine

def test_scoring_weights_and_confidence():
    engine = ScoringEngine()
    
    sub_scores = {
        "fundamental": 8.0,
        "technical": 7.0,
        "sentiment": 6.0,
        "macro_event_risk": 7.5,
        "risk": 8.5,
        "valuation": 6.5,
        "growth": 7.5,
        "quality": 8.5,
        "business_strength": 9.0,
        "management": 8.0,
        "catalyst": 7.0,
        "event_risk": 8.0,
    }
    
    # 0.40*8.0 + 0.35*7.0 + 0.15*6.0 + 0.10*7.5 = 3.20 + 2.45 + 0.90 + 0.75 = 7.30
    penalties = {"insufficient_history": 0.20}
    res = engine.calculate_scores(sub_scores, penalties)

    assert abs(res.base_ai_score - 7.30) < 1e-4
    assert abs(res.confidence_score - 0.80) < 1e-4
    # Normalized 100: (7.30 - 1.0) / 9.0 * 100 = 6.30 / 9 * 100 = 70.0
    assert abs(res.normalized_100_score - 70.0) < 1e-4
    assert res.sub_scores["risk"] == 8.5

def test_confidence_floor():
    engine = ScoringEngine()
    sub_scores = {"fundamental": 5.0, "technical": 5.0, "sentiment": 5.0, "macro_event_risk": 5.0}
    # Massive penalties
    penalties = {
        "stale_data": 0.30,
        "missing_primary_source": 0.25,
        "unresolved_source_conflict": 0.25,
        "insufficient_history": 0.20,
        "low_sentiment_sample": 0.15,
    }
    res = engine.calculate_scores(sub_scores, penalties)
    assert res.confidence_score >= 0.0
    assert res.confidence_score <= 0.05
