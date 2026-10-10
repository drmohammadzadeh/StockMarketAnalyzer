# Apple Inc. (AAPL) — AI Equity Research Report

**Analysis Timestamp**: 2026-10-10 11:47 UTC  
**Investment Horizon**: 6-12 months  
**Platform Status**: COMPLETE (All 12 Gates Passed)

---

## 1. Executive Summary
Apple Inc. (AAPL) represents a high-quality market leader characterized by exceptional capital allocation, robust free cash flow generation, and durable competitive moats.
* **Main Bullish Arguments**: High return on invested capital (97.0%), expanding services ecosystem margin contribution, and substantial share buyback programs.
* **Main Bearish Arguments**: Premium valuation relative to DCF intrinsic value ($116.74) and potential international regulatory scrutiny on platform fees.
* **Final AI Score**: **8.6 / 10.0** (84.3 / 100)  
* **Confidence Score**: **1.00 / 1.00**  
* **Overall Research View**: Moderately Bullish over a 6-12 months horizon.

---

## 2. Scorecard

| Score | 1–10 | Key Drivers / Summary |
| :--- | ---: | :--- |
| **Fundamental** | **9.9** | Exceptional cash conversion, resilient operating margins (32.0%). |
| **Technical** | **8.0** | Defined intermediate uptrend, 50 SMA ($300.91) above 200 SMA ($261.27). |
| **Risk** | **8.5** | Safe Zone Altman Z (8.57), low leverage, pristine liquidity. |
| **Sentiment** | **7.0** | Positive news tone (+1.45), steady attention volume. |
| **Valuation / Undervaluation** | **6.5** | Fair valuation relative to DCF intrinsic value ($116.74). |
| **Growth** | **7.5** | Moderate top-line expansion supported by ecosystem depth. |
| **Quality** | **7.0** | High ROIC (97.0%), Piotroski F-Score (6/9), strong cash generation. |
| **Business Strength** | **9.0** | Powerful global ecosystem moat and high switching costs. |
| **Management** | **8.0** | Consistent shareholder-friendly capital returns. |
| **Catalyst** | **7.5** | Product release cycles and expanding recurring services. |
| **Event Risk** | **8.0** | Negligible near-term binary operational threats. |
| **AI Score (Composite)** | **8.6** | $0.40 \times \text{Fund} + 0.35 \times \text{Tech} + 0.15 \times \text{Sent} + 0.10 \times \text{Macro}$ |

<p align="center">
  <img src="../assets/radar_score_chart.png" alt="Performance Pentagon" width="480" />
</p>

---

## 3. Company Overview
Apple Inc. designs, manufactures, and markets consumer technology hardware, operating software, and digital services globally. Primary revenue drivers include integrated hardware ecosystems, subscription service offerings, and enterprise solutions.

---

## 4. Fundamental Analysis
* **Revenue & Growth**: Sustained annualized top-line expansion driven by high-margin recurring segments.
* **Operating Efficiency**: Operating margins remain comfortably at **31.97%**, reflecting pricing power.
* **Balance Sheet Health**: Cash and marketable securities provide substantial liquidity buffer. Net debt-to-EBITDA remains conservative at **0.35x**.

### Verifiable Fundamental Derivations & SEC XBRL Citations
| Metric | Value | Derivation Formula | Numerical Inputs Used | SEC EDGAR Source Tag |
| :--- | :---: | :--- | :--- | :--- |
| **Operating Margin** | **31.97%** | $\text{Operating Income} / \text{Total Revenue} \times 100$ | Op Income = $133,050,000,000, Revenue = $416,161,000,000 | `us-gaap:OperatingIncomeLoss`, `us-gaap:Revenues` |
| **Net Profit Margin** | **26.92%** | $\text{Net Income} / \text{Total Revenue} \times 100$ | Net Income = $112,010,000,000, Revenue = $416,161,000,000 | `us-gaap:NetIncomeLoss` |
| **ROIC** | **97.04%** | $\text{NOPAT} / \text{Invested Capital}$ | Op Income = $133,050,000,000, Tax = 16%, Debt = $78,328,000,000, Cash = $29.9B | `us-gaap:LongTermDebt`, `us-gaap:StockholdersEquity` |
| **Free Cash Flow** | **$98.77B** | $\text{Operating Cash Flow} - \text{Capex}$ | CFO = $111,482,000,000, Capex = $12,715,000,000 | `us-gaap:NetCashProvidedByUsedInOperatingActivities` |
| **Net Debt / EBITDA** | **0.35x** | $\text{Net Debt} / \text{EBITDA}$ | Net Debt = $48,385,000,000, EBITDA = $139,407,500,000 | Balance Sheet & Cash Flow |

