"""
Macro Economic Data Fetcher for Manta trading agent.
Fetches and analyzes macroeconomic indicators.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

import pandas as pd
import requests
from loguru import logger


class EconomicCycle(Enum):
    """Economic cycle states."""
    INFLATIONARY = "inflationary"  # High inflation, rising rates
    TIGHTENING = "tightening"      # Rate hikes, slowing growth
    RECESSIONARY = "recessionary"  # Low growth, potential rate cuts
    RECOVERY = "recovery"          # Improving growth, stable rates


class MacroDataFetcher:
    """
    Fetches macroeconomic data from various sources.

    Data Sources:
    - Federal Reserve (FRED) API for interest rates, CPI
    - Yahoo Finance for DXY, VIX, Treasury yields
    - CoinGecko for crypto market data
    """

    def __init__(self, fred_api_key: Optional[str] = None):
        """
        Initialize macro data fetcher.

        Args:
            fred_api_key: FRED API key (optional, for enhanced data)
        """
        self.fred_api_key = fred_api_key
        self.fred_base_url = "https://api.stlouisfed.org/fred/series/observations"

        logger.info("Macro data fetcher initialized")

    async def get_fed_rate(self) -> Dict:
        """
        Get Federal Funds Rate data.

        Returns:
            Dictionary with current rate and trend
        """
        try:
            # Use free API or scrape data
            # For demo, we'll use approximate values
            # In production, use FRED API

            current_rate = 5.25  # As of 2024, update as needed

            return {
                "current_rate": current_rate,
                "previous_rate": 5.50,
                "trend": "decreasing",  # decreasing, stable, increasing
                "next_meeting": "2024-09-18",
                "market_expectation": "cut",
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error("Error fetching Fed rate", error=str(e))
            return {}

    async def get_cpi(self) -> Dict:
        """
        Get Consumer Price Index (CPI) data.

        Returns:
            Dictionary with CPI values and inflation rate
        """
        try:
            # Approximate values - in production use FRED API
            return {
                "cpi_value": 314.0,
                "year_over_year": 3.2,  # YoY change %
                "month_over_month": 0.3,  # MoM change %
                "core_cpi": 4.8,  # Excluding food and energy
                "trend": "decreasing",
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error("Error fetching CPI", error=str(e))
            return {}

    async def get_dxy(self, days: int = 30) -> pd.DataFrame:
        """
        Get US Dollar Index (DXY) data.

        Args:
            days: Number of days of historical data

        Returns:
            DataFrame with DXY data
        """
        try:
            # Use Yahoo Finance API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
            params = {
                "range": f"{days}d",
                "interval": "1d"
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                timestamps = data["chart"]["result"][0]["timestamp"]
                quotes = data["chart"]["result"][0]["indicators"]["quote"][0]

                df = pd.DataFrame({
                    "timestamp": pd.to_datetime(timestamps, unit="s"),
                    "open": quotes["open"],
                    "high": quotes["high"],
                    "low": quotes["low"],
                    "close": quotes["close"],
                    "volume": quotes["volume"]
                })

                df = df.dropna()
                logger.info("Got DXY data", days=days)
                return df
            else:
                logger.error("Failed to fetch DXY", status=response.status_code)
                return pd.DataFrame()

        except Exception as e:
            logger.error("Error fetching DXY", error=str(e))
            return pd.DataFrame()

    async def get_treasury_yields(self) -> Dict:
        """
        Get US Treasury yields.

        Returns:
            Dictionary with yields for different maturities
        """
        try:
            # Approximate values - in production use FRED API
            return {
                "2_year": 4.85,
                "5_year": 4.45,
                "10_year": 4.25,
                "30_year": 4.45,
                "spread_2_10": -0.60,  # 2-10 spread (inverted = recession signal)
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error("Error fetching treasury yields", error=str(e))
            return {}

    async def get_vix(self) -> Dict:
        """
        Get VIX (Volatility Index) data.

        Returns:
            Dictionary with VIX value and interpretation
        """
        try:
            # Use Yahoo Finance
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX"
            params = {"range": "1d", "interval": "1d"}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                quote = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

                # Interpret VIX level
                if quote < 15:
                    regime = "low_volatility"
                    interpretation = "Complacency, potential for sharp moves"
                elif quote < 25:
                    regime = "normal"
                    interpretation = "Normal market conditions"
                elif quote < 35:
                    regime = "elevated"
                    interpretation = "Market stress, caution advised"
                else:
                    regime = "high_volatility"
                    interpretation = "Extreme fear, potential opportunity"

                return {
                    "value": quote,
                    "regime": regime,
                    "interpretation": interpretation,
                    "timestamp": datetime.now()
                }
            else:
                logger.error("Failed to fetch VIX", status=response.status_code)
                return {}

        except Exception as e:
            logger.error("Error fetching VIX", error=str(e))
            return {}

    async def analyze_economic_cycle(self) -> Dict:
        """
        Analyze current economic cycle based on indicators.

        Returns:
            Dictionary with cycle analysis and recommendations
        """
        try:
            fed_rate = await self.get_fed_rate()
            cpi = await self.get_cpi()
            treasury = await self.get_treasury_yields()
            vix = await self.get_vix()

            # Simple rule-based cycle detection
            signals = {
                "inflation_high": cpi.get("year_over_year", 0) > 3.0,
                "rates_high": fed_rate.get("current_rate", 0) > 5.0,
                "yield_curve_inverted": treasury.get("spread_2_10", 0) < 0,
                "vix_elevated": vix.get("value", 20) > 25
            }

            # Determine cycle
            if signals["inflation_high"] and signals["rates_high"]:
                cycle = EconomicCycle.INFLATIONARY
                description = "High inflation with elevated rates"
            elif signals["rates_high"] and signals["yield_curve_inverted"]:
                cycle = EconomicCycle.TIGHTENING
                description = "Rate hikes impacting growth"
            elif signals["yield_curve_inverted"] and signals["vix_elevated"]:
                cycle = EconomicCycle.RECESSIONARY
                description = "Recession risk elevated"
            else:
                cycle = EconomicCycle.RECOVERY
                description = "Economic recovery phase"

            # Generate trading recommendations
            recommendations = self._get_cycle_recommendations(cycle)

            return {
                "cycle": cycle.value,
                "description": description,
                "signals": signals,
                "indicators": {
                    "fed_rate": fed_rate.get("current_rate"),
                    "cpi_yoy": cpi.get("year_over_year"),
                    "yield_spread": treasury.get("spread_2_10"),
                    "vix": vix.get("value")
                },
                "recommendations": recommendations,
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error("Error analyzing economic cycle", error=str(e))
            return {}

    def _get_cycle_recommendations(self, cycle: EconomicCycle) -> Dict:
        """
        Get trading recommendations based on economic cycle.

        Args:
            cycle: Current economic cycle

        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            EconomicCycle.INFLATIONARY: {
                "bias": "neutral_to_short",
                "prefer": ["commodities", "inflation_hedges", "short_duration_bonds"],
                "avoid": ["long_duration_bonds", "growth_stocks"],
                "risk_level": "high"
            },
            EconomicCycle.TIGHTENING: {
                "bias": "short",
                "prefer": ["cash", "short_duration_bonds", "value_stocks"],
                "avoid": ["high_growth", "crypto", "speculative_assets"],
                "risk_level": "high"
            },
            EconomicCycle.RECESSIONARY: {
                "bias": "short",
                "prefer": ["defensive_stocks", "bonds", "gold"],
                "avoid": ["cyclical_stocks", "crypto", "high_yield_bonds"],
                "risk_level": "very_high"
            },
            EconomicCycle.RECOVERY: {
                "bias": "long",
                "prefer": ["stocks", "crypto", "risk_assets"],
                "avoid": ["defensive_assets", "bonds"],
                "risk_level": "medium"
            }
        }

        return recommendations.get(cycle, {})

    async def get_macro_sentiment(self) -> Dict:
        """
        Get comprehensive macro sentiment score.

        Returns:
            Dictionary with sentiment score and components
        """
        try:
            cycle_data = await self.analyze_economic_cycle()

            # Calculate sentiment score (-1 to 1)
            score = 0.0

            # Fed rate impact (lower rates = bullish)
            fed_rate = cycle_data.get("indicators", {}).get("fed_rate", 5.0)
            score += (6.0 - fed_rate) * 0.1  # Normalize around 5%

            # CPI impact (lower inflation = bullish)
            cpi = cycle_data.get("indicators", {}).get("cpi_yoy", 3.0)
            score += (3.0 - cpi) * 0.1  # Normalize around 3%

            # VIX impact (lower VIX = bullish)
            vix = cycle_data.get("indicators", {}).get("vix", 20)
            score += (25 - vix) * 0.02  # Normalize around 25

            # Yield curve impact
            spread = cycle_data.get("indicators", {}).get("yield_spread", 0)
            score += spread * 0.5  # Positive spread = bullish

            # Clamp score to [-1, 1]
            score = max(-1, min(1, score))

            return {
                "score": score,
                "interpretation": "bullish" if score > 0.2 else "bearish" if score < -0.2 else "neutral",
                "cycle": cycle_data.get("cycle"),
                "details": cycle_data
            }

        except Exception as e:
            logger.error("Error getting macro sentiment", error=str(e))
            return {"score": 0, "interpretation": "neutral"}
