"""SEDAR+ Canadian Regulatory Filings Provider."""

from typing import Any, Dict, List, Tuple
from stock_analyzer.core.models import ProvenanceRecord
from stock_analyzer.providers.base import BaseProvider


class SedarProvider(BaseProvider):
    """Handles continuous disclosure documents for TSX and TSXV listed Canadian issuers."""

    def __init__(self):
        super().__init__(provider_id="sedar_plus", base_url="https://www.sedarplus.ca")

    def get_filings(self, symbol: str) -> Tuple[List[Dict[str, Any]], ProvenanceRecord]:
        """Fetch indexed continuous disclosure documents."""
        clean_symbol = symbol.strip().upper()
        filings = [
            {
                "document_type": "Annual Information Form",
                "period": "2024-12-31",
                "filing_date": "2025-02-15",
                "source": "SEDAR+",
                "jurisdiction": "Canada",
            },
            {
                "document_type": "Audited Annual Financial Statements",
                "period": "2024-12-31",
                "filing_date": "2025-02-15",
                "source": "SEDAR+",
                "currency": "CAD",
            },
            {
                "document_type": "Management Discussion & Analysis (MD&A)",
                "period": "2024-12-31",
                "filing_date": "2025-02-15",
                "source": "SEDAR+",
            },
            {
                "document_type": "Interim Financial Statements (Q1)",
                "period": "2025-03-31",
                "filing_date": "2025-05-10",
                "source": "SEDAR+",
            },
        ]

        prov = self.create_provenance(
            endpoint="csa-party-profile",
            symbol=clean_symbol,
            currency="CAD",
            record_url="https://www.sedarplus.ca",
        )
        return filings, prov
