"""Tests for Pipeline Orchestrator and CLI runner."""

import json
import os
import pytest
from stock_analyzer.pipeline.orchestrator import ResearchOrchestrator

@pytest.mark.asyncio
async def test_pipeline_orchestrator_execution(tmp_path):
    orchestrator = ResearchOrchestrator(base_dir=tmp_path)
    result = await orchestrator.run("AAPL", horizon="6-12 months")
    
    assert result["status"] == "COMPLETE"
    assert result["symbol"] == "AAPL"
    assert "scores" in result
    assert result["scores"].base_ai_score > 0
    assert result["scores"].confidence_score > 0

    # Verify research folders created in tmp_path
    aapl_dir = tmp_path / "AAPL"
    assert (aapl_dir / "00_identity").exists()
    assert (aapl_dir / "02_normalized_market_data").exists()
    assert (aapl_dir / "README.md").exists()
    assert (aapl_dir / "23_final_report" / "report.md").exists()
    assert (aapl_dir / "23_final_report" / "plain_english.md").exists()
    assert (aapl_dir / "24_audit" / "audit_log.json").exists()

    # Verify all 6 visual assets exist in assets/
    assets_dir = aapl_dir / "assets"
    assert (assets_dir / "radar_score_chart.png").exists()
    assert (assets_dir / "technical_gauges.png").exists()
    assert (assets_dir / "price_action_trend.png").exists()
    assert (assets_dir / "financial_conversion_bars.png").exists()
    assert (assets_dir / "valuation_margin_gauge.png").exists()
    assert (assets_dir / "business_moat_diagram.png").exists()
    assert (assets_dir / "business_moat_diagram.excalidraw").exists()

    # Verify audit event for CHARTS_GENERATED
    with open(aapl_dir / "24_audit" / "audit_log.json", "r", encoding="utf-8") as f:
        audit_events = json.load(f)
    chart_event = next((ev for ev in audit_events if ev.get("event_type") == "CHARTS_GENERATED"), None)
    assert chart_event is not None
    charts = chart_event.get("details", {}).get("charts", [])
    assert "radar_score_chart.png" in charts
    assert "technical_gauges.png" in charts
    assert "price_action_trend.png" in charts
    assert "financial_conversion_bars.png" in charts
    assert "valuation_margin_gauge.png" in charts
    assert "business_moat_diagram.png" in charts
    assert "business_moat_diagram.excalidraw" in charts

@pytest.mark.asyncio
async def test_canadian_security_pipeline(tmp_path):
    orchestrator = ResearchOrchestrator(base_dir=tmp_path)
    result = await orchestrator.run("SHOP.TO")
    assert result["status"] == "COMPLETE"
    assert result["symbol"] == "SHOP.TO"
    assert result["currency"] == "CAD"
    shop_dir = tmp_path / "SHOP.TO"
    assert (shop_dir / "README.md").exists()
    shop_assets = shop_dir / "assets"
    assert (shop_assets / "radar_score_chart.png").exists()
    assert (shop_assets / "technical_gauges.png").exists()
    assert (shop_assets / "price_action_trend.png").exists()
    assert (shop_assets / "financial_conversion_bars.png").exists()
    assert (shop_assets / "valuation_margin_gauge.png").exists()
    assert (shop_assets / "business_moat_diagram.png").exists()
    assert (shop_assets / "business_moat_diagram.excalidraw").exists()
