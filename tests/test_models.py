"""Unit tests for Pydantic core data models and contracts."""

from stock_analyzer.core.models import (
    ProvenanceRecord,
    SecurityIdentity,
    AgentTask,
    AgentOutput,
    JudgeReview,
    ChiefReviewOutput,
    ScoringResult,
    GateResult,
)

def test_provenance_record_serialization():
    rec = ProvenanceRecord(
        provider="sec_edgar",
        dataset_or_endpoint="xbrl/companyfacts",
        source_timestamp_utc="2026-02-05T21:00:00Z",
        retrieved_at_utc="2026-09-14T09:00:00Z",
        market_session="closed",
        symbol="AAPL",
        currency="USD",
        adjustment_status="unadjusted",
        request_parameters={"cik": "0000320193"},
        provider_record_id_or_url="https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
    )
    assert rec.provider == "sec_edgar"
    assert rec.currency == "USD"
    data = rec.model_dump()
    assert data["adjustment_status"] == "unadjusted"

def test_security_identity():
    sec = SecurityIdentity(
        canonical_ticker="AAPL",
        exchange="NASDAQ",
        country="US",
        currency="USD",
        company_name="Apple Inc.",
        cik="0000320193",
        figi="BBG000B9XRY4",
        isin="US0378331005",
        primary_listing=True,
        asset_type="stock",
        sector="Technology",
        industry="Consumer Electronics",
    )
    assert sec.canonical_ticker == "AAPL"
    assert sec.country == "US"

def test_scoring_result_contracts():
    res = ScoringResult(
        sub_scores={"fundamental": 8.0, "technical": 7.5, "risk": 8.2},
        base_ai_score=7.8,
        extended_ai_score=7.75,
        normalized_100_score=75.5,
        confidence_score=0.85,
        penalties={"insufficient_history": 0.15},
    )
    assert res.base_ai_score == 7.8
    assert res.confidence_score == 0.85
