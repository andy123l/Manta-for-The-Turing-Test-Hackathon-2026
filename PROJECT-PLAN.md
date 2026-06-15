# Mantle Macro-Aware Trading Agent - 项目详细计划

## 1. 项目概述

**项目名称:** Mantle Macro-Aware Trading Agent (Manta)
**赛道:** AI Trading & Strategy
**目标:** 构建一个宏观驱动的AI交易代理，结合链上数据、宏观经济指标和新闻情绪，自动在Mantle上执行交易策略。

---

## 2. 官方要求分析

### 2.1 赛道描述
> AI Trading & Strategy — AI quant bots and macro-driven smart contracts, with Python and Solidity templates and Bybit API support. (Sponsored by BGA)

**关键点：**
- ✅ AI量化机器人
- ✅ 宏观驱动的智能合约
- ✅ Python模板
- ✅ Solidity模板
- ✅ Bybit API支持

### 2.2 评判标准

| 维度 | 权重 | 我们的目标 |
|------|------|-----------|
| Technical Depth | 30% | AI × Mantle深度集成，完整架构 |
| Innovation | 25% | 宏观驱动的新范式 |
| Mantle Ecosystem Contribution | 25% | 在Mantle上部署和执行 |
| Product Completeness | 20% | 完整的Dashboard和演示 |

### 2.3 获胜路径
**B. [AI-Driven] Trading Strategy** — 构建可执行的AI交易代理

**评分重点：**
- Strategy Alpha: 策略复杂性 + 可验证性（回测/实盘交易/链上记录）

### 2.4 鼓励方向
- Smart money tracking agent ✅ (我们将集成)
- Mantle ecosystem protocol data dashboard ✅ (Dashboard)
- AI-driven market sentiment analysis ✅ (核心功能)
- Automated arbitrage / market-making strategies ✅ (可选)

---

## 3. 技术栈选择

### 3.1 后端/AI (Python)
| 库 | 用途 | 安装命令 |
|----|------|----------|
| `pybit` | Bybit官方Python SDK | `pip install pybit` |
| `ccxt` | 统一交易所API | `pip install ccxt` |
| `pandas` | 数据处理 | `pip install pandas` |
| `numpy` | 数值计算 | `pip install numpy` |
| `scikit-learn` | 机器学习 | `pip install scikit-learn` |
| `ta-lib` | 技术指标 | `pip install ta-lib` |
| `requests` | HTTP请求 | `pip install requests` |
| `python-dotenv` | 环境变量 | `pip install python-dotenv` |
| `websocket-client` | WebSocket | `pip install websocket-client` |
| `transformers` | NLP模型 | `pip install transformers` |

### 3.2 智能合约 (Solidity)
| 工具 | 用途 | 安装命令 |
|------|------|----------|
| Hardhat | 开发框架 | `npm init -y && npm install --save-dev hardhat` |
| OpenZeppelin | 合约库 | `npm install @openzeppelin/contracts` |
| ethers.js | 交互库 | `npm install ethers` |

### 3.3 前端 (可选)
| 库 | 用途 |
|----|------|
| Next.js | React框架 |
| ethers.js | Web3交互 |
| Tailwind CSS | 样式 |

---

## 4. 项目架构

