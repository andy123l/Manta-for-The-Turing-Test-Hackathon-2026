# Manta - Mantle Macro-Aware Trading Agent

AI Trading & Strategy赛道项目 - Turing Test Hackathon 2026

## 项目简介

Manta是一个宏观驱动的AI交易代理，结合链上数据、宏观经济指标和新闻情绪，自动在Mantle上执行交易策略。

### 核心特性

- **宏观驱动策略**: 基于美联储利率、CPI、美元指数等宏观指标调整交易策略
- **AI情绪分析**: 使用NLP模型分析新闻和社交媒体情绪
- **多策略组合**: 宏观策略 + 动量策略 + 均值回归策略
- **链上执行**: 通过Mantle智能合约执行交易
- **实时Dashboard**: 监控交易状态和性能

## 技术栈

### 后端 (Python)
- `pybit` - Bybit API客户端
- `ccxt` - 统一交易所API
- `pandas` - 数据处理
- `scikit-learn` - 机器学习
- `transformers` - NLP模型

### 智能合约 (Solidity)
- OpenZeppelin - 安全合约库
- Hardhat - 开发框架
- Mantle Network - L2执行层

## 项目结构

```
AI-Trading-Strategy/
├── ai-agent/                    # AI交易代理核心
│   ├── strategies/              # 交易策略
│   ├── data/                    # 数据层
│   ├── models/                  # AI模型
│   ├── executor/                # 执行层
│   └── utils/                   # 工具函数
│
├── contracts/                   # 智能合约
│   ├── TradingVault.sol         # 交易金库
│   ├── StrategyExecutor.sol     # 策略执行器
│   └── scripts/                 # 部署脚本
│
├── dashboard/                   # 前端Dashboard
├── tests/                       # 测试
└── docs/                        # 文档
```

## 快速开始

### 1. 环境准备

```bash
# Python环境
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Solidity环境
cd contracts
npm install
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填写：

```env
# Bybit API
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
BYBIT_TESTNET=true

# Mantle
PRIVATE_KEY=your_wallet_private_key
RPC_URL=https://rpc.testnet.mantle.xyz
```

### 3. 部署智能合约

```bash
cd contracts
npx hardhat run scripts/deploy.js --network mantle_testnet
```

### 4. 运行AI代理

```bash
cd ai-agent
python main.py
```

## 策略说明

### 宏观驱动策略 (权重: 40%)

基于以下宏观指标：
- 美联储利率 (Fed Funds Rate)
- 消费者价格指数 (CPI)
- 美元指数 (DXY)
- 国债收益率
- VIX恐慌指数

经济周期判断：
- **复苏期 (Recovery)**: 偏多，买入风险资产
- **通胀期 (Inflationary)**: 中性，持有抗通胀资产
- **紧缩期 (Tightening)**: 偏空，减少风险敞口
- **衰退期 (Recessionary)**: 偏空，持有现金和债券

### 情绪分析 (权重: 30%)

- 新闻情绪分析 (NLP模型)
- 恐惧/贪婪指数
- 社交媒体情绪

### 技术分析 (权重: 30%)

- RSI (相对强弱指数)
- MACD (移动平均收敛散度)
- 布林带 (Bollinger Bands)
- 移动平均线交叉

## 部署网络

### Mantle 测试网 (推荐用于开发)
- **RPC**: https://rpc.testnet.mantle.xyz
- **Chain ID**: 5001
- **水龙头**: https://faucet.testnet.mantle.xyz/

### Mantle 主网 (生产环境)
- **RPC**: https://rpc.mantle.xyz
- **Chain ID**: 5000

## 比赛要求

- ✅ Deploy on Mantle Network
- ✅ Open-source repo + runnable demo
- ✅ Python and Solidity
- ✅ Bybit API support

## License

MIT
