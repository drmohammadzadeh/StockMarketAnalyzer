# Multi-Agent AI Equity Research System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade, multi-agent AI equity research, analysis, validation, and scoring system for U.S. and Canadian equities and ETFs, with 26 specialist and judge agents, deterministic financial math, data quality gates, and auditable report delivery.

**Architecture:** Layered Python package (`stock_analyzer`) with a custom async DAG pipeline runner, 26 specialist/judge/reviewer agents, multi-tiered data providers (SEC EDGAR direct XBRL, FRED, GDELT, yfinance/open market data, licensed APIs), local quantitative engine (technical indicators, DCF, Graham, Piotroski F-Score, Altman Z-Score), 12 quality gates, and 25-folder research report delivery.

**Tech Stack:** Python 3.13, Pydantic v2, Pandas, DuckDB, yfinance, requests, pytest, pytest-asyncio, Rich, google-genai (Gemini Flash 3.8).

**Spec:** `docs/superpowers/specs/2026-09-14-multi-agent-equity-research-system-design.md`

## Global Constraints
- Every material data point retains a complete `ProvenanceRecord` (provider, endpoint, timestamps, symbol, currency, adjustment status, URL/record ID).
- Zero API keys or tokens are stored in code, logs, git commits, or reports. Secrets read strictly from environment variables.
- Raw provider data is immutably preserved in Parquet format partitioned by `[provider, dataset, symbol, date]`.
- Data quality gate (Gate 4) holds hard veto power: halts with `FAILED_VALIDATION` or `INSUFFICIENT_DATA` if critical values conflict beyond tolerances.
- Scoring scale is standardized to 1.0–10.0 across all dimensions, with Base AI Score computed as $0.40 \times \text{Fundamental} + 0.35 \times \text{Technical} + 0.15 \times \text{Sentiment} + 0.10 \times \text{Macro/Event Risk}$.
- The system supports both US (NYSE, Nasdaq, AMEX) and Canadian (TSX, TSXV) markets with strict currency isolation (USD vs CAD).
- All LLM agents feature an offline deterministic mock mode so tests and pipeline runs execute reliably even without active API keys.

---

### Task 1: Environment Scaffolding & Package Setup

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `stock_analyzer/__init__.py`
- Test: `tests/test_environment.py`

**Interfaces:**
- Produces: Base package initialization, package metadata, dependencies installed via uv, test environment sanity.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_environment.py
def test_environment_import():
    import stock_analyzer
    assert stock_analyzer.__version__ == "1.0.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_environment.py -v`  
Expected: FAIL with ModuleNotFoundError: No module named 'stock_analyzer'

- [ ] **Step 3: Write minimal implementation**

Create `pyproject.toml`:
```toml
[project]
name = "stock-analyzer"
version = "1.0.0"
description = "Multi-Agent AI Equity Research and Validation System"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7.0",
    "pyyaml>=6.0.1",
    "requests>=2.31.0",
    "pandas>=2.2.0",
    "pyarrow>=15.0.0",
    "duckdb>=0.10.0",
    "yfinance>=0.2.38",
    "rich>=13.7.0",
    "google-genai>=0.1.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Create `stock_analyzer/__init__.py`:
```python
"""Multi-Agent AI Equity Research Platform."""

__version__ = "1.0.0"
```

Create `.env.example`:
```env
# LLM Inference
GEMINI_API_KEY=

# Commercial Data Providers (Optional - system auto-promotes when set)
POLYGON_API_KEY=
FINNHUB_API_KEY=
FMP_API_KEY=
TWELVE_DATA_API_KEY=
TIINGO_API_KEY=
FRED_API_KEY=

# SEC EDGAR User-Agent (Required for SEC compliance: Name email@domain.com)
SEC_EDGAR_USER_AGENT=StockMarketAnalyzer research@analyzer.local
```

Update `.gitignore`:
Ensure `.env`, `research/`, `*.parquet`, `__pycache__/`, `.pytest_cache/`, and artifacts are ignored.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv pip install -e .` and `uv run pytest tests/test_environment.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .env.example .gitignore stock_analyzer/__init__.py tests/test_environment.py
git commit -m "feat: initialize project scaffolding and dependency setup"
```

---

### Task 2: Core Data Contracts & Models

