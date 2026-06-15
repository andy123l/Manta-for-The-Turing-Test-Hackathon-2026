"""
Configuration management for Manta trading agent.
Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class BybitConfig:
    """Bybit API configuration."""
    api_key: str = ""
    api_secret: str = ""
    testnet: bool = True


@dataclass
class MantleConfig:
    """Mantle Network configuration."""
    private_key: str = ""
    rpc_url: str = "https://rpc.testnet.mantle.xyz"
    chain_id: int = 5001
    contract_address: str = ""


@dataclass
class TradingConfig:
    """Trading parameters configuration."""
    max_position_size: float = 0.1  # 10% of capital
    max_loss_per_trade: float = 0.02  # 2% per trade
    max_daily_loss: float = 0.05  # 5% daily
    initial_capital: float = 10000.0
    symbols: list = field(default_factory=lambda: ["BTCUSDT", "ETHUSDT"])


@dataclass
class MacroConfig:
    """Macro data sources configuration."""
    fred_api_key: str = ""
    news_api_key: str = ""


@dataclass
class LogConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: str = "logs/trading.log"


class Config:
    """Main configuration class that aggregates all config sections."""

    def __init__(self):
        self.bybit = BybitConfig(
            api_key=os.getenv("BYBIT_API_KEY", ""),
            api_secret=os.getenv("BYBIT_API_SECRET", ""),
            testnet=os.getenv("BYBIT_TESTNET", "true").lower() == "true"
        )
        self.mantle = MantleConfig(
            private_key=os.getenv("PRIVATE_KEY", ""),
            rpc_url=os.getenv("RPC_URL", "https://rpc.testnet.mantle.xyz"),
            chain_id=int(os.getenv("CHAIN_ID", "5001")),
            contract_address=os.getenv("CONTRACT_ADDRESS", "")
        )
        self.trading = TradingConfig(
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "0.1")),
            max_loss_per_trade=float(os.getenv("MAX_LOSS_PER_TRADE", "0.02")),
            max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "0.05")),
            initial_capital=float(os.getenv("INITIAL_CAPITAL", "10000"))
        )
        self.macro = MacroConfig(
            fred_api_key=os.getenv("FRED_API_KEY", ""),
            news_api_key=os.getenv("NEWS_API_KEY", "")
        )
        self.logging = LogConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file=os.getenv("LOG_FILE", "logs/trading.log")
        )

    def validate(self) -> bool:
        """Validate configuration."""
        errors = []

        if not self.bybit.api_key:
            errors.append("BYBIT_API_KEY is required")
        if not self.bybit.api_secret:
            errors.append("BYBIT_API_SECRET is required")
        if not self.mantle.private_key:
            errors.append("PRIVATE_KEY is required")

        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(errors))

        return True

    def __str__(self) -> str:
        """String representation (masks sensitive data)."""
        return f"""
Manta Configuration:
---------------------
Bybit:
  API Key: {self.bybit.api_key[:8]}...{self.bybit.api_key[-4:] if len(self.bybit.api_key) > 12 else ''}
  Testnet: {self.bybit.testnet}

Mantle:
  RPC URL: {self.mantle.rpc_url}
  Chain ID: {self.mantle.chain_id}
  Contract: {self.mantle.contract_address[:10]}...{self.mantle.contract_address[-6:] if len(self.mantle.contract_address) > 16 else ''}

Trading:
  Max Position: {self.trading.max_position_size * 100}%
  Max Loss/Trade: {self.trading.max_loss_per_trade * 100}%
  Initial Capital: ${self.trading.initial_capital:,.2f}

Logging:
  Level: {self.logging.level}
"""


# Global config instance
config = Config()