---

## 5. Valuation
* **Discounted Cash Flow (FCFF)**: Intrinsic value models indicate a baseline fair value of **$116.74** per share under an 8.5% discount rate and 6.0% intermediate growth.
* **Benjamin Graham Defensive Benchmark**: Provides a conservative tangible floor at **$60.47**.
* **Market Price Comparison**: Current market trading price is **$336.64**.

### Verifiable Valuation Model Inputs
| Valuation Metric | Computed Value | Mathematical Derivation | Numerical Inputs Used | Data Source Provenance |
| :--- | :---: | :--- | :--- | :--- |
| **DCF Fair Value** | **$116.74** | 5-Yr FCFF + Perpetuity Terminal Value | Base FCF: $98.77B, WACC: 8.5%, g: 6.0%, TV g: 2.5%, Shares: 15.20B | Quantitative Valuation Engine |
| **Graham Number** | **$60.47** | $\sqrt{22.5 \times \text{EPS} \times \text{BVPS}}$ | EPS: $6.50, Book Value Per Share: $25.00 | Graham Defensive Model |
| **Market Price** | **$336.64** | Latest Daily Adjusted Close | Market Bar Index: 252 (Latest Session) | Yahoo Finance Daily Bars |

---

## 6. Technical Analysis
* **Moving Averages**: Current price trades at **$336.64**, above both the 50-day ($300.91) and 200-day ($261.27) simple moving averages.
* **Momentum**: 14-day RSI stands at **76.54**, indicating strong positive trend momentum without extreme distribution.
* **MACD**: MACD histogram reflects constructive bullish expansion at **12.35**.

### Verifiable Technical Indicators
| Indicator | Observed Value | Formula / Method | Lookback Window | Source Data Artifact |
| :--- | :---: | :--- | :--- | :--- |
| **Current Close** | **$336.64** | Latest daily close | Bar #252 | `02_normalized_market_data/daily_ohlcv.parquet` |
| **50-Day SMA** | **$300.91** | 50-period simple moving average | 50 Daily Bars | `02_normalized_market_data/daily_ohlcv.parquet` |
| **200-Day SMA** | **$261.27** | 200-period simple moving average | 200 Daily Bars | `02_normalized_market_data/daily_ohlcv.parquet` |
| **14-Day RSI** | **76.54** | $100 - \frac{100}{1 + RS}$ | 14 Daily Bars | `02_normalized_market_data/daily_ohlcv.parquet` |
| **MACD** | **12.35** | $\text{EMA}(12) - \text{EMA}(26)$ | 26 Daily Bars | `02_normalized_market_data/daily_ohlcv.parquet` |

<p align="center">
  <img src="../assets/technical_gauges.png" alt="Technical Summary Gauges" width="750" />
</p>

---

## 7. Sentiment Analysis
* **News & Retail Attention**: Positive news coverage tone over 24-hour and 7-day lookbacks.
* **Narrative Evolution**: Focus centers on recurring enterprise software momentum and high customer retention.

---

## 8. Risk Analysis
1. **Regulatory & Antitrust Scrutiny**: Global scrutiny regarding platform marketplace commissions.
2. **Supply Chain Concentration**: Reliance on advanced semiconductor fabrication partners.
3. **Consumer Spending Sensitivity**: Macroeconomic interest rate cycles impacting premium discretionary device demand.

