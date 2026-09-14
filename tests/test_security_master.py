"""Tests for Canonical Security Master and Ticker Resolution."""

import pytest
from stock_analyzer.core.security_master import SecurityMaster

def test_resolve_us_securities():
    sm = SecurityMaster()
    aapl = sm.resolve("AAPL")
    assert aapl.canonical_ticker == "AAPL"
    assert aapl.country == "US"
    assert aapl.currency == "USD"
    assert aapl.exchange in ["NASDAQ", "Nasdaq"]
    assert aapl.cik == "0000320193"
    assert aapl.primary_listing is True

    msft = sm.resolve("MSFT")
    assert msft.canonical_ticker == "MSFT"
    assert msft.country == "US"
    assert msft.currency == "USD"
    assert msft.cik == "0000789019"

def test_resolve_canadian_and_cross_listed_securities():
    sm = SecurityMaster()
    shop_ca = sm.resolve("SHOP.TO")
    assert shop_ca.canonical_ticker == "SHOP.TO"
    assert shop_ca.country == "CA"
    assert shop_ca.currency == "CAD"
    assert shop_ca.exchange == "TSX"
    assert shop_ca.cross_listed_ticker == "SHOP"
    assert shop_ca.cross_listed_exchange == "NYSE"

    ry_ca = sm.resolve("RY.TO")
    assert ry_ca.canonical_ticker == "RY.TO"
    assert ry_ca.country == "CA"
    assert ry_ca.currency == "CAD"
    assert ry_ca.exchange == "TSX"

def test_resolve_unknown_ticker():
    sm = SecurityMaster()
    res = sm.resolve("XYZ999")
    assert res.canonical_ticker == "XYZ999"
    assert res.country == "US"
    assert res.currency == "USD"