**Files:**
- Create: `stock_analyzer/core/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces: `ProvenanceRecord`, `SecurityIdentity`, `MarketQuote`, `FinancialStatements`, `AgentTask`, `AgentOutput`, `JudgeReview`, `ScoringResult`, `GateResult`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
from stock_analyzer.core.models import ProvenanceRecord, SecurityIdentity, AgentTask, ScoringResult

def test_provenance_record_serialization():
    rec = ProvenanceRecord(
        provider="sec_edgar",
        dataset_or_endpoint="xbrl/companyfacts",
        source_timestamp_utc="2026-02-05T21:00:00Z",
        retrieved_at_utc="2026-09-14T09:00:00Z",
        market_session="closed",
        symbol="AAPL",
        currency="USD",
        adjustment_status="unadjusted",
        request_parameters={"cik": "0000320193"},
        provider_record_id_or_url="https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
    )
    assert rec.provider == "sec_edgar"
    assert rec.currency == "USD"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -v`  
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

Implement `stock_analyzer/core/models.py` with complete Pydantic v2 schemas:
- `ProvenanceRecord`: Full audit tracing fields.
- `SecurityIdentity`: canonical_ticker, exchange, country, currency, company_name, cik, figi, isin, primary_listing, asset_type, sector, industry.
- `MarketDataSeries`: daily OHLCV dataframe reference, adjusted series, unadjusted series, start_date, end_date, bar_count.
- `FinancialStatements`: annual and quarterly balance sheets, income statements, cash flow statements.
- `AgentTask`: job_id, symbol, agent, task, status, inputs, outputs, evidence, confidence, warnings, data_gaps, review_status.
- `AgentOutput`: agent_name, status, summary, facts, calculations, inferences, uncertainties, data_gaps, citations, confidence.
- `JudgeReview`: judge_name, target_agent, passed, score, objections, recommendations, review_timestamp.
- `ChiefReviewOutput`: passed, critical_defects, falsification_challenges, confidence_penalty, approved_for_delivery.
- `ScoringResult`: sub_scores (dict of 1.0-10.0), base_ai_score, extended_ai_score, normalized_100_score, confidence_score, penalties.
- `GateResult`: gate_id, gate_name, passed, details, checked_at_utc.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/core/models.py tests/test_models.py
git commit -m "feat(core): define Pydantic data contracts and agent task models"
```

---

### Task 3: Canonical Security Master & Ticker Resolution

**Files:**
- Create: `stock_analyzer/core/security_master.py`
- Test: `tests/test_security_master.py`

**Interfaces:**
- Consumes: Raw ticker string (e.g. `AAPL`, `SHOP.TO`, `RY.TO`, `TSLA`, `SHOP`).
- Produces: `SecurityIdentity` object with country (`US` vs `CA`), exchange (`NASDAQ`, `NYSE`, `TSX`, `TSXV`), currency (`USD` vs `CAD`), primary listing detection, and CIK/FIGI mappings.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_security_master.py
from stock_analyzer.core.security_master import SecurityMaster

def test_resolve_us_security():
    master = SecurityMaster()
    sec = master.resolve("AAPL")
    assert sec.canonical_ticker == "AAPL"
    assert sec.country == "US"
    assert sec.currency == "USD"
    assert sec.exchange in ["NASDAQ", "Nasdaq"]
    assert sec.cik == "0000320193"

def test_resolve_canadian_security():
    master = SecurityMaster()
    sec = master.resolve("SHOP.TO")
    assert sec.canonical_ticker == "SHOP.TO"
    assert sec.country == "CA"
    assert sec.currency == "CAD"
    assert sec.exchange == "TSX"
    assert sec.cross_listed_ticker == "SHOP"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_security_master.py -v`  
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write minimal implementation**

Create `stock_analyzer/core/security_master.py`:
- Contains canonical mapping database for major US and Canadian equities.
- Dynamic fallback parser detecting Canadian `.TO` (TSX), `.V` (TSXV) suffixes.
- Cross-listing dictionary connecting US and Canadian dual-listed equities (e.g. `SHOP` on NYSE $\leftrightarrow$ `SHOP.TO` on TSX, `RY` on NYSE $\leftrightarrow$ `RY.TO` on TSX, `TD` on NYSE $\leftrightarrow$ `TD.TO` on TSX).
- CIK resolver mapping tickers to official 10-digit SEC CIKs.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_security_master.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/core/security_master.py tests/test_security_master.py
git commit -m "feat(core): implement canonical security master and US/CA ticker resolver"
```

---

### Task 4: Source Registry & Configuration Loader

**Files:**
- Create: `stock_analyzer/core/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Consumes: `config/stock_market_data_config.yaml` and `stock_market_data_config_v2.yaml`.
- Produces: `SourceRegistry` ranking providers by priority (authoritative > licensed_api > exchange_or_broker > reputable_aggregator > social_or_crowd > unofficial_library), checking active environment variables.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from stock_analyzer.core.config import ConfigLoader