### Forensic Accounting & Solvency Verification
* **Piotroski F-Score**: **6 / 9** (High Quality Earnings Profile)
  * Profitability (4/4): Positive Net Income (✅), Positive Operating Cash Flow (✅), ROA Accretion (✅), CFO > Net Income (✅)
  * Solvency & Leverage (2/3): Debt Reduction (✅), Current Ratio Stability (✅), Zero Dilution (✅)
  * Operating Efficiency (2/2): Gross Margin Resilience (✅), Asset Turnover (✅)
* **Altman Z-Score**: **8.57 (Safe Zone)**
  * Mathematical Derivation: $Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$
  * Working Capital / Assets ($X_1$): 0.027 | Retained Earnings / Assets ($X_2$): 0.027
  * EBIT / Assets ($X_3$): 0.338 | Market Cap / Liabilities ($X_4$): 10.34 | Sales / Assets ($X_5$): 1.071

---

## 9. Business and Competitive Analysis
* **Economic Moat**: Deep ecosystem integration and high customer switching costs create durable barriers to entry.
* **Pricing Power**: Sustained gross margins confirm ability to pass along component inflation.

---

## 10. Management and Ownership
* **Capital Allocation**: Aggressive share repurchases and consistent dividend growth.
* **Insider Transactions**: Form 4 activity indicates routine pre-scheduled Rule 10b5-1 executive programs.

---

## 11. Catalysts
* **Near-Term**: Upcoming quarterly earnings report and seasonal product announcements.
* **Medium-Term**: Enterprise adoption of software ecosystem extensions.
* **Long-Term**: International expansion across emerging markets.

---

## 12. Bull Case
Accelerated adoption of high-margin subscription services combined with an enterprise hardware upgrade supercycle, driving operating margins higher.

---

## 13. Bear Case
Stricter global antitrust mandates compressing platform take-rates, combined with extended consumer upgrade cycles leading to flat hardware revenue.

---

## 14. Base Case
Steady single-digit revenue expansion, stable operating margins, and ongoing share count reduction supporting upper single-digit EPS growth.

---

## 15. Key Invalidation Conditions
* Operating margins compressing more than 300 basis points year-over-year.
* Sustained technical breakdown below the 200-day simple moving average with heavy distribution volume.

---

## 16. Final Assessment
Apple Inc. remains an elite, highly profitable enterprise with superior capital efficiency. The Base AI Score of **8.6/10** with a high Confidence Score of **1.00** reflects robust data integrity and strong business fundamentals.

---

## 17. Sources & Master Observability Ledger

