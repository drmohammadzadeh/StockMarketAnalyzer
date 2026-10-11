# Comprehensive Visual Charts & Excalidraw Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the multi-agent equity research platform with an institutional suite of visual charts (`price_action_trend.png`, `financial_conversion_bars.png`, `valuation_margin_gauge.png`, `business_moat_diagram.png` + `.excalidraw`) embedded across research dashboards.

**Architecture:** Implement modular chart generators in `stock_analyzer/engine/charts.py` and a dedicated `excalidraw_generator.py`. Wire them into Phase 7 of `orchestrator.py`, update `delivery_manager.py` to embed all assets into `README.md` and `report.md`, and verify with thorough unit tests and pipeline execution.

**Tech Stack:** Python 3.14, Matplotlib, Pandas, NumPy, Pydantic, Pytest.

**Spec:** `docs/superpowers/specs/2026-10-11-comprehensive-visual-charts-design.md`

## Global Constraints
- All reports and code comments must remain strictly in English.
- Visual charts must be saved into `research/{SYMBOL}/assets/`.
- Chart generation must be deterministic, offline-capable, and non-blocking (isolated with try/except logging).
- All tests must pass via `uv run pytest`.

---

### Task 1: Implement Price Action & Trend Ribbon Chart Generator

**Files:**
- Modify: `stock_analyzer/engine/charts.py`
- Test: `tests/test_charts.py`

**Interfaces:**
- Produces: `generate_price_action_chart(df: pd.DataFrame, symbol: str, company_name: str, output_path: Path) -> Path`

- [ ] **Step 1: Write the failing test for price action chart**

Create or update `tests/test_charts.py`:
```python
import numpy as np
import pandas as pd
from pathlib import Path
from stock_analyzer.engine.charts import generate_price_action_chart

def test_generate_price_action_chart(tmp_path: Path):
    dates = pd.date_range("2025-01-01", periods=252, freq="B")
    prices = 150.0 + np.cumsum(np.random.randn(252) * 2.0)
    df = pd.DataFrame({
        "close": prices,
        "volume": np.random.randint(1000000, 5000000, size=252)
    }, index=dates)
    
    out_file = tmp_path / "price_action_trend.png"
    result = generate_price_action_chart(df, "TEST", "Test Corp", out_file)
    assert result.exists()
    assert result.stat().st_size > 5000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_charts.py::test_generate_price_action_chart -v`
Expected: FAIL with `ImportError: cannot import name 'generate_price_action_chart'`

- [ ] **Step 3: Implement `generate_price_action_chart`**