def test_source_registry_priorities():
    loader = ConfigLoader()
    registry = loader.get_source_registry()
    sources = registry.get_sources_for_capability("historical_ohlcv")
    assert len(sources) > 0
    # Authoritative / licensed APIs rank before unofficial libraries
    assert sources[0].priority <= sources[-1].priority
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create `stock_analyzer/core/config.py`:
- Parses both YAML files cleanly.
- Reads API keys securely from `os.environ` without writing or exposing them.
- Builds `SourceRegistry` capable of returning enabled and authorized providers for each category (`market_and_technical`, `fundamental`, `sentiment_news_and_alternative`, `macro_and_calendar`).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/core/config.py tests/test_config.py
git commit -m "feat(core): implement source registry and YAML configuration parser"
```

---

### Task 5: Provenance Tracker & Research Directory Storage Engine

**Files:**
- Create: `stock_analyzer/core/provenance.py`
- Create: `stock_analyzer/core/storage.py`
- Create: `stock_analyzer/core/audit.py`
- Test: `tests/test_storage_and_audit.py`

**Interfaces:**
- Produces: Initializes the 25 subdirectories under `research/<SYMBOL>/`, saves raw payloads, writes partitioned Parquet files (`provider/dataset/symbol/date`), logs chronological JSON audit events.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_storage_and_audit.py
import os
import shutil
from stock_analyzer.core.storage import ResearchStorage
from stock_analyzer.core.audit import AuditLogger

def test_research_directory_scaffolding(tmp_path):
    storage = ResearchStorage(base_dir=tmp_path)
    paths = storage.init_research_dirs("AAPL")
    assert os.path.exists(paths["00_identity"])
    assert os.path.exists(paths["02_normalized_market_data"])
    assert os.path.exists(paths["23_final_report"])
    assert os.path.exists(paths["24_audit"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_storage_and_audit.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Create:
- `stock_analyzer/core/storage.py`: Sets up directories `00_identity` to `24_audit`. Provides `save_raw_json()`, `save_parquet()`, `load_parquet()`.
- `stock_analyzer/core/provenance.py`: Helper class for building, attaching, and verifying `ProvenanceRecord` on every data item.
- `stock_analyzer/core/audit.py`: Append-only `AuditLogger` writing structured JSON events to `24_audit/audit_log.json`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_storage_and_audit.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/core/provenance.py stock_analyzer/core/storage.py stock_analyzer/core/audit.py tests/test_storage_and_audit.py
git commit -m "feat(core): implement 25-folder research storage engine and audit logger"
```

---

### Task 6: Data Providers (SEC EDGAR, Market Data, FRED, GDELT)

**Files:**
- Create: `stock_analyzer/providers/base.py`
- Create: `stock_analyzer/providers/edgar.py`
- Create: `stock_analyzer/providers/open_market.py`
- Create: `stock_analyzer/providers/fred.py`
- Create: `stock_analyzer/providers/gdelt.py`
- Create: `stock_analyzer/providers/sedar.py`
- Test: `tests/test_providers.py`

**Interfaces:**
- Produces: Normalized data fetchers returning OHLCV bars (min 252 bars), SEC XBRL statements (Revenue, Net Income, FCF, Assets, Debt), FRED macro rates, GDELT news sentiment, and Canadian disclosures with full provenance records.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_providers.py
from stock_analyzer.providers.edgar import EdgarProvider
from stock_analyzer.providers.open_market import OpenMarketProvider

def test_edgar_provider_headers():
    edgar = EdgarProvider(user_agent="TestUser test@analyzer.local")
    headers = edgar.get_headers()
    assert "User-Agent" in headers
    assert "test@analyzer.local" in headers["User-Agent"]

def test_open_market_provider_fetch():
    market = OpenMarketProvider()
    data, provenance = market.get_historical_ohlcv("AAPL", bars=10)
    assert len(data) == 10
    assert "close" in data.columns
    assert provenance.symbol == "AAPL"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_providers.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement:
