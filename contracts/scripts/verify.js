/**
 * 验证合约部署状态
 * 检查TradingVault和StrategyExecutor合约是否正常工作
 */

const hre = require("hardhat");

async function main() {
  console.log("🔍 验证合约部署状态...\n");

  // 获取部署信息
  const fs = require("fs");
  const deploymentPath = "./deployments/mantle_testnet.json";

  if (!fs.existsSync(deploymentPath)) {
    console.error("❌ 未找到部署信息文件");
    return;
  }

  const deployment = JSON.parse(fs.readFileSync(deploymentPath, "utf8"));
  console.log("📋 部署信息:");
  console.log("  网络:", deployment.network);
  console.log("  Chain ID:", deployment.chainId);
  console.log("  部署者:", deployment.deployer);
  console.log("  时间:", deployment.timestamp);
  console.log("");

  // 获取签名者
  const [signer] = await hre.ethers.getSigners();
  console.log("📝 当前账户:", signer.address);
  console.log("💰 账户余额:", (await signer.provider.getBalance(signer.address)).toString());
  console.log("");

  // 验证TradingVault
  console.log("📦 验证 TradingVault...");
  try {
    const TradingVault = await hre.ethers.getContractFactory("TradingVault");
    const tradingVault = TradingVault.attach(deployment.contracts.TradingVault);

    // 检查合约状态
    const owner = await tradingVault.owner();
    const totalDeposits = await tradingVault.totalDeposits();
    const isPaused = await tradingVault.paused();

    console.log("  ✅ 合约地址:", deployment.contracts.TradingVault);
    console.log("  👑 Owner:", owner);
    console.log("  💰 Total Deposits:", totalDeposits.toString());
    console.log("  ⏸️  Paused:", isPaused);
    console.log("");
  } catch (error) {
    console.error("  ❌ TradingVault 验证失败:", error.message);
  }

  // 验证StrategyExecutor
  console.log("📦 验证 StrategyExecutor...");
  try {
    const StrategyExecutor = await hre.ethers.getContractFactory("StrategyExecutor");
    const strategyExecutor = StrategyExecutor.attach(deployment.contracts.StrategyExecutor);

    // 检查合约状态
    const owner = await strategyExecutor.owner();
    const strategyCount = await strategyExecutor.strategyCount();
    const maxRiskLevel = await strategyExecutor.maxRiskLevel();

    console.log("  ✅ 合约地址:", deployment.contracts.StrategyExecutor);
    console.log("  👑 Owner:", owner);
    console.log("  📊 Strategy Count:", strategyCount.toString());
    console.log("  ⚠️  Max Risk Level:", maxRiskLevel.toString());
    console.log("");
  } catch (error) {
    console.error("  ❌ StrategyExecutor 验证失败:", error.message);
  }

  // 总结
  console.log("=".repeat(50));
  console.log("✅ 合约验证完成！");
  console.log("=".repeat(50));
  console.log("");
  console.log("🔗 在区块链浏览器查看:");
  console.log("  TradingVault:", `https://explorer.sepolia.mantle.xyz/address/${deployment.contracts.TradingVault}`);
  console.log("  StrategyExecutor:", `https://explorer.sepolia.mantle.xyz/address/${deployment.contracts.StrategyExecutor}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ 验证失败:", error);
    process.exit(1);
  });
