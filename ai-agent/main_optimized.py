"""
Manta - Mantle Macro-Aware Trading Agent
优化版本 - 完整功能实现
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from utils.config import Config
from utils.logger import setup_logger
from data.macro_data import MacroDataFetcher
from data.sentiment import SentimentAnalyzer
from strategies.macro_strategy import MacroDrivenStrategy
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy


class MantaAgentOptimized:
    """
    优化版交易代理 - 完整功能实现
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

        # 初始化策略
        self.strategies = {
            "macro": MacroDrivenStrategy(),
            "momentum": MomentumStrategy(),
            "mean_reversion": MeanReversionStrategy()
        }

        # 初始化数据获取器
        self.macro_fetcher = MacroDataFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()

        # 交易状态
        self.position = 0
        self.entry_price = 0
        self.capital = self.config.trading.initial_capital
        self.trades = []

        # 模拟价格数据
        self.current_price = 65000.0
        self.price_history = [65000.0]

        # 状态文件路径
        self.state_file = Path("state.json")
        self.trades_file = Path("trades.json")

        # 加载状态
        self._load_state()

        self.is_running = False

        logger.info("Manta Agent Optimized initialized")

    def _load_state(self):
        """加载代理状态。"""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                state = json.load(f)
                self.position = state.get("position", 0)
                self.entry_price = state.get("entry_price", 0)
                self.capital = state.get("capital", self.config.trading.initial_capital)
                logger.info("State loaded", position=self.position, capital=self.capital)

        if self.trades_file.exists():
            with open(self.trades_file, "r") as f:
                self.trades = json.load(f)
                logger.info("Trades loaded", count=len(self.trades))

    def _save_state(self):
        """保存代理状态。"""
        state = {
            "position": self.position,
            "entry_price": self.entry_price,
            "capital": self.capital,
            "last_update": datetime.now().isoformat()
        }

        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

        with open(self.trades_file, "w") as f:
            json.dump(self.trades, f, indent=2)

        logger.debug("State saved")

    async def start(self):
        """启动交易代理。"""
        logger.info("Starting Manta Agent Optimized...")
        self.is_running = True

        # 显示初始状态
        self._print_status()

        # 主交易循环
        cycle_count = 0
        while self.is_running:
            try:
                cycle_count += 1
                await self.trading_cycle(cycle_count)
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
        self._save_state()
        self._print_final_report()

    async def trading_cycle(self, cycle_count: int):
        """执行一个交易周期。"""
        logger.info(f"=== Trading Cycle {cycle_count} ===")

        # 1. 模拟价格变动
        self.current_price = self._simulate_price()
        self.price_history.append(self.current_price)

        # 2. 获取宏观数据
        macro_sentiment = await self.macro_fetcher.get_macro_sentiment()

        # 3. 获取情绪数据
        market_sentiment = await self.sentiment_analyzer.get_market_sentiment()
        fear_greed = self.sentiment_analyzer.get_fear_greed_index()

        # 4. 计算技术指标
        indicators = self._calculate_indicators()

        # 5. 准备信号数据
        signal_data = {
            "macro": macro_sentiment,
            "sentiment": {
                "score": market_sentiment.get("score", 0),
                "fear_greed": fear_greed
            },
            "price": {
                "last_price": self.current_price,
                "volume_24h": 1000000
            },
            "indicators": indicators
        }

        # 6. 获取所有策略信号
        signals = {}
        for name, strategy in self.strategies.items():
            signals[name] = strategy.generate_signal(signal_data)

        # 7. 综合决策
        final_signal = self._combine_signals(signals)

        # 8. 执行交易
        await self._execute_signal(final_signal, cycle_count)

        # 9. 检查止损/止盈
        self._check_exit_conditions(indicators)

        # 10. 保存状态
        self._save_state()

        # 11. 打印状态
        self._print_cycle_summary(cycle_count, signals, final_signal)

    def _simulate_price(self) -> float:
        """模拟价格变动。"""
        import random
        change = random.uniform(-0.02, 0.02)
        self.current_price *= (1 + change)
        return self.current_price

    def _calculate_indicators(self) -> dict:
        """计算技术指标。"""
        import random

        if len(self.price_history) < 20:
            # 数据不足，返回默认值
            return {
                "rsi": 50,
                "macd": 0,
                "macd_signal": 0,
                "bb_upper": self.current_price * 1.02,
                "bb_middle": self.current_price,
                "bb_lower": self.current_price * 0.98,
                "sma_20": self.current_price,
                "sma_50": self.current_price,
                "volume_sma": 1000000
            }

        # 简化版指标计算
        prices = self.price_history[-50:]

        # RSI
        gains = []
        losses = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-14:]) / 14 if gains else 0
        avg_loss = sum(losses[-14:]) / 14 if losses else 1
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # Moving Averages
        sma_20 = sum(prices[-20:]) / 20
        sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20

        # Bollinger Bands
        bb_middle = sma_20
        bb_std = (sum((p - bb_middle) ** 2 for p in prices[-20:]) / 20) ** 0.5
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std

        return {
            "rsi": rsi,
            "macd": random.uniform(-100, 100),
            "macd_signal": random.uniform(-100, 100),
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "volume_sma": 1000000
        }

    def _combine_signals(self, signals: dict) -> dict:
        """综合所有策略信号。"""
        # 权重分配
        weights = {
            "macro": 0.5,
            "momentum": 0.25,
            "mean_reversion": 0.25
        }

        # 计算加权得分
        total_score = 0
        total_confidence = 0

        for name, signal in signals.items():
            weight = weights.get(name, 0)
            if signal.action == "buy":
                score = signal.confidence
            elif signal.action == "sell":
                score = -signal.confidence
            else:
                score = 0

            total_score += score * weight
            total_confidence += signal.confidence * weight

        # 确定最终信号
        if total_score > 0.3:
            action = "buy"
            reason = f"Bullish signals: {', '.join(f'{k}={v.confidence:.2f}' for k, v in signals.items())}"
        elif total_score < -0.3:
            action = "sell"
            reason = f"Bearish signals: {', '.join(f'{k}={v.confidence:.2f}' for k, v in signals.items())}"
        else:
            action = "hold"
            reason = f"Neutral: score={total_score:.2f}"

        return {
            "action": action,
            "confidence": abs(total_score),
            "reason": reason,
            "individual_signals": {k: {"action": v.action, "confidence": v.confidence} for k, v in signals.items()}
        }

    async def _execute_signal(self, signal: dict, cycle_count: int):
        """执行交易信号。"""
        action = signal["action"]
        confidence = signal["confidence"]

        # 只在高置信度时执行
        if confidence < 0.6:
            logger.info("Signal confidence too low, skipping", confidence=confidence)
            return

        # 检查是否有持仓
        has_position = self.position != 0

        if action == "buy" and not has_position:
            # 开多仓
            position_size = self.capital * 0.1 / self.current_price
            self.position = position_size
            self.entry_price = self.current_price
            self.capital -= position_size * self.current_price

            trade = {
                "cycle": cycle_count,
                "action": "buy",
                "price": self.current_price,
                "size": position_size,
                "timestamp": datetime.now().isoformat(),
                "reason": signal["reason"]
            }
            self.trades.append(trade)

            logger.info(
                "📈 BUY order executed",
                price=self.current_price,
                size=position_size,
                cost=position_size * self.current_price
            )

        elif action == "sell" and has_position and self.position > 0:
            # 平多仓
            pnl = (self.current_price - self.entry_price) * self.position
            pnl_pct = (self.current_price - self.entry_price) / self.entry_price * 100

            self.capital += self.position * self.current_price
            self.position = 0
            self.entry_price = 0

            trade = {
                "cycle": cycle_count,
                "action": "sell",
                "price": self.current_price,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "timestamp": datetime.now().isoformat(),
                "reason": signal["reason"]
            }
            self.trades.append(trade)

            emoji = "✅" if pnl > 0 else "❌"
            logger.info(
                f"{emoji} SELL order executed",
                price=self.current_price,
                pnl=f"{pnl:.2f}",
                pnl_pct=f"{pnl_pct:.2f}%"
            )

        elif action == "sell" and not has_position:
            # 开空仓（简化版：只记录信号）
            logger.info("📉 Short signal detected (not implemented)", confidence=confidence)

    def _check_exit_conditions(self, indicators: dict):
        """检查止损/止盈条件。"""
        if self.position == 0:
            return

        # 止损: -2%
        stop_loss_pct = -0.02
        current_pnl_pct = (self.current_price - self.entry_price) / self.entry_price

        if current_pnl_pct <= stop_loss_pct:
            logger.warning("⚠️ Stop loss triggered!")
            # 触发卖出
            asyncio.create_task(self._force_sell("Stop loss triggered"))

        # 止盈: +4%
        take_profit_pct = 0.04
        if current_pnl_pct >= take_profit_pct:
            logger.info("🎯 Take profit triggered!")
            asyncio.create_task(self._force_sell("Take profit triggered"))

    async def _force_sell(self, reason: str):
        """强制平仓。"""
        if self.position == 0:
            return

        pnl = (self.current_price - self.entry_price) * self.position
        pnl_pct = (self.current_price - self.entry_price) / self.entry_price * 100

        self.capital += self.position * self.current_price
        self.position = 0
        self.entry_price = 0

        trade = {
            "action": "force_sell",
            "price": self.current_price,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        }
        self.trades.append(trade)

        emoji = "✅" if pnl > 0 else "❌"
        logger.info(f"{emoji} Force sell executed", reason=reason, pnl=pnl)

    def _print_status(self):
        """打印当前状态。"""
        print("\n" + "="*60)
        print("🤖 MANTA - Mantle Macro-Aware Trading Agent")
        print("="*60)
        print(f"💰 Capital: ${self.capital:,.2f}")
        print(f"📊 Position: {self.position:.6f} BTC")
        if self.position > 0:
            print(f"💵 Entry Price: ${self.entry_price:,.2f}")
            pnl = (self.current_price - self.entry_price) * self.position
            print(f"📈 Unrealized P&L: ${pnl:,.2f}")
        print(f"💲 Current Price: ${self.current_price:,.2f}")
        print(f"📋 Total Trades: {len(self.trades)}")
        print("="*60 + "\n")

    def _print_cycle_summary(self, cycle_count: int, signals: dict, final_signal: dict):
        """打印周期摘要。"""
        print(f"\n--- Cycle {cycle_count} Summary ---")
        print(f"Price: ${self.current_price:,.2f}")
        print(f"Signal: {final_signal['action'].upper()} (confidence: {final_signal['confidence']:.2f})")
        print(f"Position: {self.position:.6f} BTC")
        print(f"Capital: ${self.capital:,.2f}")

        # 计算总P&L
        if self.position > 0:
            unrealized_pnl = (self.current_price - self.entry_price) * self.position
            print(f"Unrealized P&L: ${unrealized_pnl:,.2f}")

        # 计算已实现P&L
        realized_pnl = sum(t.get("pnl", 0) for t in self.trades)
        print(f"Realized P&L: ${realized_pnl:,.2f}")
        print("-"*40)

    def _print_final_report(self):
        """打印最终报告。"""
        print("\n" + "="*60)
        print("📊 FINAL TRADING REPORT")
        print("="*60)

        # 基本统计
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.get("pnl", 0) > 0)
        losing_trades = sum(1 for t in self.trades if t.get("pnl", 0) < 0)

        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")

        if total_trades > 0:
            win_rate = winning_trades / total_trades * 100
            print(f"Win Rate: {win_rate:.1f}%")

        # P&L统计
        realized_pnl = sum(t.get("pnl", 0) for t in self.trades)
        print(f"\nRealized P&L: ${realized_pnl:,.2f}")

        # 最终资本
        final_capital = self.capital + (self.position * self.current_price if self.position > 0 else 0)
        print(f"Final Capital: ${final_capital:,.2f}")

        # 收益率
        initial_capital = self.config.trading.initial_capital
        roi = (final_capital - initial_capital) / initial_capital * 100
        print(f"ROI: {roi:.2f}%")

        print("="*60)
        print("\nThank you for using Manta!")
        print("="*60)


async def main():
    """主函数。"""
    agent = MantaAgentOptimized()
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
