"""Quality Gates Engine enforcing deterministic gates 1 through 12."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import pandas as pd
from stock_analyzer.core.models import GateResult, SecurityIdentity


class QualityGateEngine:
    """Evaluates pipeline quality gates with veto enforcement."""

    def evaluate_gate1_identity(self, identity: Optional[SecurityIdentity]) -> GateResult:
        """Gate 1: Verify canonical security identity and exchange classification."""
        if not identity or not identity.canonical_ticker:
            return GateResult(
                gate_id="GATE_1_IDENTITY",
                gate_name="Security Identity Verification",
                passed=False,
                details="Security identity could not be resolved.",
                remedy_action="Check ticker symbol spelling or add to security master.",
            )
        return GateResult(
            gate_id="GATE_1_IDENTITY",
            gate_name="Security Identity Verification",
            passed=True,
            details=f"Resolved canonical ticker {identity.canonical_ticker} on {identity.exchange} ({identity.currency}).",
        )

    def evaluate_gate2_market_data(self, df: pd.DataFrame, required_bars: int = 252) -> GateResult:
        """Gate 2: Verify required historical market data bars and structure."""
        if df is None or df.empty:
            return GateResult(
                gate_id="GATE_2_MARKET_DATA",
                gate_name="Historical Market Data Acquisition",
                passed=False,
                details="No market data was returned.",
                remedy_action="Check market data provider status or symbol availability.",
            )
        
        count = len(df)
        if count < required_bars:
            return GateResult(
                gate_id="GATE_2_MARKET_DATA",
                gate_name="Historical Market Data Acquisition",
                passed=False,
                details=f"Insufficient history: {count} bars returned, {required_bars} required for complete technical indicators.",
                remedy_action="Acquire longer historical bar series.",
            )

        return GateResult(
            gate_id="GATE_2_MARKET_DATA",
            gate_name="Historical Market Data Acquisition",
            passed=True,
            details=f"Successfully acquired {count} bars of daily OHLCV trading data.",
        )

    def evaluate_gate3_fundamentals(self, facts: Dict[str, Any]) -> GateResult:
        """Gate 3: Verify availability of primary financial statement facts."""
        required_concepts = ["Revenues", "NetIncomeLoss", "Assets"]
        missing = [c for c in required_concepts if c not in facts]

        if missing:
            return GateResult(
                gate_id="GATE_3_FUNDAMENTALS",
                gate_name="Primary Regulatory Filings and Statements",
                passed=False,
                details=f"Missing essential fundamental concepts: {', '.join(missing)}.",
                remedy_action="Attempt second-source fundamental provider.",
            )

        return GateResult(
            gate_id="GATE_3_FUNDAMENTALS",
            gate_name="Primary Regulatory Filings and Statements",
            passed=True,
            details="Essential GAAP statement concepts (Revenue, Net Income, Assets) present.",
        )

    def evaluate_gate4_data_quality(
        self,
        market_df: pd.DataFrame,
        filing_days_old: int = 45,
        max_filing_age_days: int = 120,
    ) -> GateResult:
        """Gate 4: Hard Data Quality & Provenance Veto."""
        # 1. Non-negative prices/volumes
        if (market_df["close"] <= 0).any():
            return GateResult(
                gate_id="GATE_4_DATA_QUALITY_VETO",
                gate_name="Data Quality and Provenance Integrity",
                passed=False,
                details="Negative price detected in market data series.",
                remedy_action="Purge corrupt tick rows and refetch.",
            )

        if (market_df["volume"] < 0).any():
            return GateResult(
                gate_id="GATE_4_DATA_QUALITY_VETO",
                gate_name="Data Quality and Provenance Integrity",
                passed=False,
                details="Negative volume detected in market data series.",
                remedy_action="Purge corrupt tick rows and refetch.",
            )

        # 2. Freshness check
        if filing_days_old > max_filing_age_days:
            return GateResult(
                gate_id="GATE_4_DATA_QUALITY_VETO",
                gate_name="Data Quality and Provenance Integrity",
                passed=False,
                details=f"Fundamental filings freshness limit exceeded: {filing_days_old} days old (max allowed: {max_filing_age_days}).",
                remedy_action="Check for newly published 10-Q or 10-K filings.",
            )

        return GateResult(
            gate_id="GATE_4_DATA_QUALITY_VETO",
            gate_name="Data Quality and Provenance Integrity",
            passed=True,
            details="Data quality checks passed: non-negative prices, valid volume, and fresh statements.",
        )
