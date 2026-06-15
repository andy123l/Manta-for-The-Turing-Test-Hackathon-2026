"""
运行回测脚本
测试宏观驱动策略在历史数据上的表现
"""

import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from strategies.macro_strategy import MacroDrivenStrategy
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from backtest.backtester import Backtester


def generate_mock_data(days: int = 365) -> pd.DataFrame:
    """
    生成模拟历史数据

    Args:
        days: 天数

    Returns:
        DataFrame with OHLCV data
    """
    np.random.seed(42)

    # 初始价格
    initial_price = 65000

    # 生成价格序列（几何布朗运动）
    returns = np.random.normal(0.0001, 0.02, days)
    prices = initial_price * np.exp(np.cumsum(returns))

    # 生成OHLCV数据
    data = []
    for i, price in enumerate(prices):
        # 生成日内波动
        high = price * (1 + np.random.uniform(0, 0.02))
        low = price * (1 - np.random.uniform(0, 0.02))
        open_price = price * (1 + np.random.uniform(-0.01, 0.01))
        volume = np.random.uniform(1000000, 5000000)

        data.append({
            'timestamp': datetime.now() - timedelta(days=days-i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })

    return pd.DataFrame(data)


def run_backtest():
    """运行回测"""
    print("="*60)
    print("MANTA - Backtest Runner")
    print("="*60)

    # 生成模拟数据
    print("\nGenerating mock data...")
    data = generate_mock_data(days=365)
    print(f"  Data points: {len(data)}")
    print(f"  Date range: {data['timestamp'].min()} to {data['timestamp'].max()}")
    print(f"  Price range: ${data['close'].min():,.2f} to ${data['close'].max():,.2f}")

    # 定义策略
    strategies = {
        "MacroDriven": MacroDrivenStrategy(),
        "Momentum": MomentumStrategy(),
        "MeanReversion": MeanReversionStrategy()
    }

    # 运行回测
    results = {}
    for name, strategy in strategies.items():
        print(f"\n{'='*60}")
        print(f"Testing {name} Strategy")
        print(f"{'='*60}")

        backtester = Backtester(initial_capital=10000)
        result = backtester.run(data, strategy)
        backtester.print_report(result)

        results[name] = result

    # 比较结果
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)

    print(f"\n{'Strategy':<20} {'Return':<15} {'Sharpe':<15} {'Max DD':<15} {'Win Rate':<15}")
    print("-"*80)

    for name, result in results.items():
        print(f"{name:<20} {result.total_return:<15.2%} {result.sharpe_ratio:<15.2f} {result.max_drawdown:<15.2%} {result.win_rate:<15.2%}")

    print("="*60)

    # 找出最佳策略
    best_strategy = max(results.items(), key=lambda x: x[1].total_return)
    print(f"\nBest Strategy: {best_strategy[0]}")
    print(f"   Total Return: {best_strategy[1].total_return:.2%}")


if __name__ == "__main__":
    run_backtest()
