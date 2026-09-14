"""Tests for Source Registry and Configuration Loader."""

import os
import pytest
from stock_analyzer.core.config import ConfigLoader

def test_load_authoritative_config():
    loader = ConfigLoader()
    cfg = loader.load_main_config()
    assert cfg["config_version"] == "1.0"
    assert "sources" in cfg
    assert "source_priority" in cfg

def test_source_registry_resolution():
    loader = ConfigLoader()
    registry = loader.get_source_registry()
    sources = registry.get_sources_for_capability("real_time_quotes")
    assert len(sources) > 0
    # First source has lowest numerical priority (1 is higher than 6)
    assert sources[0].priority <= sources[-1].priority

def test_secret_detection(monkeypatch):
    monkeypatch.setenv("POLYGON_API_KEY", "dummy_poly_key")
    loader = ConfigLoader()
    registry = loader.get_source_registry()
    poly = registry.get_source("polygon")
    assert poly is not None
    assert poly.is_authenticated() is True
