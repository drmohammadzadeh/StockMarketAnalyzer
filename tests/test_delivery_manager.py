"""Tests for Delivery Manager and Report Generation Engine."""

import pytest
from stock_analyzer.agents.delivery_manager import DeliveryManager
from stock_analyzer.core.models import ScoringResult, ProvenanceRecord

def test_report_generation():
    manager = DeliveryManager()
    scores = ScoringResult(
        sub_scores={
            "fundamental": 8.5,
            "technical": 7.0,
            "risk": 8.0,
            "sentiment": 6.5,
            "valuation": 6.0,
            "growth": 7.5,
            "quality": 9.0,
            "business_strength": 9.0,
            "management": 8.0,
            "catalyst": 7.0,
            "event_risk": 8.0,
        },
        base_ai_score=7.70,
        extended_ai_score=7.65,
        normalized_100_score=74.4,
        confidence_score=0.90,
        penalties={},
    )

    prov = ProvenanceRecord(
        provider="sec_edgar",
        dataset_or_endpoint="xbrl",
        source_timestamp_utc="2026-02-05T00:00:00Z",
        retrieved_at_utc="2026-09-14T00:00:00Z",
        symbol="AAPL",
        provider_record_id_or_url="https://sec.gov",
    )

    report_md, plain_md, report_json = manager.generate_reports(
        symbol="AAPL",
        company_name="Apple Inc.",
        scores=scores,
        specialist_outputs={},
        provenance_records=[prov],
    )

    # 1. Check required 18 report sections in report_md
    assert "# Apple Inc. (AAPL) — AI Equity Research Report" in report_md
    assert "## 1. Executive Summary" in report_md
    assert "## 2. Scorecard" in report_md
    assert "## 3. Company Overview" in report_md
    assert "## 4. Fundamental Analysis" in report_md
    assert "## 5. Valuation" in report_md
    assert "## 6. Technical Analysis" in report_md
    assert "## 7. Sentiment Analysis" in report_md
    assert "## 8. Risk Analysis" in report_md
    assert "## 9. Business and Competitive Analysis" in report_md
    assert "## 10. Management and Ownership" in report_md
    assert "## 11. Catalysts" in report_md
    assert "## 12. Bull Case" in report_md
    assert "## 13. Bear Case" in report_md
    assert "## 14. Base Case" in report_md
    assert "## 15. Key Invalidation Conditions" in report_md
    assert "## 16. Final Assessment" in report_md
    assert "## 17. Sources" in report_md
    assert "## 18. Disclaimer" in report_md

    # 2. Check Plain English summary
    assert "## In Plain English" in plain_md
    assert "What the company does" in plain_md
    assert "Why investors may like it" in plain_md
    assert "What to watch next" in plain_md

    # 3. Check JSON structure
    assert report_json["symbol"] == "AAPL"
    assert report_json["base_ai_score"] == 7.70
