"""Tests for Data Provider Adapters."""

import pytest
import pandas as pd
from stock_analyzer.providers.base import BaseProvider
from stock_analyzer.providers.edgar import EdgarProvider
from stock_analyzer.providers.open_market import OpenMarketProvider
from stock_analyzer.providers.fred import FredProvider
from stock_analyzer.providers.gdelt import GdeltProvider
from stock_analyzer.providers.sedar import SedarProvider

def test_edgar_provider_headers():
    edgar = EdgarProvider(user_agent="StockMarketAnalyzer research@analyzer.local")
    headers = edgar.get_headers()
    assert "User-Agent" in headers
    assert "research@analyzer.local" in headers["User-Agent"]

def test_edgar_provider_mock_facts():
    edgar = EdgarProvider()
    facts, prov = edgar.get_company_facts("0000320193", symbol="AAPL")
    assert "facts" in facts
    assert prov.provider == "sec_edgar"
    assert prov.symbol == "AAPL"

def test_open_market_provider():
    omp = OpenMarketProvider()
    # Offline / mock-tolerant fetch for testing
    df_adj, df_unadj, prov = omp.get_historical_ohlcv("AAPL", bars=252)
    assert len(df_adj) >= 252
    assert "close" in df_adj.columns
    assert "open" in df_adj.columns
    assert prov.provider in ["open_market", "yfinance"]

def test_fred_provider():
    fred = FredProvider()
    macro, prov = fred.get_macro_snapshot()
    assert "fed_funds_rate" in macro
    assert "cpi_yoy" in macro
    assert "treasury_10y_yield" in macro
    assert prov.provider == "fred"

def test_gdelt_provider():
    gdelt = GdeltProvider()
    sentiment, prov = gdelt.get_news_sentiment("AAPL", "Apple Inc.")
    assert "tone" in sentiment
    assert "article_count" in sentiment
    assert prov.provider == "gdelt"

def test_sedar_provider():
    sedar = SedarProvider()
    filings, prov = sedar.get_filings("SHOP.TO")
    assert len(filings) > 0
    assert prov.provider == "sedar_plus"
