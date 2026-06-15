# Manta - Mantle Macro-Aware Trading Agent

## 项目概述

**项目名称:** Manta - Mantle Macro-Aware Trading Agent
**赛道:** AI Trading & Strategy (Turing Test Hackathon 2026)
**核心概念:** 宏观驱动的AI交易代理，只使用Mantle网络

---

## 遇到的问题和解决方案

### 问题 7: Mantle测试网RPC URL返回301重定向

**错误信息:**
```
HH110: Invalid JSON-RPC response received: <html><head><title>301 Moved Permanently</title></head>...
```

**原因:** Mantle测试网RPC URL (https://rpc.testnet.mantle.xyz) 返回301重定向

**解决方案:**
1. 尝试使用其他RPC提供商
2. 使用公共RPC: https://mantle-testnet.public.blastapi.io
3. 或使用Infura/Alchemy等服务

**临时解决方案:** 使用Mantle主网RPC进行测试
```javascript
// hardhat.config.js
mantle_testnet: {
  url: "https://rpc.mantle.xyz",  // 使用主网RPC
  chainId: 5000,
  ...
}
```



### 问题 1: OpenZeppelin v5 导入路径错误

**错误信息:**
```
File @openzeppelin/contracts/security/ReentrancyGuard.sol, imported from contracts/StrategyExecutor.sol, not found.
```

**原因:** OpenZeppelin v5改变了导入路径，`security/ReentrancyGuard.sol` 改为 `utils/ReentrancyGuard.sol`

**解决方案:**
```solidity
// 旧版本 (v4)
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

// 新版本 (v5)
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
```

---

### 问题 2: Ownable 构造函数需要参数

**错误信息:**
```
TypeError: No arguments passed to the base constructor. Specify the arguments or mark "StrategyExecutor" as abstract.
```

**原因:** OpenZeppelin v5的Ownable构造函数需要传入初始owner地址

**解决方案:**
```solidity
// 旧版本 (v4)
constructor() {
    // 不需要参数
}

// 新版本 (v5)
constructor() Ownable(msg.sender) {
    // 需要传入msg.sender
}
```

---

### 问题 3: npx 找不到 node 命令

**错误信息:**
```
'"node"' 不是内部或外部命令，也不是可运行的程序
```

**原因:** Windows环境下npx无法正确找到node路径

**解决方案:**
```bash
# 旧方法 (失败)
npx hardhat compile

# 新方法 (成功)
cd contracts
node.exe "node_modules/hardhat/internal/cli/cli.js" compile
```

---

### 问题 4: Python pip 路径错误

**错误信息:**
```
D:/hacks_soft/Casper Agentic Buildathon/nodejs/node-v22.16.0-win-x64/pip.exe: No such file or directory
```

**原因:** 错误地尝试使用Node目录中的pip

**解决方案:**
```bash
# 找到正确的Python路径
D:/Anthropic/Python/python.exe -m pip install -r requirements.txt
```

---

### 问题 5: Chrome DevTools MCP 连接超时

**错误信息:**
```
Network.enable timed out. Increase the 'protocolTimeout' setting
```

**原因:** Chrome标签页过多（89个），导致Puppeteer初始化超时

**解决方案:**
1. 关闭多余标签页，保持5-10个以内
2. 使用ws模块直接通过WebSocket连接Chrome DevTools
3. 安装ws模块：`npm install ws`

---

### 问题 6: 助记词 vs 私钥混淆

**问题描述:** 用户提供了公钥地址（40字符）而非私钥（64字符）

**解决方案:**
- 公钥地址格式：`0x...` (40字符) - 用于接收资金
- 私钥格式：`0x...` (64字符) - 用于签名交易
- 从助记词生成私钥：使用ethers.js的`HDNodeWallet.fromMnemonic()`

---

## 技术栈

### 智能合约 (Solidity)
- OpenZeppelin v5 - 安全合约库
- Hardhat - 开发框架
- Mantle Network - L2执行层

### AI代理 (Python)
- pandas - 数据处理
- scikit-learn - 机器学习
- transformers - NLP模型
- pandas-ta - 技术指标
- web3 - Mantle交互

---

## 项目结构

```
AI-Trading-Strategy/
├── ai-agent/                    # AI交易代理核心
│   ├── main_simple.py           # 简化版入口（推荐）
│   ├── strategies/              # 交易策略
│   ├── data/                    # 数据层
│   └── utils/                   # 工具函数
│
├── contracts/                   # 智能合约
│   ├── TradingVault.sol         # 交易金库
│   ├── StrategyExecutor.sol     # 策略执行器
│   └── scripts/                 # 部署脚本
│
├── .env                         # 环境变量配置
└── README.md                    # 项目文档
```

---

## 配置信息

### 环境变量 (.env)

```env
# Mantle Network
PRIVATE_KEY=your_private_key_here
RPC_URL=https://rpc.sepolia.mantle.xyz
CHAIN_ID=5003

# Trading
MAX_POSITION_SIZE=0.1
MAX_LOSS_PER_TRADE=0.02
INITIAL_CAPITAL=1000
```

### Mantle 测试网

| 参数 | 值 |
|------|-----|
| 网络名称 | Mantle Sepolia Testnet |
| RPC URL | https://rpc.sepolia.mantle.xyz |
| Chain ID | 5001 |
| 水龙头 | https://faucet.testnet.mantle.xyz/ |

---

## 快速开始

### 1. 安装依赖

```bash
# Python依赖
D:/Anthropic/Python/python.exe -m pip install -r requirements.txt

# Solidity依赖
cd contracts
npm install
```

### 2. 编译智能合约

```bash
cd contracts
node.exe "node_modules/hardhat/internal/cli/cli.js" compile
```

### 3. 部署智能合约

```bash
cd contracts
node.exe "node_modules/hardhat/internal/cli/cli.js" run scripts/deploy.js --network mantle_testnet
```

### 4. 运行AI代理

```bash
cd ai-agent
D:/Anthropic/Python/python.exe main_simple.py
```

---

## 策略说明

### 宏观驱动策略

基于以下宏观指标：
- 美联储利率 (Fed Funds Rate)
- 消费者价格指数 (CPI)
- 美元指数 (DXY)
- VIX恐慌指数

经济周期判断：
- **复苏期**: 偏多，买入风险资产
- **通胀期**: 中性，持有抗通胀资产
- **紧缩期**: 偏空，减少风险敞口
- **衰退期**: 偏空，持有现金和债券

---

## 比赛要求

- ✅ Deploy on Mantle Network
- ✅ Open-source repo + runnable demo
- ✅ Python and Solidity
- ✅ AI-powered on-chain function

---

## 安全提醒

⚠️ **私钥安全**
- 私钥只保存在本地 .env 文件
- 绝不分享私钥给任何人
- 测试网专用，不要放真钱

---

## 更新日志

- 2026-06-08: 项目初始化
- 2026-06-08: 创建简化版本（无Bybit依赖）
- 2026-06-08: 配置Mantle测试网
- 2026-06-08: 生成钱包私钥
- 2026-06-08: 修复OpenZeppelin v5导入路径问题
- 2026-06-08: 修复Ownable构造函数参数问题
- 2026-06-08: 成功编译智能合约
- 2026-06-09: ✅ 成功部署合约到Mantle Sepolia测试网
  - TradingVault: 0x35ED8A35d7c3ad683Ff60BF120B56AEC4AF5B848
  - StrategyExecutor: 0x6A2b2387baD8200f50912739f5Af2485Cc9acDbb
