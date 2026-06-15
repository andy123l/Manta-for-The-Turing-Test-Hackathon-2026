"""
Bybit API Client for Manta trading agent.
Handles REST and WebSocket connections to Bybit exchange.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

import pandas as pd
from pybit.unified_trading import HTTP, WebSocket
from loguru import logger


class BybitClient:
    """
    Bybit API client for market data and trading operations.

    Features:
    - Real-time price data via REST API
    - Historical OHLCV (K-line) data
    - Order book data
    - Order placement and management
    - Position tracking
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = True
    ):
        """
        Initialize Bybit client.

        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            testnet: Use testnet (default: True)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        # Initialize REST client
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )

        logger.info(
            "Bybit client initialized",
            testnet=testnet
        )

    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict:
        """
        Get real-time ticker data.

        Args:
            symbol: Trading pair (default: BTCUSDT)

        Returns:
            Dictionary with ticker information
        """
        try:
            response = self.session.get_tickers(
                category="linear",
                symbol=symbol
            )

            if response["retCode"] == 0:
                ticker = response["result"]["list"][0]
                return {
                    "symbol": ticker["symbol"],
                    "last_price": float(ticker["lastPrice"]),
                    "bid_price": float(ticker["bid1Price"]),
                    "ask_price": float(ticker["ask1Price"]),
                    "volume_24h": float(ticker["volume24h"]),
                    "price_change_24h": float(ticker["price24hPcnt"]),
                    "high_24h": float(ticker["highPrice24h"]),
                    "low_24h": float(ticker["lowPrice24h"]),
                    "timestamp": datetime.now()
                }
            else:
                logger.error("Failed to get ticker", response=response)
                return {}

        except Exception as e:
            logger.error("Error getting ticker", error=str(e))
            return {}

    async def get_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get historical OHLCV (K-line) data.

        Args:
            symbol: Trading pair
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles

        Returns:
            DataFrame with OHLCV data
        """
        try:
            response = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit
            )

            if response["retCode"] == 0:
                klines = response["result"]["list"]

                df = pd.DataFrame(klines, columns=[
                    "timestamp", "open", "high", "low", "close", "volume", "turnover"
                ])

                # Convert types
                df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="ms")
                for col in ["open", "high", "low", "close", "volume", "turnover"]:
                    df[col] = df[col].astype(float)

                df = df.sort_values("timestamp").reset_index(drop=True)

                logger.info(
                    "Got klines",
                    symbol=symbol,
                    interval=interval,
                    count=len(df)
                )

                return df
            else:
                logger.error("Failed to get klines", response=response)
                return pd.DataFrame()

        except Exception as e:
            logger.error("Error getting klines", error=str(e))
            return pd.DataFrame()

    async def get_orderbook(
        self,
        symbol: str = "BTCUSDT",
        limit: int = 20
    ) -> Dict:
        """
        Get order book data.

        Args:
            symbol: Trading pair
            limit: Depth limit

        Returns:
            Dictionary with bids and asks
        """
        try:
            response = self.session.get_orderbook(
                category="linear",
                symbol=symbol,
                limit=limit
            )

            if response["retCode"] == 0:
                orderbook = response["result"]

                return {
                    "bids": [(float(p), float(q)) for p, q in orderbook["b"]],
                    "asks": [(float(p), float(q)) for p, q in orderbook["a"]],
                    "timestamp": datetime.now()
                }
            else:
                logger.error("Failed to get orderbook", response=response)
                return {"bids": [], "asks": []}

        except Exception as e:
            logger.error("Error getting orderbook", error=str(e))
            return {"bids": [], "asks": []}

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        order_type: str = "Market"
    ) -> Dict:
        """
        Place a trading order.

        Args:
            symbol: Trading pair
            side: "Buy" or "Sell"
            quantity: Order quantity
            price: Limit price (None for market orders)
            order_type: "Market" or "Limit"

        Returns:
            Order result dictionary
        """
        try:
            params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(quantity)
            }

            if order_type == "Limit" and price is not None:
                params["price"] = str(price)

            response = self.session.place_order(**params)

            if response["retCode"] == 0:
                order = response["result"]
                logger.info(
                    "Order placed",
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    order_id=order["orderId"]
                )
                return {
                    "success": True,
                    "order_id": order["orderId"],
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity
                }
            else:
                logger.error("Failed to place order", response=response)
                return {"success": False, "error": response["retMsg"]}

        except Exception as e:
            logger.error("Error placing order", error=str(e))
            return {"success": False, "error": str(e)}

    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """
        Cancel an order.

        Args:
            symbol: Trading pair
            order_id: Order ID to cancel

        Returns:
            Cancellation result
        """
        try:
            response = self.session.cancel_order(
                category="linear",
                symbol=symbol,
                orderId=order_id
            )

            if response["retCode"] == 0:
                logger.info("Order cancelled", order_id=order_id)
                return {"success": True, "order_id": order_id}
            else:
                logger.error("Failed to cancel order", response=response)
                return {"success": False, "error": response["retMsg"]}

        except Exception as e:
            logger.error("Error cancelling order", error=str(e))
            return {"success": False, "error": str(e)}

    async def get_position(self, symbol: str) -> Dict:
        """
        Get current position for a symbol.

        Args:
            symbol: Trading pair

        Returns:
            Position information
        """
        try:
            response = self.session.get_positions(
                category="linear",
                symbol=symbol
            )

            if response["retCode"] == 0:
                positions = response["result"]["list"]

                if positions:
                    pos = positions[0]
                    return {
                        "symbol": pos["symbol"],
                        "side": pos["side"],
                        "size": float(pos["size"]),
                        "entry_price": float(pos["avgPrice"]),
                        "unrealised_pnl": float(pos["unrealisedPnl"]),
                        "leverage": float(pos["leverage"])
                    }
                else:
                    return {
                        "symbol": symbol,
                        "side": "None",
                        "size": 0,
                        "entry_price": 0,
                        "unrealised_pnl": 0,
                        "leverage": 0
                    }
            else:
                logger.error("Failed to get position", response=response)
                return {}

        except Exception as e:
            logger.error("Error getting position", error=str(e))
            return {}

    async def get_account_balance(self) -> Dict:
        """
        Get account balance.

        Returns:
            Balance information
        """
        try:
            response = self.session.get_wallet_balance(
                accountType="UNIFIED"
            )

            if response["retCode"] == 0:
                account = response["result"]["list"][0]
                return {
                    "total_equity": float(account["totalEquity"]),
                    "available_balance": float(account["availableToWithdraw"]),
                    "unrealised_pnl": float(account["totalUnrealisedPnl"])
                }
            else:
                logger.error("Failed to get balance", response=response)
                return {}

        except Exception as e:
            logger.error("Error getting balance", error=str(e))
            return {}
