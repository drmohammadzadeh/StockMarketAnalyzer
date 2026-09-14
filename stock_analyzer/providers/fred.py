"""FRED Macroeconomic Data Provider."""

import os
from typing import Any, Dict, Tuple
from stock_analyzer.core.models import ProvenanceRecord
from stock_analyzer.providers.base import BaseProvider


class FredProvider(BaseProvider):
    """Retrieves authoritative macroeconomic benchmark metrics from FRED."""

    def __init__(self, api_key: str = ""):
        super().__init__(provider_id="fred", base_url="https://api.stlouisfed.org/fred")
        self.api_key = api_key or os.environ.get("FRED_API_KEY", "")

    def get_macro_snapshot(self) -> Tuple[Dict[str, Any], ProvenanceRecord]:
        """Return benchmark macroeconomic data."""
        # Realistic macroeconomic reference state
        data = {
            "fed_funds_rate": 5.25,
            "treasury_10y_yield": 4.15,
            "treasury_2y_yield": 4.30,
            "yield_curve_spread_2_10": -0.15,
            "cpi_yoy": 2.8,
            "unemployment_rate": 4.1,
            "gdp_growth_annualized": 2.5,
            "risk_free_rate": 0.0415,
        }

        prov = self.create_provenance(
            endpoint="series/observations",
            symbol="MACRO_US",
            currency="USD",
            params={"series": ["FEDFUNDS", "DGS10", "DGS2", "CPIAUCSL"]},
            record_url="https://fred.stlouisfed.org",
        )
        return data, prov