In `stock_analyzer/engine/charts.py`:
```python
def generate_price_action_chart(
    df: pd.DataFrame,
    symbol: str,
    company_name: str,
    output_path: Path,
) -> Path:
    """
    Renders 252-day price action with 50/200 SMA trend ribbon, volume, and 14-day RSI.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_df = df.copy()
    if "close" not in clean_df.columns:
        raise ValueError("DataFrame must contain 'close' column")
    
    close = clean_df["close"].astype(float)
    sma50 = close.rolling(50, min_periods=1).mean()
    sma200 = close.rolling(200, min_periods=1).mean()
    
    # RSI 14
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.rolling(14, min_periods=1).mean()
    avg_loss = loss.rolling(14, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-6)
    rsi14 = 100.0 - (100.0 / (1.0 + rs))
    
    fig, (ax_price, ax_rsi) = plt.subplots(
        2, 1, figsize=(10, 6.5), dpi=200, facecolor="#0f172a",
        gridspec_kw={"height_ratios": [3.2, 1.2], "hspace": 0.15}
    )
    
    x = np.arange(len(close))
    ax_price.set_facecolor("#1e293b")
    ax_price.plot(x, close, color="#f8fafc", linewidth=2.0, label="Daily Close")
    ax_price.plot(x, sma50, color="#38bdf8", linewidth=1.8, label="50-Day SMA")
    ax_price.plot(x, sma200, color="#fbbf24", linewidth=1.8, label="200-Day SMA")
    
    # Shaded ribbon between SMAs
    ax_price.fill_between(x, sma50, sma200, where=(sma50 >= sma200), color="#22c55e", alpha=0.25, label="Bullish Regime")
    ax_price.fill_between(x, sma50, sma200, where=(sma50 < sma200), color="#ef4444", alpha=0.25, label="Bearish Regime")
    
    # Volume bars
    if "volume" in clean_df.columns:
        vol = clean_df["volume"].astype(float)
        ax_vol = ax_price.twinx()
        ax_vol.bar(x, vol, color="#64748b", alpha=0.3, width=0.8)
        ax_vol.set_ylim(0, vol.max() * 4.0)
        ax_vol.axis("off")
        
    curr_p = close.iloc[-1]
    ax_price.set_title(f"{company_name} ({symbol}) — Price Action & Trend Ribbon | Close: ${curr_p:.2f}", fontsize=13, fontweight="bold", color="#f8fafc", pad=10)
    ax_price.grid(color="#334155", linestyle="--", linewidth=0.7, alpha=0.6)
    ax_price.tick_params(colors="#94a3b8")
    ax_price.legend(loc="upper left", facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc", fontsize=9)
    
    # RSI Sub-panel
    ax_rsi.set_facecolor("#1e293b")
    ax_rsi.plot(x, rsi14, color="#a855f7", linewidth=1.8)
    ax_rsi.axhline(70, color="#ef4444", linestyle=":", linewidth=1.2, alpha=0.8)
    ax_rsi.axhline(30, color="#22c55e", linestyle=":", linewidth=1.2, alpha=0.8)
    ax_rsi.fill_between(x, 70, 100, color="#ef4444", alpha=0.15)
    ax_rsi.fill_between(x, 0, 30, color="#22c55e", alpha=0.15)
    ax_rsi.set_ylim(0, 100)
    curr_rsi = rsi14.iloc[-1]
    ax_rsi.set_ylabel(f"RSI(14): {curr_rsi:.1f}", color="#f8fafc", fontsize=10, fontweight="bold")
    ax_rsi.grid(color="#334155", linestyle="--", linewidth=0.7, alpha=0.6)
    ax_rsi.tick_params(colors="#94a3b8")
    
    plt.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=200)
    plt.close(fig)
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_charts.py::test_generate_price_action_chart -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/charts.py tests/test_charts.py
git commit -m "feat(charts): add generate_price_action_chart with 50/200 SMA and RSI"
```

---

### Task 2: Implement Financial Conversion & Cash Flow Waterfall Chart

**Files:**
- Modify: `stock_analyzer/engine/charts.py`
- Test: `tests/test_charts.py`

**Interfaces:**
- Produces: `generate_financial_waterfall_chart(financials: Dict[str, float], symbol: str, company_name: str, output_path: Path) -> Path`

- [ ] **Step 1: Write the failing test for financial conversion chart**

In `tests/test_charts.py`:
```python
from stock_analyzer.engine.charts import generate_financial_waterfall_chart

def test_generate_financial_waterfall_chart(tmp_path: Path):
    data = {
        "revenue": 716924000000.0,
        "operating_income": 79975000000.0,
        "net_income": 77670000000.0,
        "operating_cash_flow": 139514000000.0,
        "free_cash_flow": 132777000000.0,
    }
    out_file = tmp_path / "financial_conversion_bars.png"
    result = generate_financial_waterfall_chart(data, "AMZN", "Amazon.com, Inc.", out_file)
    assert result.exists()
    assert result.stat().st_size > 5000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_charts.py::test_generate_financial_waterfall_chart -v`
Expected: FAIL with `ImportError: cannot import name 'generate_financial_waterfall_chart'`

- [ ] **Step 3: Implement `generate_financial_waterfall_chart`**

