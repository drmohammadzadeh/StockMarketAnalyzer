"""Tests for Research Directory Storage, Provenance Tracker, and Audit Logger."""

import json
import os
import pandas as pd
import pytest
from stock_analyzer.core.storage import ResearchStorage
from stock_analyzer.core.provenance import ProvenanceTracker
from stock_analyzer.core.audit import AuditLogger
from stock_analyzer.core.models import ProvenanceRecord

def test_research_storage_scaffolding(tmp_path):
    storage = ResearchStorage(base_dir=tmp_path)
    dirs = storage.init_research_dirs("AAPL")
    
    # Verify key directories from the 25 required folders exist
    assert os.path.exists(dirs["00_identity"])
    assert os.path.exists(dirs["01_raw_market_data"])
    assert os.path.exists(dirs["02_normalized_market_data"])
    assert os.path.exists(dirs["04_filings"])
    assert os.path.exists(dirs["12_fundamental_analysis"])
    assert os.path.exists(dirs["21_scores"])
    assert os.path.exists(dirs["23_final_report"])
    assert os.path.exists(dirs["24_audit"])

def test_save_and_load_parquet(tmp_path):
    storage = ResearchStorage(base_dir=tmp_path)
    df = pd.DataFrame([{"close": 150.0, "volume": 1000, "date": "2026-01-01"}])
    path = storage.save_parquet("AAPL", "02_normalized_market_data", "daily_ohlcv.parquet", df)
    assert os.path.exists(path)
    
    loaded_df = storage.load_parquet(path)
    assert len(loaded_df) == 1
    assert loaded_df["close"].iloc[0] == 150.0

def test_audit_logger(tmp_path):
    storage = ResearchStorage(base_dir=tmp_path)
    dirs = storage.init_research_dirs("AAPL")
    audit_file = os.path.join(dirs["24_audit"], "audit_log.json")
    
    logger = AuditLogger(audit_file)
    logger.log_event("TEST_EVENT", {"detail": "sample event message"})
    
    assert os.path.exists(audit_file)
    with open(audit_file, "r", encoding="utf-8") as f:
        events = json.load(f)
    assert len(events) == 1
    assert events[0]["event_type"] == "TEST_EVENT"

def test_provenance_tracker():
    tracker = ProvenanceTracker()
    rec = tracker.create_record(
        provider="sec_edgar",
        endpoint="xbrl",
        symbol="AAPL",
        source_time="2026-02-05T00:00:00Z",
        url="https://sec.gov",
    )
    assert rec.symbol == "AAPL"
    assert rec.provider == "sec_edgar"
    tracker.register(rec)
    records = tracker.get_records_for_symbol("AAPL")
    assert len(records) == 1