```
manta/
├── ai-agent/                    # AI交易代理核心
│   ├── __init__.py
│   ├── main.py                  # 入口文件
│   ├── strategies/              # 交易策略
│   │   ├── __init__.py
│   │   ├── base.py              # 策略基类
│   │   ├── momentum.py          # 动量策略
│   │   ├── mean_reversion.py    # 均值回归
│   │   ├── macro_strategy.py    # 宏观驱动策略 ⭐
│   │   └── composite.py         # 组合策略
│   ├── data/                    # 数据层
│   │   ├── __init__.py
│   │   ├── bybit_client.py      # Bybit API客户端 ⭐
│   │   ├── mantle_client.py     # Mantle链上数据 ⭐
│   │   ├── macro_data.py        # 宏观数据获取 ⭐
│   │   └── sentiment.py         # 新闻情绪分析 ⭐
│   ├── models/                  # AI模型
│   │   ├── __init__.py
│   │   ├── macro_analyzer.py    # 宏观分析模型 ⭐
│   │   ├── price_predictor.py   # 价格预测模型
│   │   └── risk_assessor.py     # 风险评估模型
│   ├── executor/                # 执行层
│   │   ├── __init__.py
│   │   ├── trade_executor.py    # 交易执行 ⭐
│   │   ├── contract_executor.py # 合约交互 ⭐
│   │   └── risk_manager.py      # 风险管理
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── config.py            # 配置管理
│       ├── logger.py            # 日志记录
│       └── metrics.py           # 指标计算
│
├── contracts/                   # 智能合约
│   ├── contracts/
│   │   ├── TradingVault.sol     # 交易金库 ⭐
│   │   ├── StrategyExecutor.sol # 策略执行器 ⭐
│   │   ├── Oracle.sol           # 预言机接口 ⭐
│   │   └── RiskManager.sol      # 风险管理合约
│   ├── scripts/
│   │   └── deploy.js            # 部署脚本
│   ├── test/
│   │   └── TradingVault.test.js # 测试
│   └── hardhat.config.js        # Hardhat配置
│
├── dashboard/                   # 前端Dashboard
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── styles/
│   └── package.json
│
├── data/                        # 数据存储
│   ├── historical/              # 历史数据
│   └── models/                  # 训练好的模型
│
├── docs/                        # 文档
│   ├── ARCHITECTURE.md          # 架构文档
│   └── API.md                   # API文档
│
├── tests/                       # 测试
│   ├── test_strategies.py
│   ├── test_data.py
│   └── test_executor.py
│
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量模板
└── README.md                    # 项目说明
```

---

## 5. 核心功能详细设计

### 5.1 数据层 (Data Layer)

#### 5.1.1 Bybit客户端 (bybit_client.py)
**功能：**
- 连接Bybit REST API获取市场数据
- WebSocket实时价格订阅
- 订单管理（下单、撤单、查询）
- 账户余额查询

**核心方法：**
```python
class BybitClient:
    def __init__(self, api_key, api_secret, testnet=True):
        """初始化Bybit客户端"""
        
    async def get_ticker(self, symbol: str) -> dict:
        """获取实时价格"""
        
    async def get_klines(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """获取K线数据"""
        
    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict:
        """获取订单簿"""
        
    async def place_order(self, symbol: str, side: str, quantity: float, price: float = None) -> dict:
        """下单"""
        
    async def cancel_order(self, symbol: str, order_id: str) -> dict:
        """撤单"""
        
    async def get_position(self, symbol: str) -> dict:
        """获取持仓"""
```

#### 5.1.2 Mantle链上数据 (mantle_client.py)
**功能：**
- 查询Mantle链上交易数据
- 获取TVL（总锁仓量）变化
- 监控大户钱包活动
- 查询协议数据

**核心方法：**
```python
class MantleClient:
    def __init__(self, rpc_url: str):
        """初始化Mantle客户端"""
        
    async def get_tvl_history(self, days: int = 30) -> pd.DataFrame:
        """获取TVL历史"""
        
    async def get_whale_activity(self, min_amount: float) -> list:
        """获取大户活动"""
        
    async def get_protocol_data(self, protocol: str) -> dict:
        """获取协议数据"""
        
    async def get_gas_price(self) -> int:
        """获取Gas价格"""
```

#### 5.1.3 宏观数据 (macro_data.py)
**功能：**
- 获取美联储利率数据
- 获取CPI通胀数据
- 获取美元指数(DXY)
- 获取国债收益率
- 获取VIX恐慌指数

**核心方法：**
```python
class MacroDataFetcher:
    def __init__(self):
        """初始化宏观数据获取器"""
        
    async def get_fed_rate(self) -> dict:
        """获取美联储利率"""
        
    async def get_cpi(self) -> dict:
        """获取CPI数据"""
        
    async def get_dxy(self) -> pd.DataFrame:
        """获取美元指数"""
        
    async def get_treasury_yields(self) -> dict:
        """获取国债收益率"""
        
    async def get_macro_sentiment(self) -> dict:
        """综合宏观情绪评分"""
```

#### 5.1.4 新闻情绪分析 (sentiment.py)
**功能：**
- 获取加密货币新闻
- 使用NLP模型分析情绪
- 计算市场恐惧/贪婪指数
- 社交媒体情绪分析