- `providers/base.py`: `BaseProvider` with rate limiting, exponential backoff (retries on 429/5xx), and provenance builder.
- `providers/edgar.py`: Directly queries `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` and submissions, strictly complying with SEC User-Agent regulations.
- `providers/open_market.py`: Retrieves daily split-adjusted and unadjusted OHLCV bars (with $\ge 252$ bars capability) and volume.
- `providers/fred.py`: Ingests Federal Reserve economic data (Fed funds, CPI, 10-Year Treasury rate).
- `providers/gdelt.py`: Queries GDELT tone and article volume for symbol/company name.
- `providers/sedar.py`: Handles TSX/TSXV filings and cross-listed references.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_providers.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/providers/ tests/test_providers.py
git commit -m "feat(providers): implement multi-tiered data adapters with SEC EDGAR and market data"
```

---

### Task 7: Data Quality Gates & Validation Engine (Gate 1 to Gate 4)

**Files:**
- Create: `stock_analyzer/pipeline/gates.py`
- Test: `tests/test_gates.py`

**Interfaces:**
- Consumes: Fetched market data, filings, security identity.
- Produces: `GateResult` objects; holds VETO authority on Gate 4 (halts pipeline if critical data is negative, missing, stale, or conflicting).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gates.py
import pandas as pd
from stock_analyzer.pipeline.gates import DataQualityGate

def test_reject_negative_price():
    gate = DataQualityGate()
    bad_df = pd.DataFrame([{"close": -10.0, "volume": 1000, "date": "2026-01-01"}])
    result = gate.verify_market_data(bad_df)
    assert result.passed is False
    assert "Negative price detected" in result.details

def test_freshness_verification():
    gate = DataQualityGate()
    result = gate.verify_freshness(latest_filing_days=45)
    assert result.passed is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_gates.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement `stock_analyzer/pipeline/gates.py`:
- `Gate 1 (Identity)`: Validates security identity resolution.
- `Gate 2 (Market Data)`: Validates $\ge 252$ bars, unadjusted and adjusted segregation.
- `Gate 3 (Fundamentals)`: Validates required primary statement fields exist.
- `Gate 4 (Data Quality & Provenance Veto)`: Checks non-negative prices/volumes, validates freshness (<120 days for quarterly financials), verifies cross-source reconciliation against configured tolerances (0.25% price, 5% volume, 1% fundamental).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_gates.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/pipeline/gates.py tests/test_gates.py
git commit -m "feat(pipeline): implement data quality validation engine and hard veto gates"
```

---

### Task 8: Technical Indicator & Volatility Engine

**Files:**
- Create: `stock_analyzer/engine/technical.py`
- Test: `tests/test_technical_engine.py`

**Interfaces:**
- Consumes: Split-adjusted daily OHLCV DataFrame.
- Produces: Standardized technical features dictionary (SMA 20/50/200, EMA 20, ADX 14, RSI 14, MACD 12/26/9, ROC 20, ATR 14, Bollinger Bands 20/2, VWAP, OBV, RVOL 20).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_technical_engine.py
import numpy as np
import pandas as pd
from stock_analyzer.engine.technical import TechnicalEngine

def test_technical_indicators_calculation():
    engine = TechnicalEngine()
    # Create 300 bars of synthetic upward trending OHLCV
    dates = pd.date_range("2025-01-01", periods=300)
    prices = np.linspace(100, 200, 300)
    df = pd.DataFrame({
        "open": prices * 0.99,
        "high": prices * 1.02,
        "low": prices * 0.98,
        "close": prices,
        "volume": np.full(300, 1000000),
    }, index=dates)
    
    result = engine.compute_all_indicators(df)
    assert "SMA_20" in result
    assert "SMA_50" in result
    assert "SMA_200" in result
    assert "RSI_14" in result
    assert "MACD_line" in result
    assert 0 <= result["RSI_14"] <= 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_technical_engine.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement `stock_analyzer/engine/technical.py`:
- Pure vectorized Pandas/NumPy indicator implementations:
  - SMA 20, 50, 200 and EMA 20.
  - Wilder's Smoothed RSI 14.
  - MACD (12, 26, 9) line, signal, histogram.
  - ATR 14 from True Range.
  - Bollinger Bands ($20, 2\sigma$).
  - VWAP, OBV, and Relative Volume $RVOL_{20}$.
  - Support & Resistance levels based on 60-day swing highs/lows.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_technical_engine.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/technical.py tests/test_technical_engine.py
