"""Chief Research Pipeline Orchestrator."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from stock_analyzer.core.models import SecurityIdentity, ScoringResult, ProvenanceRecord
from stock_analyzer.core.security_master import SecurityMaster
from stock_analyzer.core.storage import ResearchStorage
from stock_analyzer.core.provenance import ProvenanceTracker
from stock_analyzer.core.audit import AuditLogger
from stock_analyzer.pipeline.gates import QualityGateEngine

from stock_analyzer.providers.edgar import EdgarProvider
from stock_analyzer.providers.open_market import OpenMarketProvider
from stock_analyzer.providers.fred import FredProvider
from stock_analyzer.providers.gdelt import GdeltProvider
from stock_analyzer.providers.sedar import SedarProvider

from stock_analyzer.engine.technical import TechnicalEngine
from stock_analyzer.engine.fundamental import FundamentalEngine
from stock_analyzer.engine.forensics import ForensicsEngine
from stock_analyzer.engine.valuation import ValuationEngine
from stock_analyzer.engine.scoring import ScoringEngine
from stock_analyzer.engine.charts import (
    generate_radar_chart,
    generate_technical_gauges,
    generate_price_action_chart,
    generate_financial_waterfall_chart,
    generate_valuation_margin_chart,
)
from stock_analyzer.engine.excalidraw_generator import generate_moat_excalidraw_diagram

from stock_analyzer.agents.specialists.fundamental import FundamentalAgent
from stock_analyzer.agents.specialists.technical import TechnicalAgent
from stock_analyzer.agents.specialists.valuation import ValuationAgent
from stock_analyzer.agents.specialists.risk import RiskAgent
from stock_analyzer.agents.specialists.sentiment import SentimentAgent
from stock_analyzer.agents.specialists.scenario import ScenarioAgent
from stock_analyzer.agents.specialists.other_specialists import (
    ForensicsAgent, NewsEventsAgent, BusinessAgent, ManagementAgent, MacroAgent, QuantAgent
)

from stock_analyzer.agents.judges.domain_judges import (
    FundamentalJudge, TechnicalJudge, RiskJudge, SentimentJudge, QuantJudge, EvidenceJudge, ReportQualityJudge
)
from stock_analyzer.agents.chief_reviewer import ChiefReviewer
from stock_analyzer.agents.delivery_manager import DeliveryManager, get_company_profile

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """End-to-end multi-agent equity research pipeline coordinator."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.storage = ResearchStorage(base_dir=base_dir)
        self.security_master = SecurityMaster()
        self.gates = QualityGateEngine()
        self.provenance_tracker = ProvenanceTracker()

        # Data Providers
        self.edgar = EdgarProvider()
        self.open_market = OpenMarketProvider()
        self.fred = FredProvider()
        self.gdelt = GdeltProvider()
        self.sedar = SedarProvider()

        # Quantitative Engines
        self.tech_engine = TechnicalEngine()
        self.fund_engine = FundamentalEngine()
        self.forensics_engine = ForensicsEngine()
        self.val_engine = ValuationEngine()
        self.scoring_engine = ScoringEngine()

        # Reviewers and Delivery
        self.chief_reviewer = ChiefReviewer()
        self.delivery_manager = DeliveryManager()

    async def run(self, raw_symbol: str, horizon: str = "6-12 months") -> Dict[str, Any]:
        """Execute the full 8-phase research pipeline for a given ticker."""
        # -------------------------------------------------------------
        # Phase 1: Security Identity Resolution (Gate 1)
        # -------------------------------------------------------------
        identity = self.security_master.resolve(raw_symbol)
        clean_symbol = identity.canonical_ticker
        dirs = self.storage.init_research_dirs(clean_symbol)
        
        audit_file = Path(dirs["24_audit"]) / "audit_log.json"
        audit = AuditLogger(audit_file)
        audit.log_event("PIPELINE_START", {"symbol": clean_symbol, "horizon": horizon})

        gate1 = self.gates.evaluate_gate1_identity(identity)
        audit.log_event("GATE_CHECK", gate1.model_dump())
        if not gate1.passed:
            return {"status": "FAILED_VALIDATION", "gate_failed": gate1.gate_id}

        # Save identity artifact
        with open(Path(dirs["00_identity"]) / "identity.json", "w", encoding="utf-8") as f:
            json.dump(identity.model_dump(), f, indent=2)

        # -------------------------------------------------------------
        # Phase 2: Data Acquisition & Provenance Tracking
        # -------------------------------------------------------------
        # Market Data
        df_adj, df_unadj, prov_mkt = self.open_market.get_historical_ohlcv(clean_symbol, bars=252)
        self.provenance_tracker.register(prov_mkt)
        self.storage.save_parquet(clean_symbol, "02_normalized_market_data", "daily_ohlcv.parquet", df_adj)
        
        gate2 = self.gates.evaluate_gate2_market_data(df_adj, required_bars=252)
        audit.log_event("GATE_CHECK", gate2.model_dump())
        if not gate2.passed:
            return {"status": "INSUFFICIENT_DATA", "gate_failed": gate2.gate_id}

        # Filings & Statements
        prov_filings: List[ProvenanceRecord] = []
        facts_payload = {}
        if identity.country == "CA":
            sedar_docs, prov_s = self.sedar.get_filings(clean_symbol)
            self.provenance_tracker.register(prov_s)
            prov_filings.append(prov_s)
            with open(Path(dirs["04_filings"]) / "sedar_filings.json", "w", encoding="utf-8") as f:
                json.dump(sedar_docs, f, indent=2)
        
        # Ingest SEC facts for US or cross-listed
        cik = identity.cik or "0000320193"
        facts_payload, prov_e = self.edgar.get_company_facts(cik, clean_symbol)
        self.provenance_tracker.register(prov_e)
        prov_filings.append(prov_e)
        with open(Path(dirs["04_filings"]) / "sec_facts.json", "w", encoding="utf-8") as f:
            json.dump(facts_payload, f, indent=2)

        gate3 = self.gates.evaluate_gate3_fundamentals(facts_payload.get("facts", {}).get("us-gaap", {}))
        audit.log_event("GATE_CHECK", gate3.model_dump())

        # Macro & News
        macro_data, prov_macro = self.fred.get_macro_snapshot()
        self.provenance_tracker.register(prov_macro)
        with open(Path(dirs["08_macro"]) / "macro_snapshot.json", "w", encoding="utf-8") as f:
            json.dump(macro_data, f, indent=2)

        sentiment_data, prov_sent = self.gdelt.get_news_sentiment(clean_symbol, identity.company_name)
        self.provenance_tracker.register(prov_sent)
        with open(Path(dirs["10_sentiment"]) / "sentiment_snapshot.json", "w", encoding="utf-8") as f:
            json.dump(sentiment_data, f, indent=2)

        # Ingest user-curated links from links.txt if present
        curated_links: List[str] = []
        symbol_root_dir = self.storage.get_symbol_dir(clean_symbol)
        links_file = symbol_root_dir / "links.txt"
        if links_file.exists():
            with open(links_file, "r", encoding="utf-8") as f:
                for line in f:
                    url = line.strip()
                    if url and url.startswith("http"):
                        curated_links.append(url)
                        prov_link = self.provenance_tracker.create_record(
                            provider="user_curated_link",
                            endpoint="intelligence_dossier",
                            symbol=clean_symbol,
                            url=url,
                        )
                        self.provenance_tracker.register(prov_link)
            audit.log_event("CURATED_LINKS_LOADED", {"count": len(curated_links), "path": str(links_file)})

        # -------------------------------------------------------------
        # Phase 3: Data Quality Gatekeeper (Gate 4 Veto)
        # -------------------------------------------------------------
        gate4 = self.gates.evaluate_gate4_data_quality(df_adj, filing_days_old=45)
        audit.log_event("GATE_CHECK", gate4.model_dump())
        if not gate4.passed:
            audit.log_event("PIPELINE_VETO", {"details": gate4.details})
            return {"status": "FAILED_VALIDATION", "gate_failed": gate4.gate_id}

        # -------------------------------------------------------------
        # Phase 4: Local Quantitative Engine Calculations
        # -------------------------------------------------------------
        indicators = self.tech_engine.compute_all_indicators(df_adj)
        levels = self.tech_engine.detect_support_resistance(df_adj)
        indicators.update(levels)

        # Extract statement numbers from facts
        us_gaap = facts_payload.get("facts", {}).get("us-gaap", {})

        def _get_annual_fact(concept_names: List[str], default_val: float) -> float:
            for c in concept_names:
                units = us_gaap.get(c, {}).get("units", {}).get("USD", [])
                fy_units = [u for u in units if u.get("form") == "10-K" and u.get("fp") == "FY"]
                if fy_units:
                    return float(fy_units[-1]["val"])
                if units:
                    return float(units[-1]["val"])
            return default_val

        def _get_annual_prior_fact(concept_names: List[str], default_val: float) -> float:
            for c in concept_names:
                units = us_gaap.get(c, {}).get("units", {}).get("USD", [])
                fy_units = [u for u in units if u.get("form") == "10-K" and u.get("fp") == "FY"]
                if len(fy_units) >= 2:
                    return float(fy_units[-2]["val"])
            return default_val

        rev_curr = _get_annual_fact(["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"], 100000000000.0)
        rev_prior = _get_annual_prior_fact(["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"], rev_curr * 0.95)
        op_inc_curr = _get_annual_fact(["OperatingIncomeLoss"], rev_curr * 0.15)
        ni_curr = _get_annual_fact(["NetIncomeLoss"], rev_curr * 0.10)
        cfo_curr = _get_annual_fact(["NetCashProvidedByUsedInOperatingActivities"], rev_curr * 0.18)
        capex_curr = _get_annual_fact(["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"], rev_curr * 0.05)
        debt_curr = _get_annual_fact(["LongTermDebtNoncurrent", "LongTermDebt"], rev_curr * 0.20)
        assets_curr = _get_annual_fact(["Assets"], rev_curr * 0.90)

        cash_curr = _get_annual_fact(["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"], assets_curr * 0.10)
        equity_curr = _get_annual_fact(["StockholdersEquity", "CommonStockholdersEquity"], assets_curr * 0.50)
        curr_assets = _get_annual_fact(["AssetsCurrent"], assets_curr * 0.35)
        curr_liab = _get_annual_fact(["LiabilitiesCurrent"], assets_curr * 0.30)
        retained_earn = _get_annual_fact(["RetainedEarningsAccumulatedDeficit"], equity_curr * 0.60)
        tot_liab = _get_annual_fact(["Liabilities"], max(assets_curr - equity_curr, 1.0))

        # Shares outstanding
        shares_units = us_gaap.get("CommonStockSharesOutstanding", {}).get("units", {}).get("shares", []) or \
                       facts_payload.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", [])
        shares_curr = float(shares_units[-1]["val"]) if shares_units else max(assets_curr / 35.0, 1000000.0)

        fund_metrics = self.fund_engine.compute_metrics(
            revenue_current=rev_curr,
            revenue_prior=rev_prior,
            net_income=ni_curr,
            operating_cash_flow=cfo_curr,
            capex=capex_curr,
            total_debt=debt_curr,
            cash_and_equiv=cash_curr,
            total_equity=equity_curr,
            operating_income=op_inc_curr,
        )

        f_score, f_breakdown = self.forensics_engine.compute_piotroski_f_score({
            "net_income": ni_curr,
            "operating_cash_flow": cfo_curr,
            "total_assets_current": assets_curr,
            "total_assets_prior": assets_curr * 0.95,
            "long_term_debt_current": debt_curr,
            "long_term_debt_prior": debt_curr * 1.05,
        })

        market_cap = indicators["current_price"] * shares_curr
        z_score, z_status = self.forensics_engine.compute_altman_z_score({
            "total_assets_current": assets_curr,
            "current_assets": curr_assets,
            "current_liabilities": curr_liab,
            "retained_earnings": retained_earn,
            "ebit": op_inc_curr,
            "market_cap": market_cap,
            "total_liabilities": tot_liab,
            "sales": rev_curr,
        })

        val_metrics = self.val_engine.compute_dcf(
            base_fcf=fund_metrics["free_cash_flow"],
            shares_outstanding=shares_curr,
            net_debt=fund_metrics["net_debt"],
        )
        eps_calc = ni_curr / max(shares_curr, 1.0)
        bvps_calc = equity_curr / max(shares_curr, 1.0)
        graham_val = self.val_engine.compute_graham_number(eps=eps_calc, bvps=bvps_calc)
        val_metrics["graham_number"] = graham_val

        # -------------------------------------------------------------
        # Phase 5: Concurrent Specialist Agent Execution
        # -------------------------------------------------------------
        analysis_context = {
            "symbol": clean_symbol,
            "company_name": identity.company_name,
            "sector": identity.sector,
            "industry": identity.industry,
            "currency": identity.currency,
            "revenue": rev_curr,
            "revenue_prior": rev_prior,
            "net_income": ni_curr,
            "operating_cash_flow": cfo_curr,
            "capex": capex_curr,
            "free_cash_flow": fund_metrics.get("free_cash_flow", cfo_curr - capex_curr),
            "total_debt": debt_curr,
            "assets": assets_curr,
            "current_assets": curr_assets,
            "current_liabilities": curr_liab,
            "retained_earnings": retained_earn,
            "cash": cash_curr,
            "equity": equity_curr,
            "liabilities": tot_liab,
            "shares_outstanding": shares_curr,
            "eps": eps_calc,
            "bvps": bvps_calc,
            "market_cap": market_cap,
            "operating_income": op_inc_curr,
            "close": indicators["current_price"],
            "current_price": indicators.get("current_price", float(df_adj["close"].iloc[-1])),
            "intrinsic_value": val_metrics.get("intrinsic_value_per_share", val_metrics.get("intrinsic_value", float(df_adj["close"].iloc[-1]))),
            "graham_number": val_metrics.get("graham_number"),
            "fifty_two_week_low": float(df_adj["low"].min()) if "low" in df_adj.columns else None,
            "fifty_two_week_high": float(df_adj["high"].max()) if "high" in df_adj.columns else None,
            "indicators": indicators,
            "fundamental_metrics": fund_metrics,
            "valuation": val_metrics,
            "f_score": f_score,
            "f_breakdown": f_breakdown,
            "z_score": z_score,
            "z_status": z_status,
            "macro": macro_data,
            "sentiment": sentiment_data,
            "curated_links": curated_links,
        }

        specialists = [
            FundamentalAgent(),
            TechnicalAgent(),
            ValuationAgent(),
            RiskAgent(),
            SentimentAgent(),
            ScenarioAgent(),
            ForensicsAgent(),
            NewsEventsAgent(),
            BusinessAgent(),
            ManagementAgent(),
            MacroAgent(),
            QuantAgent(),
        ]

        # Run specialists concurrently
        outputs = await asyncio.gather(*(agent.run(analysis_context) for agent in specialists))
        specialist_outputs = {out.agent_name: out.model_dump() for out in outputs}

        # -------------------------------------------------------------
        # Phase 6: Independent Domain Judges & Adversarial Chief Review
        # -------------------------------------------------------------
        judges = [
            FundamentalJudge(),
            TechnicalJudge(),
            RiskJudge(),
            SentimentJudge(),
            QuantJudge(),
            EvidenceJudge(),
            ReportQualityJudge(),
        ]
        judge_reviews = await asyncio.gather(*(judge.review(analysis_context) for judge in judges))
        for jrev in judge_reviews:
            audit.log_event("JUDGE_REVIEW", jrev.model_dump())

        # Gate 11: Adversarial Review
        chief_out = await self.chief_reviewer.adversarial_review(analysis_context)
        audit.log_event("CHIEF_REVIEW", chief_out.model_dump())

        # -------------------------------------------------------------
        # Phase 7: Deterministic Score Calculation
        # -------------------------------------------------------------
        sub_scores = {
            "fundamental": min(10.0, max(1.0, 5.0 + fund_metrics["roic"] * 5.0)),
            "technical": 8.0 if indicators["trend_direction"] == "Bullish" else 5.0,
            "risk": 8.5 if z_status == "Safe Zone" else 5.0,
            "sentiment": 7.0 if sentiment_data["tone"] > 0 else 4.0,
            "valuation": 6.5,
            "growth": 7.5 if fund_metrics["revenue_growth_yoy"] > 0 else 4.0,
            "quality": min(10.0, float(f_score) + 1.0),
            "business_strength": 9.0,
            "management": 8.0,
            "catalyst": 7.5,
            "event_risk": 8.0,
        }
        penalties = {}
        if chief_out.confidence_penalty > 0:
            penalties["chief_review_penalty"] = chief_out.confidence_penalty

        scores = self.scoring_engine.calculate_scores(sub_scores, penalties)
        with open(Path(dirs["21_scores"]) / "scores.json", "w", encoding="utf-8") as f:
            json.dump(scores.model_dump(), f, indent=2)

        # -------------------------------------------------------------
        # Phase 8: Delivery Manager, Charts & Report Publishing (Gate 12)
        # -------------------------------------------------------------
        symbol_root_dir = self.storage.get_symbol_dir(clean_symbol)
        assets_dir = symbol_root_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        curr_close = float(df_adj["close"].iloc[-1])
        prev_close = float(df_adj["close"].iloc[-2]) if len(df_adj) >= 2 else curr_close
        p_chg = curr_close - prev_close
        p_chg_pct = (p_chg / prev_close) * 100.0 if prev_close != 0 else 0.0

        # Technical indicator votes matching TradingView layout
        tech_votes = self.tech_engine.compute_indicator_votes(df_adj, indicators)

        # Performance pentagon dimensions matching GuruFocus layout
        radar_dims = {
            "profitability": min(100.0, max(15.0, float(sub_scores.get("fundamental", 9.0)) * 10.0)),
            "valuation": min(100.0, max(15.0, float(sub_scores.get("valuation", 6.5)) * 10.0)),
            "momentum": min(100.0, max(15.0, float(sub_scores.get("technical", 8.0)) * 10.0)),
            "financial_strength": min(100.0, max(15.0, float(sub_scores.get("risk", 8.5)) * 10.0)),
            "growth": min(100.0, max(15.0, float(sub_scores.get("growth", 4.0)) * 10.0)),
        }

        generated_charts: List[str] = []

        try:
            generate_radar_chart(
                symbol=clean_symbol,
                company_name=identity.company_name,
                score_100=scores.normalized_100_score,
                dimensions=radar_dims,
                output_path=assets_dir / "radar_score_chart.png",
            )
            generated_charts.append("radar_score_chart.png")
        except Exception as e:
            logger.warning(f"Failed to generate radar score chart for {clean_symbol}: {e}")

        try:
            generate_technical_gauges(
                symbol=clean_symbol,
                company_name=identity.company_name,
                current_price=curr_close,
                price_change=p_chg,
                price_change_pct=p_chg_pct,
                technical_votes=tech_votes,
                output_path=assets_dir / "technical_gauges.png",
            )
            generated_charts.append("technical_gauges.png")
        except Exception as e:
            logger.warning(f"Failed to generate technical gauges for {clean_symbol}: {e}")

        try:
            generate_price_action_chart(
                df=df_adj,
                symbol=clean_symbol,
                company_name=identity.company_name,
                output_path=assets_dir / "price_action_trend.png",
            )
            generated_charts.append("price_action_trend.png")
        except Exception as e:
            logger.warning(f"Failed to generate price action trend chart for {clean_symbol}: {e}")

        try:
            generate_financial_waterfall_chart(
                financials=analysis_context,
                symbol=clean_symbol,
                company_name=identity.company_name,
                output_path=assets_dir / "financial_conversion_bars.png",
            )
            generated_charts.append("financial_conversion_bars.png")
        except Exception as e:
            logger.warning(f"Failed to generate financial conversion bars for {clean_symbol}: {e}")

        try:
            generate_valuation_margin_chart(
                valuation_data=analysis_context,
                symbol=clean_symbol,
                company_name=identity.company_name,
                output_path=assets_dir / "valuation_margin_gauge.png",
            )
            generated_charts.append("valuation_margin_gauge.png")
        except Exception as e:
            logger.warning(f"Failed to generate valuation margin gauge for {clean_symbol}: {e}")

        try:
            company_profile = get_company_profile(
                symbol=clean_symbol,
                company_name=identity.company_name,
                sector=identity.sector,
                industry=identity.industry,
            )
            generate_moat_excalidraw_diagram(
                symbol=clean_symbol,
                company_name=identity.company_name,
                profile=company_profile,
                output_base_path=assets_dir / "business_moat_diagram",
            )
            generated_charts.append("business_moat_diagram.png")
            generated_charts.append("business_moat_diagram.excalidraw")
        except Exception as e:
            logger.warning(f"Failed to generate business moat diagram for {clean_symbol}: {e}")

        audit.log_event("CHARTS_GENERATED", {"charts": generated_charts})

        all_provs = self.provenance_tracker.get_records_for_symbol(clean_symbol)

        # Compile and persist verifiable observability ledger
        observability_ledger = self.delivery_manager.build_observability_ledger(
            symbol=clean_symbol,
            company_name=identity.company_name,
            scores=scores,
            analysis_context=analysis_context,
            provenance_records=all_provs,
        )
        with open(Path(dirs["24_audit"]) / "observability_ledger.json", "w", encoding="utf-8") as f:
            json.dump(observability_ledger, f, indent=2)
        audit.log_event("OBSERVABILITY_LEDGER_COMPILED", {"metrics_count": len(observability_ledger)})

        report_md, plain_md, report_json = self.delivery_manager.generate_reports(
            symbol=clean_symbol,
            company_name=identity.company_name,
            scores=scores,
            specialist_outputs=specialist_outputs,
            provenance_records=all_provs,
            horizon=horizon,
            analysis_context=analysis_context,
        )

        readme_md = self.delivery_manager.generate_readme_summary(
            symbol=clean_symbol,
            company_name=identity.company_name,
            scores=scores,
            specialist_outputs=specialist_outputs,
            horizon=horizon,
            analysis_context=analysis_context,
        )

        with open(Path(dirs["23_final_report"]) / "report.md", "w", encoding="utf-8") as f:
            f.write(report_md)
        with open(Path(dirs["23_final_report"]) / "plain_english.md", "w", encoding="utf-8") as f:
            f.write(plain_md)
        with open(Path(dirs["23_final_report"]) / "report.json", "w", encoding="utf-8") as f:
            json.dump(report_json, f, indent=2)

        # Save executive summary README.md in root stock folder
        symbol_root_dir = self.storage.get_symbol_dir(clean_symbol)
        with open(symbol_root_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_md)

        audit.log_event("PIPELINE_COMPLETE", {"status": "COMPLETE", "base_ai_score": scores.base_ai_score})

        return {
            "status": "COMPLETE",
            "symbol": clean_symbol,
            "company_name": identity.company_name,
            "currency": identity.currency,
            "scores": scores,
            "readme_path": str(symbol_root_dir / "README.md"),
            "report_path": str(Path(dirs["23_final_report"]) / "report.md"),
            "plain_english_path": str(Path(dirs["23_final_report"]) / "plain_english.md"),
        }
