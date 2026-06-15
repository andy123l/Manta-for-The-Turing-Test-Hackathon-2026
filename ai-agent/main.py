"""
Manta - Mantle Macro-Aware Trading Agent
Main entry point for the trading agent
"""

import asyncio
from datetime import datetime

from loguru import logger

from utils.config import Config
from utils.logger import setup_logger
from data.bybit_client import BybitClient
from data.macro_data import MacroDataFetcher
from data.sentiment import SentimentAnalyzer
from strategies.macro_strategy import MacroDrivenStrategy


class MantaAgent:
    """
    Main trading agent that orchestrates all components.
    """

    def __init__(self):
        """Initialize the Manta trading agent."""
        # Load configuration
        self.config = Config()

        # Setup logger
        self.logger = setup_logger(
            level=self.config.logging.level,
            log_file=self.config.logging.file
        )

        # Initialize components
        self.bybit_client = BybitClient(
            api_key=self.config.bybit.api_key,
            api_secret=self.config.bybit.api_secret,
            testnet=self.config.bybit.testnet
        )

        self.macro_fetcher = MacroDataFetcher(
            fred_api_key=self.config.macro.fred_api_key
        )

        self.sentiment_analyzer = SentimentAnalyzer()

        self.strategy = MacroDrivenStrategy()

        self.is_running = False

        logger.info("Manta Agent initialized")

    async def start(self):
        """Start the trading agent."""
        logger.info("Starting Manta Agent...")
        self.is_running = True

        # Validate configuration
        try:
            self.config.validate()
        except ValueError as e:
            logger.error("Configuration error", error=str(e))
            return

        # Main trading loop
        while self.is_running:
            try:
                await self.trading_cycle()
                await asyncio.sleep(60)  # Run every minute
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.stop()
            except Exception as e:
                logger.error("Error in trading cycle", error=str(e))
                await asyncio.sleep(10)

    def stop(self):
        """Stop the trading agent."""
        logger.info("Stopping Manta Agent...")
        self.is_running = False

    async def trading_cycle(self):
        """Execute one trading cycle."""
        logger.info("Starting new trading cycle")

        # 1. Fetch market data
        ticker = await self.bybit_client.get_ticker("BTCUSDT")
        if not ticker:
            logger.warning("Failed to fetch ticker")
            return

        klines = await self.bybit_client.get_klines("BTCUSDT", "1h", 100)
        if klines.empty:
            logger.warning("Failed to fetch klines")
            return

        # 2. Fetch macro data
        macro_sentiment = await self.macro_fetcher.get_macro_sentiment()

        # 3. Fetch sentiment data
        market_sentiment = await self.sentiment_analyzer.get_market_sentiment()
        fear_greed = self.sentiment_analyzer.get_fear_greed_index()

        # 4. Calculate technical indicators
        indicators = self._calculate_indicators(klines)

        # 5. Generate trading signal
        signal_data = {
            "macro": macro_sentiment,
            "sentiment": {
                "score": market_sentiment.get("score", 0),
                "fear_greed": fear_greed
            },
            "price": ticker,
            "indicators": indicators
        }

        signal = self.strategy.generate_signal(signal_data)

        # 6. Execute trade if signal is strong enough
        if signal.action in ["buy", "sell"] and signal.confidence > 0.6:
            logger.info(
                "Strong signal detected",
                action=signal.action,
                confidence=signal.confidence,
                reason=signal.reason
            )

            # Execute trade
            await self._execute_trade(signal, ticker)

        # 7. Log cycle summary
        logger.info(
            "Trading cycle completed",
            price=ticker.get("last_price"),
            signal=signal.action,
            confidence=signal.confidence
        )

    def _calculate_indicators(self, klines) -> dict:
        """Calculate technical indicators from klines data."""
        try:
            import pandas_ta as ta

            # Calculate indicators
            df = klines.copy()

            # RSI
            df["rsi"] = ta.rsi(df["close"], length=14)

            # MACD
            macd = ta.macd(df["close"])
            if macd is not None:
                df["macd"] = macd.iloc[:, 0]
                df["macd_signal"] = macd.iloc[:, 1]
                df["macd_hist"] = macd.iloc[:, 2]

            # Bollinger Bands
            bb = ta.bbands(df["close"], length=20, std=2)
            if bb is not None:
                df["bb_upper"] = bb.iloc[:, 0]
                df["bb_middle"] = bb.iloc[:, 1]
                df["bb_lower"] = bb.iloc[:, 2]

            # Moving Averages
            df["sma_20"] = ta.sma(df["close"], length=20)
            df["sma_50"] = ta.sma(df["close"], length=50)
            df["ema_12"] = ta.ema(df["close"], length=12)
            df["ema_26"] = ta.ema(df["close"], length=26)

            # Volume
            df["volume_sma"] = ta.sma(df["volume"], length=20)

            # Get latest values
            latest = df.iloc[-1]

            return {
                "rsi": float(latest.get("rsi", 50)) if not pd.isna(latest.get("rsi")) else 50,
                "macd": float(latest.get("macd", 0)) if not pd.isna(latest.get("macd")) else 0,
                "macd_signal": float(latest.get("macd_signal", 0)) if not pd.isna(latest.get("macd_signal")) else 0,
                "bb_upper": float(latest.get("bb_upper", 0)) if not pd.isna(latest.get("bb_upper")) else 0,
                "bb_middle": float(latest.get("bb_middle", 0)) if not pd.isna(latest.get("bb_middle")) else 0,
                "bb_lower": float(latest.get("bb_lower", 0)) if not pd.isna(latest.get("bb_lower")) else 0,
                "sma_20": float(latest.get("sma_20", 0)) if not pd.isna(latest.get("sma_20")) else 0,
                "sma_50": float(latest.get("sma_50", 0)) if not pd.isna(latest.get("sma_50")) else 0,
                "ema_12": float(latest.get("ema_12", 0)) if not pd.isna(latest.get("ema_12")) else 0,
                "ema_26": float(latest.get("ema_26", 0)) if not pd.isna(latest.get("ema_26")) else 0,
                "volume_sma": float(latest.get("volume_sma", 0)) if not pd.isna(latest.get("volume_sma")) else 0
            }

        except Exception as e:
            logger.error("Error calculating indicators", error=str(e))
            return {}

    async def _execute_trade(self, signal, ticker):
        """Execute a trade based on the signal."""
        try:
            # Calculate position size
            balance = await self.bybit_client.get_account_balance()
            capital = balance.get("available_balance", 0)

            if capital <= 0:
                logger.warning("No available balance")
                return

            # Calculate position size (1% of capital per trade)
            position_size = capital * 0.01 / ticker.get("last_price", 1)

            # Place order
            result = await self.bybit_client.place_order(
                symbol="BTCUSDT",
                side="Buy" if signal.action == "buy" else "Sell",
                quantity=position_size
            )

            if result.get("success"):
                logger.info(
                    "Trade executed",
                    order_id=result.get("order_id"),
                    side=signal.action,
                    size=position_size
                )
            else:
                logger.error("Trade execution failed", error=result.get("error"))

        except Exception as e:
            logger.error("Error executing trade", error=str(e))


async def main():
    """Main function to run the Manta agent."""
    agent = MantaAgent()
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
