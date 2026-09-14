from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from stock_analyzer.core.models import ProvenanceRecord


class ProvenanceTracker:
    """Maintains and verifies provenance chains for all data artifacts."""

    def __init__(self):
        self._records: List[ProvenanceRecord] = []

    def create_record(
        self,
        provider: str,
        endpoint: str,
        symbol: str,
        source_time: Optional[str] = None,
        currency: str = "USD",
        adjustment: str = "unadjusted",
        params: Optional[Dict[str, Any]] = None,
        url: str = "",
        session: str = "closed",
    ) -> ProvenanceRecord:
        """Create a new ProvenanceRecord with UTC timestamps."""
        now_utc = datetime.now(timezone.utc).isoformat()
        return ProvenanceRecord(
            provider=provider,
            dataset_or_endpoint=endpoint,
            source_timestamp_utc=source_time or now_utc,
            retrieved_at_utc=now_utc,
            market_session=session,
            symbol=symbol.strip().upper(),
            currency=currency,
            adjustment_status=adjustment,
            request_parameters=params or {},
            provider_record_id_or_url=url,
        )

    def register(self, record: ProvenanceRecord) -> None:
        """Register a record into the active provenance chain."""
        self._records.append(record)

    def get_records_for_symbol(self, symbol: str) -> List[ProvenanceRecord]:
        """Retrieve all provenance records for a given security symbol."""
        clean = symbol.strip().upper()
        return [r for r in self._records if r.symbol == clean]

    def all_records(self) -> List[ProvenanceRecord]:
        return list(self._records)