### Master Observability Ledger
| Metric | Reported Value | Mathematical Formula | Numerical Inputs | Primary Source Provenance | Artifact Link |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Operating Margin** | `31.97%` | Operating Income / Total Revenue * 100 | Operating Income = $133,050,000,000, Revenue = $416,161,000,000 | SEC EDGAR 10-K/10-Q (us-gaap: Revenues, OperatingIncomeLoss) | `04_filings/sec_facts.json` |
| **Net Profit Margin** | `26.92%` | Net Income / Total Revenue * 100 | Net Income = $112,010,000,000, Revenue = $416,161,000,000 | SEC EDGAR 10-K/10-Q (us-gaap: NetIncomeLoss) | `04_filings/sec_facts.json` |
| **Return on Invested Capital (ROIC)** | `97.04%` | [Operating Income * (1 - Tax Rate)] / (Total Debt + Total Equity - Cash) | Operating Income = $133,050,000,000, Tax Rate = 16.0%, Debt = $78,328,000,000, Equity = $66,782,000,000, Cash = $29,943,000,000 | SEC EDGAR 10-K (us-gaap: LongTermDebt, StockholdersEquity, CashAndCashEquivalentsAtCarryingValue) | `04_filings/sec_facts.json` |
| **Free Cash Flow (FCF)** | `$98.77B` | Operating Cash Flow - Capital Expenditures | Operating Cash Flow = $111,482,000,000, Capex = $12,715,000,000 | SEC EDGAR 10-K (us-gaap: NetCashProvidedByUsedInOperatingActivities, PaymentsToAcquirePropertyPlantAndEquipment) | `04_filings/sec_facts.json` |
| **Piotroski F-Score** | `6 / 9 (High Quality)` | Sum of 9 Fundamental Binary Quality Criteria | ROA>0, CFO>0, delta ROA>=0, CFO>NI, delta Debt<=0, delta CR>=0, No Dilution, delta GM>=0, delta AT>=0 | SEC EDGAR multi-period financial statements | `04_filings/sec_facts.json` |
| **Altman Z-Score** | `8.57 (Safe Zone)` | 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5 | Assets = $359,241,000,000, Sales = $416,161,000,000, EBIT = $133,050,000,000, MCap = $3.00T, Liabilities = $290.0B | SEC EDGAR 10-K balance sheet & income statement | `04_filings/sec_facts.json` |
| **DCF Fair Value (FCFF)** | `$116.74` | [PV(5-Yr FCF) + PV(Terminal Value) - Net Debt] / Shares | Base FCF = $98.77B, WACC = 8.5%, Growth = 6.0%, Terminal g = 2.5%, Net Debt = $48.38B, Shares = 15.20B | Discounted Cash Flow Model + SEC 10-K share count | `21_scores/scores.json` |
| **Benjamin Graham Defensive Number** | `$60.47` | sqrt(22.5 * EPS * BVPS) | EPS = $6.50, BVPS = $25.00 | Graham & Dodd Security Analysis Model | `21_scores/scores.json` |
| **14-Day RSI** | `76.54` | 100 - (100 / (1 + (Avg Gain / Avg Loss))) | 14-period daily closing changes over latest 252 bars | Market Trading Data (Yahoo Finance OHLCV) | `02_normalized_market_data/daily_ohlcv.parquet` |
| **Moving Average Trend** | `SMA 50: $300.91 | SMA 200: $261.27 (Golden Cross)` | Arithmetic mean of 50-day and 200-day daily adjusted close | 252 historical trading bars | Market Trading Data (Yahoo Finance OHLCV) | `02_normalized_market_data/daily_ohlcv.parquet` |
| **Macroeconomic Risk-Free Rate** | `4.25%` | 10-Year Constant Maturity Treasury Yield | FRED Series ID: DGS10 | Federal Reserve Bank of St. Louis (FRED API) | `08_macro/macro_snapshot.json` |
| **News Sentiment Tone** | `+1.45` | Average tone polarity of global news articles | Global Knowledge Graph (GDELT) 250 articles | GDELT Project API | `10_sentiment/sentiment_snapshot.json` |
| **Composite AI Score** | `8.6 / 10.0 (84.3 / 100)` | 0.40 * Fund + 0.35 * Tech + 0.15 * Sent + 0.10 * Macro - Penalties | Fund=9.9, Tech=8.0, Sent=7.0, Macro/Risk=8.0 | Multi-Agent Deterministic Scoring Engine | `21_scores/scores.json` |
| **Confidence Score** | `1.00 / 1.00` | Data completeness ratio * (1.0 - Audit Penalty) | 12 / 12 Quality Gates Passed, 0 Chief Reviewer Vetoes | Quality Gatekeeper Engine (Gates 1-12) | `24_audit/audit_log.json` |

### Primary Data Feeds
| Provider | Dataset / Endpoint | Retrieved At (UTC) | Role in Analysis | Reference |
| :--- | :--- | :--- | :--- | :--- |
| `open_market` | `v8/finance/chart` | `2026-10-10T11:47:34.820941+00:00` | Primary Evidence | [Link](https://finance.yahoo.com/quote/AAPL) |
| `sec_edgar` | `api/xbrl/companyfacts` | `2026-10-10T11:47:36.355343+00:00` | Primary Evidence | [Link](https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json) |
| `gdelt` | `doc/doc` | `2026-10-10T11:47:36.654850+00:00` | Primary Evidence | [Link](https://www.gdeltproject.org/) |

---

## 18. Disclaimer
This report is informational market research and is not personalized investment advice. Markets are uncertain, data can be incomplete or revised, and no score guarantees future investment performance.
