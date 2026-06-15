/**
 * Deployment script for Manta Trading Agent contracts
 * Deploys TradingVault and StrategyExecutor to Mantle Network
 */

const hre = require("hardhat");

async function main() {
  console.log("🚀 Starting deployment to Mantle Network...");

  // Debug: Check environment
  console.log("📋 Environment check:");
  console.log("  - RPC_URL:", process.env.RPC_URL);
  console.log("  - CHAIN_ID:", process.env.CHAIN_ID);
  console.log("  - PRIVATE_KEY exists:", !!process.env.PRIVATE_KEY);

  // Get deployer account
  let deployer;
  try {
    const signers = await hre.ethers.getSigners();
    deployer = signers[0];
    console.log("📝 Deploying with account:", deployer.address);
    console.log("💰 Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());
  } catch (error) {
    console.error("❌ Failed to get signers:", error.message);
    throw error;
  }

  // Deploy TradingVault
  console.log("\n📦 Deploying TradingVault...");

  // USDC address on Mantle (replace with actual address)
  const USDC_ADDRESS = "0x09b49b1234567890123456789012345678901234"; // Placeholder

  try {
    const TradingVault = await hre.ethers.getContractFactory("TradingVault");
    const tradingVault = await TradingVault.deploy(USDC_ADDRESS);
    await tradingVault.waitForDeployment();

    const tradingVaultAddress = await tradingVault.getAddress();
    console.log("✅ TradingVault deployed to:", tradingVaultAddress);

    // Deploy StrategyExecutor
    console.log("\n📦 Deploying StrategyExecutor...");

    const StrategyExecutor = await hre.ethers.getContractFactory("StrategyExecutor");
    const strategyExecutor = await StrategyExecutor.deploy();
    await strategyExecutor.waitForDeployment();

    const strategyExecutorAddress = await strategyExecutor.getAddress();
    console.log("✅ StrategyExecutor deployed to:", strategyExecutorAddress);

    // Summary
    console.log("\n" + "=".repeat(50));
    console.log("📋 Deployment Summary");
    console.log("=".repeat(50));
    console.log("Network:", hre.network.name);
    console.log("TradingVault:", tradingVaultAddress);
    console.log("StrategyExecutor:", strategyExecutorAddress);
    console.log("=".repeat(50));

    // Save deployment addresses
    const fs = require("fs");
    const deploymentInfo = {
      network: hre.network.name,
      chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
      contracts: {
        TradingVault: tradingVaultAddress,
        StrategyExecutor: strategyExecutorAddress
      },
      deployer: deployer.address,
      timestamp: new Date().toISOString()
    };

    const deploymentPath = `./deployments/${hre.network.name}.json`;
    fs.mkdirSync("./deployments", { recursive: true });
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));

    console.log("\n📄 Deployment info saved to:", deploymentPath);

  } catch (error) {
    console.error("❌ Deployment failed:", error.message);
    throw error;
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