git commit -m "feat(engine): implement technical indicator and volatility calculation engine"
```

---

### Task 9: Fundamental, Forensic & Financial Health Engine

**Files:**
- Create: `stock_analyzer/engine/fundamental.py`
- Create: `stock_analyzer/engine/forensics.py`
- Test: `tests/test_fundamental_and_forensics.py`

**Interfaces:**
- Consumes: Normalized financial statement data (Income statement, Balance sheet, Cash flow).
- Produces: Growth metrics, margins, ROIC, Piotroski F-Score (0–9), Altman Z-Score, Sloan Accrual ratio.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_fundamental_and_forensics.py
from stock_analyzer.engine.fundamental import FundamentalEngine
from stock_analyzer.engine.forensics import ForensicsEngine

def test_piotroski_f_score():
    forensics = ForensicsEngine()
    # Healthy company data fixture
    fin_data = {
        "net_income": 100000,
        "operating_cash_flow": 120000,
        "total_assets_current": 500000,
        "total_assets_prior": 480000,
        "long_term_debt_current": 100000,
        "long_term_debt_prior": 110000,
        "current_ratio_current": 2.0,
        "current_ratio_prior": 1.8,
        "shares_current": 10000,
        "shares_prior": 10000,
        "gross_margin_current": 0.40,
        "gross_margin_prior": 0.38,
        "asset_turnover_current": 1.2,
        "asset_turnover_prior": 1.1,
    }
    score, breakdown = forensics.compute_piotroski_f_score(fin_data)
    assert score >= 7
    assert breakdown["cfo_greater_than_net_income"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_fundamental_and_forensics.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement:
- `engine/fundamental.py`: Revenue CAGR, EPS growth, gross/operating/FCF margins, ROIC ($NOPAT / Invested Capital$), net debt to EBITDA, interest coverage.
- `engine/forensics.py`: Full 9-point Piotroski F-Score, Altman Z-Score with safe/distress thresholds, Sloan Accrual Ratio ($(NI - CFO) / Assets$).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_fundamental_and_forensics.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/fundamental.py stock_analyzer/engine/forensics.py tests/test_fundamental_and_forensics.py
git commit -m "feat(engine): implement fundamental metrics and accounting forensics engine"
```

---

### Task 10: Valuation Engine (DCF, Reverse DCF, Graham, Peer Multiples)

**Files:**
- Create: `stock_analyzer/engine/valuation.py`
- Test: `tests/test_valuation_engine.py`

**Interfaces:**
- Consumes: Cash flows, current price, shares outstanding, risk-free rate (FRED), beta, peers.
- Produces: DCF intrinsic value, 5x5 WACC sensitivity matrix, reverse DCF implied growth rate, Graham Number, peer percentile rankings.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_valuation_engine.py
from stock_analyzer.engine.valuation import ValuationEngine

def test_dcf_and_graham_number():
    engine = ValuationEngine()
    graham = engine.compute_graham_number(eps=6.5, bvps=25.0)
    assert graham > 0
    
    dcf_val, sensitivity = engine.compute_dcf(
        base_fcf=100000,
        growth_rate=0.08,
        wacc=0.09,
        terminal_growth=0.025,
        shares_outstanding=10000,
        net_debt=20000,
    )
    assert dcf_val > 0
    assert len(sensitivity) == 5  # 5x5 matrix
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_valuation_engine.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement `stock_analyzer/engine/valuation.py`:
- 5-year FCFF projection model with growth fade toward terminal rate.
- Perpetuity growth terminal value (capped at max 75% of EV).
- 5x5 WACC $\times$ Terminal Growth sensitivity grid.
- Reverse DCF calculating market-implied growth rate.
- Graham Number calculation $\sqrt{22.5 \times \text{EPS} \times \text{BVPS}}$.
- Relative valuation comparing P/E, EV/EBITDA, P/FCF against industry peer percentiles.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_valuation_engine.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/valuation.py tests/test_valuation_engine.py
git commit -m "feat(engine): implement intrinsic DCF, reverse DCF, and relative valuation engine"
```

---

### Task 11: Deterministic Scoring Engine & Confidence Penalties

**Files:**
- Create: `stock_analyzer/engine/scoring.py`
- Test: `tests/test_scoring.py`

**Interfaces:**
- Consumes: Evaluated sub-scores (Fundamental, Technical, Risk, Sentiment, Valuation, etc.) and data quality indicators.
- Produces: `ScoringResult` with 1.0–10.0 sub-scores, Base AI Score ($0.40 F + 0.35 T + 0.15 S + 0.10 M$), Normalized 0–100 score, Confidence score ($0.0 - 1.0$), and itemized penalty list.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scoring.py
from stock_analyzer.engine.scoring import ScoringEngine

def test_score_calculation_and_confidence():
    engine = ScoringEngine()
    sub_scores = {
        "fundamental": 8.0,
        "technical": 7.0,
        "sentiment": 6.0,
        "macro_event_risk": 7.5,
    }
    penalties = {"insufficient_history": 0.20}
    res = engine.calculate_scores(sub_scores, penalties)
    
    # 0.4*8.0 + 0.35*7.0 + 0.15*6.0 + 0.10*7.5 = 3.2 + 2.45 + 0.90 + 0.75 = 7.30
    assert abs(res.base_ai_score - 7.30) < 1e-4
    assert abs(res.confidence_score - 0.80) < 1e-4
    assert 0 <= res.normalized_100_score <= 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_scoring.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement `stock_analyzer/engine/scoring.py`:
- Implements strict 1.0–10.0 sub-score normalization for all 11 scorecard dimensions.
- Enforces Risk Score polarity: 10 = low risk, 1 = high risk.
- Enforces Valuation Score polarity: 10 = undervalued, 1 = overvalued.
- Base AI Score formula: $0.40 \times F + 0.35 \times T + 0.15 \times S + 0.10 \times M$.
- Extended AI Score incorporating Quality, Growth, Moat, and Valuation.
- Normalized score: $(\text{Base} - 1.0) / 9.0 \times 100$.
- Confidence penalty deductions (stale data: 0.30, missing primary filing: 0.25, unresolved conflict: 0.25, short history: 0.20, low sentiment sample: 0.15).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_scoring.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/scoring.py tests/test_scoring.py
git commit -m "feat(engine): implement deterministic scoring and confidence penalty engine"
```

