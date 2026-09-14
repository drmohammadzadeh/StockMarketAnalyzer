"""Technical Indicator and Volatility Calculation Engine."""

from typing import Any, Dict
import numpy as np
import pandas as pd


class TechnicalEngine:
    """Computes deterministic technical analysis indicators from validated OHLCV data."""

    def compute_all_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute the full suite of technical indicators required by the platform."""
        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # --- Trend ---
        sma_20 = float(close.rolling(window=20).mean().iloc[-1])
        sma_50 = float(close.rolling(window=50).mean().iloc[-1]) if len(close) >= 50 else sma_20
        sma_200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else sma_50
        ema_20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])

        # ADX 14 calculation
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_14 = float(tr.ewm(span=14, adjust=False).mean().iloc[-1])

        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(span=14, adjust=False).mean() / tr.replace(0, 1)
        minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(span=14, adjust=False).mean() / tr.replace(0, 1)
        dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1) * 100
        adx_14 = float(dx.ewm(span=14, adjust=False).mean().iloc[-1])

        # --- Momentum ---
        # Wilder's RSI 14
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-9)
        rsi_series = 100 - (100 / (1 + rs))
        rsi_14 = float(rsi_series.iloc[-1])

        # MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - macd_signal

        roc_20 = float(((close - close.shift(20)) / close.shift(20).replace(0, 1) * 100).iloc[-1])

        # --- Volatility ---
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        bb_upper = float((bb_middle + 2 * bb_std).iloc[-1])
        bb_lower = float((bb_middle - 2 * bb_std).iloc[-1])
        realized_vol_20 = float((close.pct_change().rolling(20).std() * np.sqrt(252) * 100).iloc[-1])

        # --- Volume ---
        rvol_20 = float((volume / volume.rolling(20).mean().replace(0, 1)).iloc[-1])
        
        # OBV
        direction = np.sign(close.diff().fillna(0))
        obv = float((direction * volume).cumsum().iloc[-1])

        # VWAP
        typical_price = (high + low + close) / 3
        vwap = float(((typical_price * volume).cumsum() / volume.cumsum().replace(0, 1)).iloc[-1])

        current_price = float(close.iloc[-1])

        return {
            "current_price": round(current_price, 2),
            "SMA_20": round(sma_20, 2),
            "SMA_50": round(sma_50, 2),
            "SMA_200": round(sma_200, 2),
            "EMA_20": round(ema_20, 2),
            "ADX_14": round(adx_14, 2),
            "RSI_14": round(rsi_14, 2),
            "MACD_line": round(float(macd_line.iloc[-1]), 3),
            "MACD_signal": round(float(macd_signal.iloc[-1]), 3),
            "MACD_hist": round(float(macd_hist.iloc[-1]), 3),
            "ROC_20": round(roc_20, 2),
            "ATR_14": round(atr_14, 2),
            "BB_upper": round(bb_upper, 2),
            "BB_middle": round(float(bb_middle.iloc[-1]), 2),
            "BB_lower": round(bb_lower, 2),
            "realized_vol_20": round(realized_vol_20, 2),
            "RVOL_20": round(rvol_20, 2),
            "OBV": round(obv, 0),
            "VWAP": round(vwap, 2),
            "trend_direction": "Bullish" if current_price > sma_50 > sma_200 else ("Bearish" if current_price < sma_50 < sma_200 else "Neutral"),
        }

    def detect_support_resistance(self, df: pd.DataFrame, window: int = 60) -> Dict[str, float]:
        """Detect local swing support and resistance levels."""
        subset = df.iloc[-window:] if len(df) >= window else df
        support = float(subset["low"].min())
        resistance = float(subset["high"].max())
        return {
            "support_level": round(support, 2),
            "resistance_level": round(resistance, 2),
        }
