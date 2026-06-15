"""
Contract Executor for Manta trading agent.
Handles interaction with Mantle smart contracts.
"""

import json
from typing import Dict, Optional
from pathlib import Path

from web3 import Web3
from loguru import logger


class ContractExecutor:
    """
    Mantle智能合约交互器
    """

    def __init__(
        self,
        rpc_url: str,
        private_key: str,
        vault_address: str,
        executor_address: str
    ):
        """
        初始化合约交互器

        Args:
            rpc_url: Mantle RPC URL
            private_key: 钱包私钥
            vault_address: TradingVault合约地址
            executor_address: StrategyExecutor合约地址
        """
        # 连接到Mantle网络
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(private_key)

        # 合约地址
        self.vault_address = Web3.to_checksum_address(vault_address)
        self.executor_address = Web3.to_checksum_address(executor_address)

        # 加载合约ABI
        self.vault_abi = self._load_abi("TradingVault")
        self.executor_abi = self._load_abi("StrategyExecutor")

        # 创建合约实例
        self.vault = self.w3.eth.contract(
            address=self.vault_address,
            abi=self.vault_abi
        )
        self.executor = self.w3.eth.contract(
            address=self.executor_address,
            abi=self.executor_abi
        )

        logger.info(
            "Contract executor initialized",
            address=self.account.address,
            vault=self.vault_address,
            executor=self.executor_address
        )

    def _load_abi(self, contract_name: str) -> list:
        """加载合约ABI"""
        abi_path = Path(f"../contracts/artifacts/contracts/{contract_name}.sol/{contract_name}.json")

        if abi_path.exists():
            with open(abi_path, "r") as f:
                artifact = json.load(f)
                return artifact.get("abi", [])
        else:
            logger.warning(f"ABI file not found for {contract_name}")
            return []

    def get_balance(self) -> Dict:
        """获取账户余额"""
        balance = self.w3.eth.get_balance(self.account.address)
        return {
            "address": self.account.address,
            "balance_wei": balance,
            "balance_eth": self.w3.from_wei(balance, "ether")
        }

    def get_vault_info(self) -> Dict:
        """获取Vault合约信息"""
        try:
            owner = self.vault.functions.owner().call()
            total_deposits = self.vault.functions.totalDeposits().call()
            is_paused = self.vault.functions.paused().call()

            return {
                "address": self.vault_address,
                "owner": owner,
                "total_deposits": total_deposits,
                "is_paused": is_paused
            }
        except Exception as e:
            logger.error("Failed to get vault info", error=str(e))
            return {}

    def get_executor_info(self) -> Dict:
        """获取StrategyExecutor合约信息"""
        try:
            owner = self.executor.functions.owner().call()
            strategy_count = self.executor.functions.strategyCount().call()
            max_risk = self.executor.functions.maxRiskLevel().call()

            return {
                "address": self.executor_address,
                "owner": owner,
                "strategy_count": strategy_count,
                "max_risk_level": max_risk
            }
        except Exception as e:
            logger.error("Failed to get executor info", error=str(e))
            return {}

    def deposit(self, amount: int) -> Dict:
        """
        存入资金到Vault

        Args:
            amount: 存入金额（以wei为单位）

        Returns:
            交易结果
        """
        try:
            # 构建交易
            tx = self.vault.functions.deposit(amount).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('50', 'gwei')
            })

            # 签名并发送交易
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # 等待交易确认
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(
                "Deposit successful",
                amount=amount,
                tx_hash=tx_hash.hex(),
                gas_used=receipt.gasUsed
            )

            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "gas_used": receipt.gasUsed
            }

        except Exception as e:
            logger.error("Deposit failed", error=str(e))
            return {"success": False, "error": str(e)}

    def withdraw(self, amount: int) -> Dict:
        """
        从Vault提取资金

        Args:
            amount: 提取金额（以wei为单位）

        Returns:
            交易结果
        """
        try:
            tx = self.vault.functions.withdraw(amount).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('50', 'gwei')
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(
                "Withdraw successful",
                amount=amount,
                tx_hash=tx_hash.hex(),
                gas_used=receipt.gasUsed
            )

            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "gas_used": receipt.gasUsed
            }

        except Exception as e:
            logger.error("Withdraw failed", error=str(e))
            return {"success": False, "error": str(e)}

    def execute_trade(self, target: str, data: bytes, value: int = 0) -> Dict:
        """
        通过Vault执行交易

        Args:
            target: 目标合约地址
            data: 编码的函数调用数据
            value: ETH值

        Returns:
            交易结果
        """
        try:
            tx = self.vault.functions.executeTrade(
                Web3.to_checksum_address(target),
                data,
                value
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,
                'gasPrice': self.w3.to_wei('50', 'gwei')
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(
                "Trade executed",
                tx_hash=tx_hash.hex(),
                gas_used=receipt.gasUsed
            )

            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "gas_used": receipt.gasUsed
            }

        except Exception as e:
            logger.error("Trade execution failed", error=str(e))
            return {"success": False, "error": str(e)}

    def get_user_balance(self, user_address: str) -> int:
        """获取用户在Vault中的余额"""
        try:
            return self.vault.functions.getBalance(
                Web3.to_checksum_address(user_address)
            ).call()
        except Exception as e:
            logger.error("Failed to get user balance", error=str(e))
            return 0

    def get_trade_count(self) -> int:
        """获取Vault中的交易总数"""
        try:
            return self.vault.functions.getTradeCount().call()
        except Exception as e:
            logger.error("Failed to get trade count", error=str(e))
            return 0