In `stock_analyzer/engine/charts.py`:
```python
def generate_financial_waterfall_chart(
    financials: Dict[str, float],
    symbol: str,
    company_name: str,
    output_path: Path,
) -> Path:
    """
    Renders 5 operational pillars: Revenue, EBIT, Net Income, CFO, and FCF.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rev = financials.get("revenue", 100e9) / 1e9
    op_inc = financials.get("operating_income", 15e9) / 1e9
    ni = financials.get("net_income", 10e9) / 1e9
    cfo = financials.get("operating_cash_flow", 18e9) / 1e9
    fcf = financials.get("free_cash_flow", 12e9) / 1e9
    
    categories = ["Revenue", "Operating\nIncome", "Net\nIncome", "Operating\nCash Flow", "Free Cash\nFlow (FCF)"]
    vals = [rev, op_inc, ni, cfo, fcf]
    colors = ["#2563eb", "#0284c7", "#10b981", "#059669", "#16a34a"]
    
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200, facecolor="#0f172a")
    ax.set_facecolor("#1e293b")
    
    bars = ax.bar(categories, vals, color=colors, width=0.55, edgecolor="#ffffff", linewidth=1.2, zorder=3)
    ax.grid(axis="y", color="#334155", linestyle="--", linewidth=0.7, alpha=0.7, zorder=0)
    
    # Annotate dollar billions and conversion ratios
    for idx, (b, val) in enumerate(zip(bars, vals)):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2.0, h + (max(vals) * 0.02), f"${val:.1f}B",
                ha="center", va="bottom", color="#f8fafc", fontweight="bold", fontsize=10)
    
    op_m = (op_inc / max(rev, 0.001)) * 100.0
    net_m = (ni / max(rev, 0.001)) * 100.0
    fcf_conv = (fcf / max(ni, 0.001)) * 100.0
    
    subtitle = f"Operating Margin: {op_m:.1f}%  |  Net Margin: {net_m:.1f}%  |  FCF Conversion: {fcf_conv:.1f}%"
    ax.set_title(f"{company_name} ({symbol}) — Financial Conversion & Cash Flow Engine\n{subtitle}",
                 fontsize=12, fontweight="bold", color="#f8fafc", pad=14)
    ax.tick_params(colors="#94a3b8")
    ax.set_ylabel("USD ($ Billions)", color="#94a3b8", fontsize=10)
    ax.set_ylim(0, max(vals) * 1.15)
    
    plt.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=200)
    plt.close(fig)
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_charts.py::test_generate_financial_waterfall_chart -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/charts.py tests/test_charts.py
git commit -m "feat(charts): add generate_financial_waterfall_chart"
```

---

### Task 3: Implement Valuation Margin-of-Safety Gauge

**Files:**
- Modify: `stock_analyzer/engine/charts.py`
- Test: `tests/test_charts.py`

**Interfaces:**
- Produces: `generate_valuation_margin_chart(valuation_data: Dict[str, float], symbol: str, company_name: str, output_path: Path) -> Path`

- [ ] **Step 1: Write the failing test for valuation gauge**

In `tests/test_charts.py`:
```python
from stock_analyzer.engine.charts import generate_valuation_margin_chart

def test_generate_valuation_margin_chart(tmp_path: Path):
    data = {
        "current_price": 262.43,
        "intrinsic_value": 229.22,
        "graham_number": 78.60,
        "fifty_two_week_low": 165.0,
        "fifty_two_week_high": 275.0,
    }
    out_file = tmp_path / "valuation_margin_gauge.png"
    result = generate_valuation_margin_chart(data, "AMZN", "Amazon.com, Inc.", out_file)
    assert result.exists()
    assert result.stat().st_size > 5000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_charts.py::test_generate_valuation_margin_chart -v`
Expected: FAIL with `ImportError: cannot import name 'generate_valuation_margin_chart'`

- [ ] **Step 3: Implement `generate_valuation_margin_chart`**

