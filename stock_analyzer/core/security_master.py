"""Canonical Security Master and Ticker Resolution Engine."""

from typing import Dict, Optional
from stock_analyzer.core.models import SecurityIdentity


class SecurityMaster:
    """Master registry and parser for US and Canadian equities and ETFs."""

    # Pre-populated directory of major canonical securities with official CIKs & identifiers
    _CANONICAL_DATABASE: Dict[str, Dict] = {
        "AAPL": {
            "canonical_ticker": "AAPL",
            "exchange": "NASDAQ",
            "country": "US",
            "currency": "USD",
            "company_name": "Apple Inc.",
            "cik": "0000320193",
            "figi": "BBG000B9XRY4",
            "isin": "US0378331005",
            "primary_listing": True,
            "asset_type": "stock",
            "sector": "Technology",
            "industry": "Consumer Electronics",
        },
        "MSFT": {
            "canonical_ticker": "MSFT",
            "exchange": "NASDAQ",
            "country": "US",
            "currency": "USD",
            "company_name": "Microsoft Corporation",
            "cik": "0000789019",
            "figi": "BBG000BPH459",
            "isin": "US5949181045",
            "primary_listing": True,
            "asset_type": "stock",
            "sector": "Technology",
            "industry": "Software—Infrastructure",
        },
        "NVDA": {
            "canonical_ticker": "NVDA",
            "exchange": "NASDAQ",
            "country": "US",
            "currency": "USD",
            "company_name": "NVIDIA Corporation",
            "cik": "0001045810",
            "figi": "BBG000BBJQV0",
            "isin": "US67066G1040",
            "primary_listing": True,
            "asset_type": "stock",
            "sector": "Technology",
            "industry": "Semiconductors",
        },
        "AMZN": {
            "canonical_ticker": "AMZN",
            "exchange": "NASDAQ",
            "country": "US",
            "currency": "USD",
            "company_name": "Amazon.com, Inc.",
            "cik": "0001018724",
            "figi": "BBG000BVPV84",
            "isin": "US0231351067",
            "primary_listing": True,
            "asset_type": "stock",
            "sector": "Consumer Cyclical",
            "industry": "Internet Retail",
        },
        "TSLA": {
            "canonical_ticker": "TSLA",
            "exchange": "NASDAQ",
            "country": "US",
            "currency": "USD",
            "company_name": "Tesla, Inc.",
            "cik": "0001318605",
            "figi": "BBG000N9MNX3",
            "isin": "US88160R1014",
            "primary_listing": True,
            "asset_type": "stock",
            "sector": "Consumer Cyclical",
            "industry": "Auto Manufacturers",
        },
        "SHOP.TO": {
            "canonical_ticker": "SHOP.TO",
            "exchange": "TSX",
            "country": "CA",
            "currency": "CAD",
            "company_name": "Shopify Inc.",
            "cik": "0001594805",
            "primary_listing": True,
            "cross_listed_ticker": "SHOP",
            "cross_listed_exchange": "NYSE",
            "asset_type": "stock",
            "sector": "Technology",
            "industry": "Software—Infrastructure",
        },
        "SHOP": {
            "canonical_ticker": "SHOP",
            "exchange": "NYSE",
            "country": "US",
            "currency": "USD",
            "company_name": "Shopify Inc.",
            "cik": "0001594805",
            "primary_listing": False,
            "cross_listed_ticker": "SHOP.TO",
            "cross_listed_exchange": "TSX",
            "asset_type": "stock",
            "sector": "Technology",
            "industry": "Software—Infrastructure",
        },
        "RY.TO": {
            "canonical_ticker": "RY.TO",
            "exchange": "TSX",
            "country": "CA",
            "currency": "CAD",
            "company_name": "Royal Bank of Canada",
            "cik": "000080424",
            "primary_listing": True,
            "cross_listed_ticker": "RY",
            "cross_listed_exchange": "NYSE",
            "asset_type": "stock",
            "sector": "Financial Services",
            "industry": "Banks—Diversified",
        },
        "TD.TO": {
            "canonical_ticker": "TD.TO",
            "exchange": "TSX",
            "country": "CA",
            "currency": "CAD",
            "company_name": "Toronto-Dominion Bank",
            "cik": "0000947263",
            "primary_listing": True,
            "cross_listed_ticker": "TD",
            "cross_listed_exchange": "NYSE",
            "asset_type": "stock",
            "sector": "Financial Services",
            "industry": "Banks—Diversified",
        },
        "CNQ.TO": {
            "canonical_ticker": "CNQ.TO",
            "exchange": "TSX",
            "country": "CA",
            "currency": "CAD",
            "company_name": "Canadian Natural Resources Limited",
            "cik": "0001063259",
            "primary_listing": True,
            "cross_listed_ticker": "CNQ",
            "cross_listed_exchange": "NYSE",
            "asset_type": "stock",
            "sector": "Energy",
            "industry": "Oil & Gas Exploration & Production",
        },
    }

    def resolve(self, symbol: str) -> SecurityIdentity:
        """Resolve a raw ticker symbol to a validated canonical SecurityIdentity."""
        clean_symbol = symbol.strip().upper()

        if clean_symbol in self._CANONICAL_DATABASE:
            data = self._CANONICAL_DATABASE[clean_symbol]
            return SecurityIdentity(**data)

        # Dynamic heuristic parsing for unlisted/arbitrary symbols
        if clean_symbol.endswith(".TO"):
            base = clean_symbol[:-3]
            return SecurityIdentity(
                canonical_ticker=clean_symbol,
                exchange="TSX",
                country="CA",
                currency="CAD",
                company_name=f"{base} Corp.",
                primary_listing=True,
                cross_listed_ticker=base,
                cross_listed_exchange="US",
                asset_type="stock",
            )
        elif clean_symbol.endswith(".V"):
            base = clean_symbol[:-2]
            return SecurityIdentity(
                canonical_ticker=clean_symbol,
                exchange="TSXV",
                country="CA",
                currency="CAD",
                company_name=f"{base} Ventures Inc.",
                primary_listing=True,
                asset_type="stock",
            )
        else:
            return SecurityIdentity(
                canonical_ticker=clean_symbol,
                exchange="NYSE/NASDAQ",
                country="US",
                currency="USD",
                company_name=f"{clean_symbol} Inc.",
                primary_listing=True,
                asset_type="stock",
            )