**核心方法：**
```python
class SentimentAnalyzer:
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        """初始化情绪分析器"""
        
    async def get_crypto_news(self) -> list:
        """获取加密货币新闻"""
        
    def analyze_sentiment(self, text: str) -> dict:
        """分析单条文本情绪"""
        
    async def get_market_sentiment(self) -> dict:
        """获取综合市场情绪"""
        
    def get_fear_greed_index(self) -> int:
        """获取恐惧贪婪指数"""
```

### 5.2 AI模型层 (Models Layer)

#### 5.2.1 宏观分析模型 (macro_analyzer.py)
**功能：**
- 分析宏观经济周期
- 识别市场趋势（通胀、紧缩、衰退、复苏）
- 生成宏观信号

**模型架构：**
```python
class MacroAnalyzer:
    def __init__(self):
        """初始化宏观分析器"""
        self.model = self._build_model()
        
    def _build_model(self):
        """构建分析模型"""
        # 使用规则引擎 + 简单ML模型
        
    def analyze_cycle(self, macro_data: dict) -> str:
        """
        分析经济周期
        Returns: 'inflationary', 'tightening', 'recessionary', 'recovery'
        """
        
    def generate_signal(self, macro_data: dict) -> dict:
        """
        生成交易信号
        Returns: {
            'direction': 'long' | 'short' | 'neutral',
            'confidence': 0.0 - 1.0,
            'reasoning': str
        }
        """
```

#### 5.2.2 价格预测模型 (price_predictor.py)
**功能：**
- 技术指标计算（MA, RSI, MACD, Bollinger）
- 价格趋势预测
- 支撑/阻力位识别

**核心方法：**
```python
class PricePredictor:
    def __init__(self):
        """初始化价格预测器"""
        
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        
    def predict_trend(self, df: pd.DataFrame) -> dict:
        """预测价格趋势"""
        
    def find_support_resistance(self, df: pd.DataFrame) -> dict:
        """识别支撑/阻力位"""
```

#### 5.2.3 风险评估模型 (risk_assessor.py)
**功能：**
- 计算VaR（风险价值）
- 评估市场波动性
- 动态调整仓位大小
- 止损/止盈设置

**核心方法：**
```python
class RiskAssessor:
    def __init__(self, max_risk_per_trade: float = 0.02):
        """初始化风险评估器"""
        
    def calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """计算VaR"""
        
    def calculate_position_size(self, capital: float, stop_loss_pct: float) -> float:
        """计算仓位大小"""
        
    def assess_volatility(self, df: pd.DataFrame) -> dict:
        """评估波动性"""
```

### 5.3 策略层 (Strategies Layer)

#### 5.3.1 策略基类 (base.py)
```python
from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.position = 0
        self.entry_price = 0
        
    @abstractmethod
    def generate_signal(self, data: dict) -> dict:
        """
        生成交易信号
        Returns: {
            'action': 'buy' | 'sell' | 'hold',
            'confidence': 0.0 - 1.0,
            'reason': str
        }
        """
        pass
    
    @abstractmethod
    def calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """计算止损价"""
        pass
    
    @abstractmethod
    def calculate_take_profit(self, entry_price: float, direction: str) -> float:
        """计算止盈价"""
        pass
```

#### 5.3.2 宏观驱动策略 (macro_strategy.py) ⭐核心
```python
class MacroDrivenStrategy(BaseStrategy):
    """宏观驱动策略 - 项目核心"""
    
    def __init__(self, macro_analyzer, sentiment_analyzer, price_predictor):
        super().__init__("MacroDriven")
        self.macro_analyzer = macro_analyzer
        self.sentiment_analyzer = sentiment_analyzer
        self.price_predictor = price_predictor
        
    def generate_signal(self, data: dict) -> dict:
        """
        综合宏观、情绪、技术指标生成信号
        
        权重分配：
        - 宏观信号: 40%
        - 情绪信号: 30%
        - 技术信号: 30%
        """
        # 1. 获取宏观信号
        macro_signal = self.macro_analyzer.generate_signal(data['macro'])
        
        # 2. 获取情绪信号
        sentiment_signal = self._get_sentiment_signal(data['sentiment'])
        
        # 3. 获取技术信号
        tech_signal = self._get_tech_signal(data['price'])
        
        # 4. 综合决策
        return self._combine_signals(macro_signal, sentiment_signal, tech_signal)
        
    def _combine_signals(self, macro, sentiment, tech) -> dict:
        """综合信号"""
        weights = {'macro': 0.4, 'sentiment': 0.3, 'tech': 0.3}
        
        # 计算加权得分
        score = (
            macro['score'] * weights['macro'] +
            sentiment['score'] * weights['sentiment'] +
            tech['score'] * weights['tech']
        )
        
        # 根据得分生成信号
        if score > 0.6:
            return {'action': 'buy', 'confidence': score, 'reason': 'Strong bullish signals'}
        elif score < -0.6:
            return {'action': 'sell', 'confidence': abs(score), 'reason': 'Strong bearish signals'}
        else:
            return {'action': 'hold', 'confidence': 1 - abs(score), 'reason': 'Neutral market'}
```