In `stock_analyzer/engine/charts.py`:
```python
def generate_valuation_margin_chart(
    valuation_data: Dict[str, float],
    symbol: str,
    company_name: str,
    output_path: Path,
) -> Path:
    """
    Renders horizontal target gauge comparing Market Price to DCF Intrinsic Value and Graham Number.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    curr_p = float(valuation_data.get("current_price", 100.0))
    dcf_val = float(valuation_data.get("intrinsic_value", 100.0))
    graham = float(valuation_data.get("graham_number", 50.0))
    low_52 = float(valuation_data.get("fifty_two_week_low", curr_p * 0.7))
    high_52 = float(valuation_data.get("fifty_two_week_high", curr_p * 1.3))
    
    min_x = min(low_52, graham, dcf_val * 0.7, curr_p * 0.8) * 0.95
    max_x = max(high_52, dcf_val * 1.3, curr_p * 1.15) * 1.05
    
    fig, ax = plt.subplots(figsize=(9.5, 3.8), dpi=200, facecolor="#0f172a")
    ax.set_facecolor("#1e293b")
    
    # Zones: Undervalued (up to 0.85 DCF), Fair (0.85 - 1.15 DCF), Overvalued (> 1.15 DCF)
    underval_end = dcf_val * 0.85
    overval_start = dcf_val * 1.15
    
    ax.axvspan(min_x, underval_end, color="#22c55e", alpha=0.25, label="Undervalued Zone")
    ax.axvspan(underval_end, overval_start, color="#f59e0b", alpha=0.25, label="Fair Value Range")
    ax.axvspan(overval_start, max_x, color="#ef4444", alpha=0.25, label="Premium / Overheated Zone")
    
    # Markers
    ax.plot([dcf_val, dcf_val], [-0.5, 0.5], color="#38bdf8", linewidth=3.5, label=f"DCF Fair Value (${dcf_val:.2f})")
    ax.plot([graham, graham], [-0.3, 0.3], color="#a855f7", linewidth=2.5, linestyle="--", label=f"Graham Floor (${graham:.2f})")
    
    # Current Price pointer
    ax.scatter([curr_p], [0.0], color="#f8fafc", s=180, edgecolors="#e11d48", linewidth=3.0, zorder=6, label=f"Market Price (${curr_p:.2f})")
    ax.annotate(f"Current Close: ${curr_p:.2f}", (curr_p, 0.0), xytext=(0, 25), textcoords="offset points",
                ha="center", color="#f8fafc", fontweight="bold", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.3", fc="#e11d48", ec="none"))
    
    diff_pct = ((dcf_val - curr_p) / curr_p) * 100.0
    status_str = f"Discount: +{diff_pct:.1f}% (Undervalued)" if diff_pct > 0 else f"Premium: {abs(diff_pct):.1f}% (Above DCF)"
    
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(-0.8, 0.8)
    ax.set_yticks([])
    ax.tick_params(colors="#94a3b8")
    ax.grid(axis="x", color="#334155", linestyle="--", linewidth=0.7, alpha=0.6)
    
    ax.set_title(f"{company_name} ({symbol}) — Valuation Range & Margin of Safety\n{status_str}",
                 fontsize=12, fontweight="bold", color="#f8fafc", pad=12)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=4, facecolor="#1e293b", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8.5)
    
    plt.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=200)
    plt.close(fig)
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_charts.py::test_generate_valuation_margin_chart -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/charts.py tests/test_charts.py
git commit -m "feat(charts): add generate_valuation_margin_chart"
```

---

### Task 4: Implement Strategic Business Moat Excalidraw Generator

**Files:**
- Create: `stock_analyzer/engine/excalidraw_generator.py`
- Test: `tests/test_excalidraw_generator.py`

**Interfaces:**
- Produces: `generate_moat_excalidraw_diagram(symbol: str, company_name: str, profile: Dict[str, Any], output_base_path: Path) -> Tuple[Path, Path]`

- [ ] **Step 1: Write test for Excalidraw generator**

Create `tests/test_excalidraw_generator.py`:
```python
import json
from pathlib import Path
from stock_analyzer.engine.excalidraw_generator import generate_moat_excalidraw_diagram

def test_generate_moat_excalidraw_diagram(tmp_path: Path):
    profile = {
        "overview": "Amazon overview",
        "thesis_moats": ["AWS Cloud Lock-in", "Fulfillment Network", "Prime Flywheel"],
        "thesis_risks": ["Capex Cycles", "Antitrust", "Pricing Pressure"]
    }
    out_file = tmp_path / "business_moat_diagram.excalidraw"
    excal_path, png_path = generate_moat_excalidraw_diagram("AMZN", "Amazon.com, Inc.", profile, out_file)
    assert excal_path.exists()
    assert png_path.exists()
    with open(excal_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["type"] == "excalidraw"
    assert len(data["elements"]) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_excalidraw_generator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'stock_analyzer.engine.excalidraw_generator'`