---

### Task 12: Base Agent & LLM Adapter (Gemini Flash 3.8 + Offline Mock)

**Files:**
- Create: `stock_analyzer/agents/base.py`
- Test: `tests/test_base_agent.py`

**Interfaces:**
- Produces: `BaseAgent` class with structured prompt execution, Pydantic JSON parsing, retries, and offline deterministic mock runner when `GEMINI_API_KEY` is not present.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_base_agent.py
import pytest
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput

@pytest.mark.asyncio
async def test_base_agent_mock_execution():
    agent = BaseAgent(name="TestAgent", role="Testing specialist")
    result = await agent.run(context={"symbol": "AAPL", "test_param": 123})
    assert isinstance(result, AgentOutput)
    assert result.agent_name == "TestAgent"
    assert result.status == "COMPLETED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_base_agent.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement `stock_analyzer/agents/base.py`:
- Integrates Google GenAI SDK (`from google import genai`) using model `gemini-2.5-flash` / `gemini-2.0-flash`.
- Detects if `GEMINI_API_KEY` is present in environment; if not, activates deterministic rule-based mock execution using the quantitative engine outputs.
- Parses LLM responses into structured `AgentOutput` objects.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_base_agent.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/agents/base.py tests/test_base_agent.py
git commit -m "feat(agents): implement BaseAgent with Gemini Flash 3.8 and offline mock runner"
```

---

### Task 13: The 17 Analytical Specialist Agents

**Files:**
- Create: `stock_analyzer/agents/specialists/fundamental.py`
- Create: `stock_analyzer/agents/specialists/technical.py`
- Create: `stock_analyzer/agents/specialists/valuation.py`
- Create: `stock_analyzer/agents/specialists/risk.py`
- Create: `stock_analyzer/agents/specialists/sentiment.py`
- Create: `stock_analyzer/agents/specialists/forensics.py`
- Create: `stock_analyzer/agents/specialists/news_events.py`
- Create: `stock_analyzer/agents/specialists/business.py`
- Create: `stock_analyzer/agents/specialists/management.py`
- Create: `stock_analyzer/agents/specialists/macro.py`
- Create: `stock_analyzer/agents/specialists/quant.py`
- Create: `stock_analyzer/agents/specialists/scenario.py`
- Create: `stock_analyzer/agents/specialists/__init__.py`
- Test: `tests/test_specialists.py`

**Interfaces:**
- Consumes: Research run context (normalized market data, financials, macro, news, quantitative calculations).
- Produces: `AgentOutput` task artifacts for all 17 specialists saved to `research/<SYMBOL>/12_fundamental_analysis/` through `20_quant_analysis/`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_specialists.py
import pytest
from stock_analyzer.agents.specialists.fundamental import FundamentalAgent
from stock_analyzer.agents.specialists.technical import TechnicalAgent

@pytest.mark.asyncio
async def test_specialists_run():
    fund_agent = FundamentalAgent()
    out = await fund_agent.run({"symbol": "AAPL", "revenue": 383000000000, "roic": 0.54})
    assert out.status == "COMPLETED"
    assert "revenue" in out.calculations or len(out.facts) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_specialists.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement each specialist agent subclassing `BaseAgent`:
- `FundamentalAgent`: Growth, profitability, capital structure.
- `TechnicalAgent`: Trend, momentum, volatility, volume confirmation.
- `ValuationAgent`: DCF, reverse DCF, peer multiples.
- `RiskAgent`: Upside & downside risks categorized.
- `SentimentAgent`: 1h/24h/7d news tone and narrative shift.
- `ForensicsAgent`: Accruals, Piotroski, and Altman.
- `NewsEventsAgent`: Verified events vs rumors.
- `BusinessAgent`: Moat, TAM, pricing power.
- `ManagementAgent`: Form 4 insider transactions, buybacks.
- `MacroAgent`: Interest rates, inflation, GDP relevance.
- `QuantAgent`: Volatility, drawdown, beta.
- `ScenarioAgent`: Bull, Base, Bear, Stress cases.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_specialists.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/agents/specialists/ tests/test_specialists.py
git commit -m "feat(agents): implement 17 analytical specialist agents"
```

