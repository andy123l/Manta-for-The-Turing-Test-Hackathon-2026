"""
Manta - Mantle Macro-Aware Trading Agent
简化版本 - 只使用Mantle网络，无Bybit依赖
"""

import asyncio
from datetime import datetime

from loguru import logger

from utils.config import Config
from utils.logger import setup_logger
from data.macro_data import MacroDataFetcher
from data.sentiment import SentimentAnalyzer
from strategies.macro_strategy import MacroDrivenStrategy


class MantaAgent:
    """
    简化的交易代理 - 只使用Mantle网络
    """

    def __init__(self):
        """初始化Manta交易代理。"""
        # 加载配置
        self.config = Config()

        # 设置日志
        self.logger = setup_logger(
            level=self.config.logging.level,
            log_file=self.config.logging.file
        )

        # 初始化组件
        self.macro_fetcher = MacroDataFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.strategy = MacroDrivenStrategy()

        # 模拟价格数据（实际应该从预言机获取）
        self.current_price = 65000.0  # BTC初始价格

        self.is_running = False

        logger.info("Manta Agent initialized (Mantle only mode)")

    async def start(self):
        """启动交易代理。"""
        logger.info("Starting Manta Agent (Mantle only mode)...")
        self.is_running = True

        # 主交易循环
        while self.is_running:
            try:
                await self.trading_cycle()
                await asyncio.sleep(60)  # 每分钟运行一次
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.stop()
            except Exception as e:
                logger.error("Error in trading cycle", error=str(e))
                await asyncio.sleep(10)

    def stop(self):
        """停止交易代理。"""
        logger.info("Stopping Manta Agent...")
        self.is_running = False

    async def trading_cycle(self):
        """执行一个交易周期。"""
        logger.info("Starting new trading cycle")

        # 1. 模拟获取市场价格（实际从预言机获取）
        self.current_price = self._simulate_price()

        # 2. 获取宏观数据
        macro_sentiment = await self.macro_fetcher.get_macro_sentiment()

        # 3. 获取情绪数据
        market_sentiment = await self.sentiment_analyzer.get_market_sentiment()
        fear_greed = self.sentiment_analyzer.get_fear_greed_index()

        # 4. 计算技术指标（简化版）
        indicators = self._calculate_simple_indicators()

        # 5. 生成交易信号
        signal_data = {
            "macro": macro_sentiment,
            "sentiment": {
                "score": market_sentiment.get("score", 0),
                "fear_greed": fear_greed
            },
            "price": {
                "last_price": self.current_price,
                "volume_24h": 1000000  # 模拟数据
            },
            "indicators": indicators
        }

        signal = self.strategy.generate_signal(signal_data)

        # 6. 记录信号
        logger.info(
            "Signal generated",
            price=self.current_price,
            action=signal.action,
            confidence=signal.confidence,
            reason=signal.reason
        )

        # 7. 模拟执行交易（实际通过Mantle合约执行）
        if signal.action in ["buy", "sell"] and signal.confidence > 0.6:
            await self._simulate_trade(signal)

        # 8. 记录周期完成
        logger.info(
            "Trading cycle completed",
            price=self.current_price,
            signal=signal.action,
            macro_cycle=macro_sentiment.get("cycle", "unknown"),
            fear_greed=fear_greed.get("value", 50)
        )

    def _simulate_price(self) -> float:
        """模拟价格变动（实际从预言机获取）。"""
        import random
        change = random.uniform(-0.02, 0.02)  # ±2%波动
        self.current_price *= (1 + change)
        return self.current_price

    def _calculate_simple_indicators(self) -> dict:
        """计算简化版技术指标。"""
        import random

        return {
            "rsi": random.uniform(30, 70),
            "macd": random.uniform(-100, 100),
            "macd_signal": random.uniform(-100, 100),
            "bb_upper": self.current_price * 1.02,
            "bb_middle": self.current_price,
            "bb_lower": self.current_price * 0.98,
            "sma_20": self.current_price * random.uniform(0.98, 1.02),
            "sma_50": self.current_price * random.uniform(0.96, 1.04),
            "volume_sma": 1000000
        }

    async def _simulate_trade(self, signal):
        """模拟交易执行（实际通过Mantle合约）。"""
        logger.info(
            "Simulated trade executed",
            action=signal.action,
            price=self.current_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit
        )


async def main():
    """主函数。"""
    agent = MantaAgent()
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