### 5.4 执行层 (Executor Layer)

#### 5.4.1 交易执行器 (trade_executor.py)
```python
class TradeExecutor:
    """交易执行器"""
    
    def __init__(self, bybit_client, risk_manager):
        self.bybit_client = bybit_client
        self.risk_manager = risk_manager
        
    async def execute_signal(self, signal: dict, capital: float) -> dict:
        """执行交易信号"""
        # 1. 风险检查
        if not self.risk_manager.check_signal(signal):
            return {'status': 'rejected', 'reason': 'Risk check failed'}
        
        # 2. 计算仓位大小
        position_size = self.risk_manager.calculate_position_size(
            capital, 
            signal['stop_loss_pct']
        )
        
        # 3. 执行交易
        if signal['action'] == 'buy':
            result = await self.bybit_client.place_order(
                symbol='BTCUSDT',
                side='Buy',
                quantity=position_size
            )
        elif signal['action'] == 'sell':
            result = await self.bybit_client.place_order(
                symbol='BTCUSDT',
                side='Sell',
                quantity=position_size
            )
        
        return result
```

#### 5.4.2 合约交互器 (contract_executor.py)
```python
from web3 import Web3

class ContractExecutor:
    """Mantle智能合约交互器"""
    
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(private_key)
        self.contract = self._load_contract(contract_address)
        
    def _load_contract(self, address: str):
        """加载合约"""
        # 加载ABI并创建合约实例
        
    async def deposit_to_vault(self, amount: float) -> dict:
        """存入资金到金库"""
        
    async def execute_strategy(self, strategy_id: int, params: dict) -> dict:
        """执行链上策略"""
        
    async def withdraw(self, amount: float) -> dict:
        """提取资金"""
```

### 5.5 风险管理 (Risk Manager)

```python
class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: dict):
        self.max_position_size = config.get('max_position_size', 0.1)  # 最大仓位10%
        self.max_loss_per_trade = config.get('max_loss_per_trade', 0.02)  # 单笔最大亏损2%
        self.max_daily_loss = config.get('max_daily_loss', 0.05)  # 日最大亏损5%
        
    def check_signal(self, signal: dict) -> bool:
        """检查信号是否符合风险规则"""
        
    def calculate_position_size(self, capital: float, stop_loss_pct: float) -> float:
        """计算仓位大小"""
        # 基于固定比例风险模型
        risk_amount = capital * self.max_loss_per_trade
        position_size = risk_amount / stop_loss_pct
        return min(position_size, capital * self.max_position_size)
        
    def check_daily_loss(self, daily_pnl: float, capital: float) -> bool:
        """检查日亏损限制"""
        return abs(daily_pnl / capital) < self.max_daily_loss
```

---

## 6. 智能合约设计