- [ ] **Step 3: Implement `stock_analyzer/engine/excalidraw_generator.py`**

Create `stock_analyzer/engine/excalidraw_generator.py`:
- Implements `build_moat_excalidraw_document` building valid Excalidraw elements.
- Implements vector image generation for `business_moat_diagram.png` rendering the visual flowchart cleanly.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_excalidraw_generator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stock_analyzer/engine/excalidraw_generator.py tests/test_excalidraw_generator.py
git commit -m "feat(excalidraw): add generate_moat_excalidraw_diagram"
```

---

### Task 5: Integrate All Visual Chart Generators in Research Pipeline

**Files:**
- Modify: `stock_analyzer/pipeline/orchestrator.py`
- Test: `tests/test_pipeline_orchestrator.py`

**Interfaces:**
- Consumes: All 5 chart renderers
- Produces: 6 image assets in `research/{clean_symbol}/assets/`

- [ ] **Step 1: Write integration test verifying all 6 assets are created**

In `tests/test_pipeline_orchestrator.py`, verify asset outputs:
```python
def test_pipeline_generates_all_six_visual_assets(tmp_path):
    # Runs pipeline mock and asserts:
    # radar_score_chart.png, technical_gauges.png, price_action_trend.png,
    # financial_conversion_bars.png, valuation_margin_gauge.png, business_moat_diagram.png
```

- [ ] **Step 2: Update `orchestrator.py` Phase 7**

Call each renderer safely inside a try-except block, logging any warning to audit log.

- [ ] **Step 3: Run pytest**

Run: `uv run pytest tests/test_pipeline_orchestrator.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add stock_analyzer/pipeline/orchestrator.py tests/test_pipeline_orchestrator.py
git commit -m "feat(pipeline): render all 6 visual assets in Phase 7"
```

---

### Task 6: Update Delivery Manager to Embed Visual Gallery

**Files:**
- Modify: `stock_analyzer/agents/delivery_manager.py`
- Test: `tests/test_delivery_manager.py`

**Interfaces:**
- Updates: `generate_readme_summary` and `generate_reports` to embed all 6 assets.

- [ ] **Step 1: Update `test_delivery_manager.py`**

Assert that generated `README.md` and `report.md` reference the new asset image names.

- [ ] **Step 2: Update `generate_readme_summary` and `generate_reports`**

Add Executive Visual Gallery section in `README.md` and contextual embeds in `report.md`.

- [ ] **Step 3: Run pytest**

Run: `uv run pytest tests/test_delivery_manager.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add stock_analyzer/agents/delivery_manager.py tests/test_delivery_manager.py
git commit -m "feat(delivery): embed complete visual chart gallery in README and report"
```

---

### Task 7: End-to-End Pipeline Execution & Verification

**Files:**
- Execute: `uv run python -m stock_analyzer analyze AMZN`
- Execute: `uv run python -m stock_analyzer analyze AAPL`
- Full Test Suite: `uv run pytest`

- [ ] **Step 1: Run full test suite**
Run: `uv run pytest`
Expected: 48+ passed, 0 failures.

- [ ] **Step 2: Run AMZN Analysis**
Run: `uv run python -m stock_analyzer analyze AMZN`
Expected: Status COMPLETE, all 12 quality gates passed, all 6 assets generated in `research/AMZN/assets/`.

- [ ] **Step 3: Run AAPL Analysis**
Run: `uv run python -m stock_analyzer analyze AAPL`
Expected: Status COMPLETE, all 12 quality gates passed, all 6 assets generated in `research/AAPL/assets/`.

- [ ] **Step 4: Commit & Push to GitHub**
```bash
git add research/AMZN/ research/AAPL/
git commit -m "feat: complete visual chart suite generation for AMZN and AAPL"
git push origin main
```
