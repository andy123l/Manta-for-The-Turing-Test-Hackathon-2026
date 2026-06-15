"""
Backtester for Manta trading strategies.
Simulates trading strategies on historical data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass

from loguru import logger


@dataclass
class BacktestResult:
    """回测结果"""
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    profit_factor: float
    avg_trade_return: float


class Backtester:
    """
    回测引擎
    """

    def __init__(self, initial_capital: float = 10000):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []

        logger.info("Backtester initialized", initial_capital=initial_capital)

    def run(
        self,
        data: pd.DataFrame,
        strategy,
        stop_loss_pct: float = 0.02,
        take_profit_pct: float = 0.04
    ) -> BacktestResult:
        """
        运行回测

        Args:
            data: 历史数据 DataFrame (columns: open, high, low, close, volume)
            strategy: 交易策略对象
            stop_loss_pct: 止损百分比
            take_profit_pct: 止盈百分比

        Returns:
            回测结果
        """
        logger.info("Starting backtest", data_points=len(data))

        # 重置状态
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []

        # 用于计算指标的窗口
        window = 20

        for i in range(window, len(data)):
            # 获取当前数据
            current_data = data.iloc[:i+1]
            current_price = data.iloc[i]['close']

            # 计算指标
            indicators = self._calculate_indicators(current_data)

            # 准备信号数据
            signal_data = {
                "price": {
                    "last_price": current_price,
                    "volume_24h": data.iloc[i].get('volume', 0)
                },
                "indicators": indicators
            }

            # 生成信号
            signal = strategy.generate_signal(signal_data)

            # 执行交易
            self._execute_signal(signal, current_price, stop_loss_pct, take_profit_pct)

            # 检查止损/止盈
            self._check_exit_conditions(current_price, stop_loss_pct, take_profit_pct)

        # 计算最终结果
        final_capital = self.capital + (self.position * data.iloc[-1]['close'] if self.position > 0 else 0)

        return self._calculate_results(final_capital, data)

    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """计算技术指标"""
        prices = data['close'].values

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

        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else 0
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else 1
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # Moving Averages
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20

        # Bollinger Bands
        bb_middle = sma_20
        bb_std = np.std(prices[-20:])
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std

        return {
            "rsi": rsi,
            "macd": 0,  # 简化
            "macd_signal": 0,
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "volume_sma": np.mean(data['volume'].values[-20:])
        }

    def _execute_signal(
        self,
        signal,
        current_price: float,
        stop_loss_pct: float,
        take_profit_pct: float
    ):
        """执行交易信号"""
        action = signal.action
        confidence = signal.confidence

        # 只在高置信度时执行
        if confidence < 0.6:
            return

        has_position = self.position != 0

        if action == "buy" and not has_position:
            # 开多仓
            position_size = self.capital * 0.1 / current_price
            self.position = position_size
            entry_price = current_price
            self.capital -= position_size * current_price

            self.trades.append({
                "action": "buy",
                "price": current_price,
                "size": position_size,
                "timestamp": datetime.now()
            })

        elif action == "sell" and has_position and self.position > 0:
            # 平多仓
            entry_price = self.trades[-1]["price"] if self.trades else current_price
            pnl = (current_price - entry_price) * self.position
            pnl_pct = (current_price - entry_price) / entry_price * 100

            self.capital += self.position * current_price
            self.position = 0

            self.trades.append({
                "action": "sell",
                "price": current_price,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "timestamp": datetime.now()
            })

    def _check_exit_conditions(
        self,
        current_price: float,
        stop_loss_pct: float,
        take_profit_pct: float
    ):
        """检查止损/止盈条件"""
        if self.position == 0:
            return

        if len(self.trades) == 0:
            return

        entry_price = self.trades[-1]["price"]
        pnl_pct = (current_price - entry_price) / entry_price

        # 止损
        if pnl_pct <= -stop_loss_pct:
            self.capital += self.position * current_price
            self.position = 0

            self.trades.append({
                "action": "stop_loss",
                "price": current_price,
                "pnl": pnl_pct * self.position * entry_price,
                "timestamp": datetime.now()
            })

        # 止盈
        elif pnl_pct >= take_profit_pct:
            self.capital += self.position * current_price
            self.position = 0

            self.trades.append({
                "action": "take_profit",
                "price": current_price,
                "pnl": pnl_pct * self.position * entry_price,
                "timestamp": datetime.now()
            })

    def _calculate_results(self, final_capital: float, data: pd.DataFrame) -> BacktestResult:
        """计算回测结果"""
        # 基本统计
        sell_trades = [t for t in self.trades if t["action"] in ["sell", "stop_loss", "take_profit"]]
        total_trades = len(sell_trades)
        winning_trades = sum(1 for t in sell_trades if t.get("pnl", 0) > 0)
        losing_trades = sum(1 for t in sell_trades if t.get("pnl", 0) < 0)

        # 收益统计
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        trades_pnl = [t.get("pnl", 0) for t in sell_trades]
        gross_profit = sum(p for p in trades_pnl if p > 0)
        gross_loss = abs(sum(p for p in trades_pnl if p < 0))

        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown()

        # 计算Sharpe比率
        sharpe_ratio = self._calculate_sharpe_ratio()

        # 计算年化收益
        days = len(data)
        annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0

        return BacktestResult(
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=winning_trades / total_trades if total_trades > 0 else 0,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            profit_factor=gross_profit / gross_loss if gross_loss > 0 else float('inf'),
            avg_trade_return=np.mean(trades_pnl) if trades_pnl else 0
        )

    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤"""
        if not self.trades:
            return 0

        cumulative = 0
        peak = 0
        max_drawdown = 0

        for trade in self.trades:
            cumulative += trade.get("pnl", 0)
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown / self.initial_capital if self.initial_capital > 0 else 0

    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """计算Sharpe比率"""
        sell_trades = [t for t in self.trades if t["action"] in ["sell", "stop_loss", "take_profit"]]

        if len(sell_trades) < 2:
            return 0

        returns = [t.get("pnl", 0) / self.initial_capital for t in sell_trades]
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0

        return (avg_return - risk_free_rate) / std_return

    def print_report(self, result: BacktestResult):
        """打印回测报告"""
        print("\n" + "="*60)
        print("📊 BACKTEST REPORT")
        print("="*60)

        print(f"\n💰 Capital:")
        print(f"  Initial: ${result.initial_capital:,.2f}")
        print(f"  Final: ${result.final_capital:,.2f}")

        print(f"\n📈 Returns:")
        print(f"  Total Return: {result.total_return:.2%}")
        print(f"  Annual Return: {result.annual_return:.2%}")

        print(f"\n📉 Risk:")
        print(f"  Max Drawdown: {result.max_drawdown:.2%}")
        print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")

        print(f"\n🎯 Trades:")
        print(f"  Total: {result.total_trades}")
        print(f"  Winning: {result.winning_trades}")
        print(f"  Losing: {result.losing_trades}")
        print(f"  Win Rate: {result.win_rate:.2%}")
        print(f"  Profit Factor: {result.profit_factor:.2f}")
        print(f"  Avg Trade Return: ${result.avg_trade_return:,.2f}")

        print("\n" + "="*60)
