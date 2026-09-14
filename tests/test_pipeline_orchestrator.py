"""Tests for Pipeline Orchestrator and CLI runner."""

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

@pytest.mark.asyncio
async def test_canadian_security_pipeline(tmp_path):
    orchestrator = ResearchOrchestrator(base_dir=tmp_path)
    result = await orchestrator.run("SHOP.TO")
    assert result["status"] == "COMPLETE"
    assert result["symbol"] == "SHOP.TO"
    assert result["currency"] == "CAD"
    assert (tmp_path / "SHOP.TO" / "README.md").exists()