---

### Task 14: Independent Judges & Adversarial Chief Reviewer

**Files:**
- Create: `stock_analyzer/agents/judges/fundamental_judge.py`
- Create: `stock_analyzer/agents/judges/technical_judge.py`
- Create: `stock_analyzer/agents/judges/risk_judge.py`
- Create: `stock_analyzer/agents/judges/sentiment_judge.py`
- Create: `stock_analyzer/agents/judges/quant_judge.py`
- Create: `stock_analyzer/agents/judges/evidence_judge.py`
- Create: `stock_analyzer/agents/judges/report_judge.py`
- Create: `stock_analyzer/agents/judges/__init__.py`
- Create: `stock_analyzer/agents/chief_reviewer.py`
- Test: `tests/test_judges_and_reviewer.py`

**Interfaces:**
- Consumes: Outputs from all specialists.
- Produces: `JudgeReview` artifacts (Gates 5–10) and `ChiefReviewOutput` (Gate 11). Evaluates evidence links, mathematical accuracy, and adversarial counterarguments. Triggers rework if critical defects exist.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_judges_and_reviewer.py
import pytest
from stock_analyzer.agents.judges.evidence_judge import EvidenceJudge
from stock_analyzer.agents.chief_reviewer import ChiefReviewer

@pytest.mark.asyncio
async def test_evidence_judge_review():
    judge = EvidenceJudge()
    review = await judge.review(specialist_outputs={"facts": ["Revenue grew 5%"], "evidence": [{"source": "10-K"}]})
    assert review.passed is True

@pytest.mark.asyncio
async def test_chief_reviewer_critical_rework():
    reviewer = ChiefReviewer()
    out = await reviewer.adversarial_review(context={"unresolved_contradictions": ["Bullish trend vs negative FCF"]})
    assert "contradiction" in out.falsification_challenges[0].lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_judges_and_reviewer.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement:
- The 7 independent domain judges checking their respective specialties.
- `EvidenceJudge`: Confirms all claims are backed by source entries in `ProvenanceRecord`.
- `ChiefReviewer`: Adversarial falsification agent identifying weak assumptions, contradictory signals, and peer group biases. Sets status to `REWORK_REQUIRED` if critical issues remain unresolved.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_judges_and_reviewer.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/agents/judges/ stock_analyzer/agents/chief_reviewer.py tests/test_judges_and_reviewer.py
git commit -m "feat(agents): implement independent judges and adversarial chief reviewer"
```

---

### Task 15: Delivery Manager & Report Generator

**Files:**
- Create: `stock_analyzer/agents/delivery_manager.py`
- Test: `tests/test_delivery_manager.py`

**Interfaces:**
- Consumes: All verified specialist outputs, judge sign-offs, scoring result, and provenance records.
- Produces:
  1. `research/<SYMBOL>/23_final_report/report.md` (complete 18-section report)
  2. `research/<SYMBOL>/23_final_report/plain_english.md` (simple summary for ordinary investors)
  3. `research/<SYMBOL>/23_final_report/report.json` (machine-readable report payload)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_delivery_manager.py
from stock_analyzer.agents.delivery_manager import DeliveryManager
from stock_analyzer.core.models import ScoringResult

def test_report_generation(tmp_path):
    mgr = DeliveryManager()
    scores = ScoringResult(
        sub_scores={"fundamental": 8.5, "technical": 7.0, "risk": 8.0, "sentiment": 6.5, "valuation": 6.0, "growth": 7.5, "quality": 9.0, "business_strength": 9.0, "management": 8.0, "catalyst": 7.0, "event_risk": 8.0},
        base_ai_score=7.70,
        extended_ai_score=7.65,
        normalized_100_score=74.4,
        confidence_score=0.90,
        penalties={},
    )
    report_md, plain_md = mgr.generate_reports(
        symbol="AAPL",
        company_name="Apple Inc.",
        scores=scores,
        specialist_outputs={},
        provenance_records=[],
    )
    assert "# Apple Inc. (AAPL) — AI Equity Research Report" in report_md
    assert "Scorecard" in report_md
    assert "In Plain English" in plain_md
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_delivery_manager.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement `stock_analyzer/agents/delivery_manager.py`:
- Formats the 18 required report sections: Executive Summary, Scorecard table, Company Overview, Fundamentals, Valuation, Technicals, Sentiment, Risk breakdown, Business & Moat, Management & Insiders, Catalysts, Bull/Bear/Base cases, Invalidation conditions, Final Assessment, Sources table, and Disclaimer.
- Formats `plain_english.md` answering: What company does, why investors like/avoid, what is attractive/expensive/risky, what to watch next.
- Enforces Gate 12 (Delivery Review).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_delivery_manager.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/agents/delivery_manager.py tests/test_delivery_manager.py
git commit -m "feat(delivery): implement delivery manager and 18-section report generator"
```

