"""Chronological Audit Logging for Research Jobs."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    """Append-only audit trail logging for research runs."""

    def __init__(self, log_path: Path | str):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self._write_events([])

    def _read_events(self) -> List[Dict[str, Any]]:
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_events(self, events: List[Dict[str, Any]]) -> None:
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Append an audit event with UTC timestamp."""
        events = self._read_events()
        event_record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "details": details,
        }
        events.append(event_record)
        self._write_events(events)

    def get_events(self) -> List[Dict[str, Any]]:
        return self._read_events()