### 6.1 TradingVault.sol
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract TradingVault is ReentrancyGuard {
    // 状态变量
    address public owner;
    address public trustedExecutor;
    uint256 public totalDeposits;
    mapping(address => uint256) public deposits;
    
    // 事件
    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    event StrategyExecuted(uint256 indexed strategyId, bool success);
    
    // 修饰符
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier onlyExecutor() {
        require(msg.sender == trustedExecutor, "Not executor");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    // 存入资金
    function deposit(uint256 amount) external nonReentrant {
        IERC20(token).transferFrom(msg.sender, address(this), amount);
        deposits[msg.sender] += amount;
        totalDeposits += amount;
        emit Deposit(msg.sender, amount);
    }
    
    // 提取资金
    function withdraw(uint256 amount) external nonReentrant {
        require(deposits[msg.sender] >= amount, "Insufficient balance");
        deposits[msg.sender] -= amount;
        totalDeposits -= amount;
        IERC20(token).transfer(msg.sender, amount);
        emit Withdraw(msg.sender, amount);
    }
    
    // 执行策略（只有受信任的执行者可以调用）
    function executeStrategy(
        uint256 strategyId,
        address target,
        bytes calldata data,
        uint256 value
    ) external onlyExecutor returns (bool success) {
        // 执行链上交易
        (success, ) = target.call{value: value}(data);
        emit StrategyExecuted(strategyId, success);
    }
}
```

### 6.2 StrategyExecutor.sol
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract StrategyExecutor {
    // 策略执行器
    // 负责调用不同的DeFi协议
    
    struct Strategy {
        uint256 id;
        address target;
        bytes encodedFunction;
        uint256 riskLevel;  // 1-5
        bool active;
    }
    
    mapping(uint256 => Strategy) public strategies;
    uint256 public strategyCount;
    
    // 添加策略
    function addStrategy(
        address target,
        bytes calldata encodedFunction,
        uint256 riskLevel
    ) external returns (uint256) {
        strategyCount++;
        strategies[strategyCount] = Strategy({
            id: strategyCount,
            target: target,
            encodedFunction: encodedFunction,
            riskLevel: riskLevel,
            active: true
        });
        return strategyCount;
    }
    
    // 执行策略
    function executeStrategy(
        uint256 strategyId,
        uint256 amount
    ) external returns (bool) {
        Strategy storage strategy = strategies[strategyId];
        require(strategy.active, "Strategy not active");
        
        // 执行交易
        (bool success, ) = strategy.target.call(
            abi.encodePacked(strategy.encodedFunction, amount)
        );
        
        return success;
    }
}
```

---

## 7. 开发时间表 (7天)

### Day 1 (6/8 - 今天): 基础架构 ✅
- [x] 分析比赛要求
- [x] 创建项目结构
- [ ] 初始化Python环境
- [ ] 配置Bybit API客户端
- [ ] 创建策略基类

### Day 2 (6/9): 数据层
- [ ] 实现Bybit数据获取
- [ ] 实现宏观数据获取
- [ ] 实现情绪分析
- [ ] 测试数据获取

### Day 3 (6/10): AI模型
- [ ] 实现宏观分析模型
- [ ] 实现价格预测模型
- [ ] 实现风险评估模型
- [ ] 测试模型输出

### Day 4 (6/11): 策略实现
- [ ] 实现宏观驱动策略
- [ ] 实现动量策略
- [ ] 实现均值回归策略
- [ ] 策略回测

### Day 5 (6/12): 智能合约
- [ ] 编写TradingVault合约
- [ ] 编写StrategyExecutor合约
- [ ] 测试合约
- [ ] 部署到Mantle测试网

### Day 6 (6/13): 集成与测试
- [ ] AI代理与合约集成
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 安全检查

### Day 7 (6/14-15): 提交
- [ ] 编写文档
- [ ] 录制演示视频
- [ ] 提交到DoraHacks
- [ ] 准备Pitch

---

## 8. 环境配置

### 8.1 Python环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 8.2 Hardhat环境
```bash
cd contracts
npm init -y
npm install --save-dev hardhat @openzeppelin/contracts ethers dotenv
npx hardhat init
```

### 8.3 环境变量 (.env)
```env
# Bybit API
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
BYBIT_TESTNET=true

# Mantle
PRIVATE_KEY=your_private_key
RPC_URL=https://rpc.testnet.mantle.xyz
CONTRACT_ADDRESS=0x...

# 通用
LOG_LEVEL=INFO
MAX_POSITION_SIZE=0.1
MAX_LOSS_PER_TRADE=0.02
```

---

## 9. 风险提示

### 技术风险
- API限流
- 网络延迟
- 合约漏洞

### 市场风险
- 价格波动
- 流动性不足
- 黑天鹅事件

### 缓解措施
- 使用测试网测试
- 设置止损
- 分散投资
- 定期审计

---

## 10. 获胜策略

### 提交内容
1. **开源GitHub仓库** - 完整代码 + README
2. **可运行Demo** - Dashboard演示
3. **演示视频** - 2分钟以上
4. **项目Pitch** - 一页纸介绍

### 亮点突出
1. **创新性** - 宏观驱动的新范式
2. **技术深度** - AI × 链上深度集成
3. **实用性** - 可以实际使用的交易工具
4. **Mantle贡献** - 在Mantle上部署和执行

---

**最后更新:** 2026-06-08
**作者:** AI Assistant