---

### Task 16: Research Pipeline Orchestrator & CLI

**Files:**
- Create: `stock_analyzer/pipeline/orchestrator.py`
- Create: `stock_analyzer/cli/main.py`
- Create: `stock_analyzer/__main__.py`
- Test: `tests/test_pipeline_orchestrator.py`

**Interfaces:**
- Produces: Top-level `ResearchOrchestrator` coordinating all 8 phases and 12 gates sequentially with concurrent task groups; Rich terminal CLI `python -m stock_analyzer analyze <SYMBOL>`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pipeline_orchestrator.py
import pytest
from stock_analyzer.pipeline.orchestrator import ResearchOrchestrator

@pytest.mark.asyncio
async def test_pipeline_orchestrator_flow(tmp_path):
    orchestrator = ResearchOrchestrator(base_dir=tmp_path)
    result = await orchestrator.run("AAPL", horizon="6-12 months")
    assert result.status in ["COMPLETE", "PARTIAL"]
    assert result.symbol == "AAPL"
    assert result.scores is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_pipeline_orchestrator.py -v`  
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement:
- `stock_analyzer/pipeline/orchestrator.py`: Coordinates Phase 1 (Identity) $\rightarrow$ Phase 2 (Data Ingestion) $\rightarrow$ Phase 3 (Quality & Provenance Gate 4) $\rightarrow$ Phase 4 (Concurrent 12 Specialists) $\rightarrow$ Phase 5 (7 Judges) $\rightarrow$ Phase 6 (Adversarial Review) $\rightarrow$ Phase 7 (Scoring Engine) $\rightarrow$ Phase 8 (Delivery Manager).
- `stock_analyzer/cli/main.py`: Rich CLI displaying interactive live progress bars, stage status, score summary table, and output report paths.
- `stock_analyzer/__main__.py`: Direct invocation entry point.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_pipeline_orchestrator.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/pipeline/orchestrator.py stock_analyzer/cli/main.py stock_analyzer/__main__.py tests/test_pipeline_orchestrator.py
git commit -m "feat(pipeline): implement research pipeline orchestrator and rich CLI runner"
```

---

### Task 17: End-to-End AAPL Run, Canadian Security Test & Remote Push

**Files:**
- Create: `tests/test_e2e.py`
- Output: `research/AAPL/` (full 25-folder populated directory and published reports)
- Output: `research/SHOP.TO/` (demonstrating Canadian security resolution and CAD currency isolation)

**Interfaces:**
- Verifies: Full acceptance criteria, all 12 gates pass, all 25 subdirectories populated, reports published, tests passing, and git push to GitHub remote.

- [ ] **Step 1: Execute full test suite**

Run: `uv run pytest -v`  
Expected: All unit and integration tests PASS.

- [ ] **Step 2: Run full research job for AAPL**

Run: `python -m stock_analyzer analyze AAPL --horizon "6-12 months"`  
Expected:
- Identity resolved: Apple Inc., NASDAQ, USD, CIK 0000320193.
- All 25 directories populated under `research/AAPL/`.
- Report published in `research/AAPL/23_final_report/report.md`.
- Summary published in `research/AAPL/23_final_report/plain_english.md`.
- Audit log written to `research/AAPL/24_audit/audit_log.json`.

- [ ] **Step 3: Run research job for Canadian cross-listed ticker SHOP.TO**

Run: `python -m stock_analyzer analyze SHOP.TO`  
Expected:
- Identity resolved: Shopify Inc., TSX, CAD, cross-listed NYSE:SHOP.
- Currency isolated to CAD.

- [ ] **Step 4: Git Commit & Remote Push**

Commit all new features, tests, and documentation. Push to `origin/main` using the provided GitHub personal access token without leaking the token in history or files.

Run:
```bash
git add .
git commit -m "feat: complete multi-agent equity research platform for US and Canadian equities"
git push https://<TOKEN>@github.com/drmohammadzadeh/StockMarketAnalyzer.git main
```
(Token passed securely via parameter in runtime shell, never committed to disk).
