"""Base Data Provider with rate limiting and exponential backoff retry logic."""

import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import requests
from stock_analyzer.core.models import ProvenanceRecord


class BaseProvider:
    """Abstract base provider handling retries, session headers, and provenance creation."""

    def __init__(self, provider_id: str, base_url: str = ""):
        self.provider_id = provider_id
        self.base_url = base_url
        self.session = requests.Session()

    def create_provenance(
        self,
        endpoint: str,
        symbol: str,
        currency: str = "USD",
        adjustment: str = "unadjusted",
        params: Optional[Dict[str, Any]] = None,
        record_url: str = "",
        session: str = "closed",
    ) -> ProvenanceRecord:
        """Helper to create a ProvenanceRecord for data produced by this provider."""
        now_utc = datetime.now(timezone.utc).isoformat()
        return ProvenanceRecord(
            provider=self.provider_id,
            dataset_or_endpoint=endpoint,
            source_timestamp_utc=now_utc,
            retrieved_at_utc=now_utc,
            market_session=session,
            symbol=symbol.strip().upper(),
            currency=currency,
            adjustment_status=adjustment,
            request_parameters=params or {},
            provider_record_id_or_url=record_url or self.base_url,
        )

    def fetch_with_retry(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        timeout: int = 15,
    ) -> requests.Response:
        """Executes HTTP request with exponential backoff on 429 and 5xx errors."""
        for attempt in range(max_retries):
            try:
                resp = self.session.get(url, headers=headers, params=params, timeout=timeout)
                if resp.status_code == 429 or (500 <= resp.status_code < 600):
                    if attempt < max_retries - 1:
                        sleep_time = backoff_factor * (2 ** attempt)
                        time.sleep(sleep_time)
                        continue
                resp.raise_for_status()
                return resp
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(backoff_factor * (2 ** attempt))
        raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts.")
