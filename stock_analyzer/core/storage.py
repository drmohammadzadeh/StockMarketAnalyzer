"""Research Directory and Parquet Storage Manager."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd


class ResearchStorage:
    """Manages the 25-folder structured directory architecture per analyzed security."""

    FOLDER_NAMES: List[str] = [
        "00_identity",
        "01_raw_market_data",
        "02_normalized_market_data",
        "03_corporate_actions",
        "04_filings",
        "05_financial_statements",
        "06_earnings",
        "07_company_news",
        "08_macro",
        "09_industry",
        "10_sentiment",
        "11_ownership_insiders",
        "12_fundamental_analysis",
        "13_technical_analysis",
        "14_valuation_analysis",
        "15_risk_analysis",
        "16_sentiment_analysis",
        "17_business_competitive_analysis",
        "18_macro_event_analysis",
        "19_scenario_analysis",
        "20_quant_analysis",
        "21_scores",
        "22_reviews",
        "23_final_report",
        "24_audit",
    ]

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            root = Path(__file__).resolve().parent.parent.parent
            self.base_dir = root / "research"
        else:
            self.base_dir = Path(base_dir)

    def init_research_dirs(self, symbol: str) -> Dict[str, str]:
        """Create all 25 structured directories for the given canonical ticker symbol."""
        clean_symbol = symbol.strip().upper()
        symbol_root = self.base_dir / clean_symbol
        symbol_root.mkdir(parents=True, exist_ok=True)

        paths: Dict[str, str] = {}
        for folder in self.FOLDER_NAMES:
            folder_path = symbol_root / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            paths[folder] = str(folder_path)

        return paths

    def get_symbol_dir(self, symbol: str, folder_name: str) -> Path:
        """Get the path to a specific folder for a security."""
        clean_symbol = symbol.strip().upper()
        path = self.base_dir / clean_symbol / folder_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_parquet(self, symbol: str, folder: str, filename: str, df: pd.DataFrame) -> str:
        """Save a pandas DataFrame to Parquet."""
        folder_path = self.get_symbol_dir(symbol, folder)
        file_path = folder_path / filename
        df.to_parquet(file_path, engine="pyarrow", index=True)
        return str(file_path)

    def load_parquet(self, filepath: str) -> pd.DataFrame:
        """Load a Parquet file to pandas DataFrame."""
        return pd.read_parquet(filepath, engine="pyarrow")
