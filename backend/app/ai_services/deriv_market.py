"""
Deriv Market Data Service

Fetches real-time market data from Deriv API to provide context
for AI-generated responses and insights.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class MarketSnapshot:
    """Current market data for a symbol."""
    symbol: str
    current_price: float
    change_percent: float
    timestamp: datetime


@dataclass
class AccountInfo:
    """User's account information from Deriv."""
    balance: float
    currency: str
    open_positions: int


class DerivMarketService:
    """
    Service for fetching market data from Deriv API.

    Uses the python-deriv-api to get real-time prices, account balance,
    and portfolio information to enhance AI context.
    """

    def __init__(self):
        """Initialize the market service."""
        self._api = None
        self._token = None
        self._is_authorized = False

    def _get_api(self):
        """Lazy load the Deriv API client."""
        if self._api is None:
            try:
                from app.config.deriv import get_deriv_api, deriv_api_token
                self._api = get_deriv_api()
                self._token = deriv_api_token
            except ImportError as e:
                logger.error(f"Failed to import Deriv API: {e}")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Deriv API: {e}")
                return None
        return self._api

    async def _ensure_authorized(self) -> bool:
        """Ensure the API is authorized."""
        if self._is_authorized:
            return True

        api = self._get_api()
        if not api or not self._token:
            return False

        try:
            await api.authorize(self._token)
            self._is_authorized = True
            return True
        except Exception as e:
            logger.error(f"Failed to authorize Deriv API: {e}")
            return False

    async def get_account_balance(self) -> Optional[AccountInfo]:
        """
        Get user's account balance from Deriv.

        Returns:
            AccountInfo with balance details, or None if unavailable
        """
        api = self._get_api()
        if not api:
            return None

        try:
            if not await self._ensure_authorized():
                return None

            balance_response = await api.balance()

            if balance_response and "balance" in balance_response:
                balance_data = balance_response["balance"]
                return AccountInfo(
                    balance=float(balance_data.get("balance", 0)),
                    currency=balance_data.get("currency", "USD"),
                    open_positions=0  # Will be updated from portfolio
                )
        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")

        return None

    async def get_portfolio(self) -> Optional[Dict[str, Any]]:
        """
        Get user's current portfolio/positions from Deriv.

        Returns:
            Dictionary with portfolio data, or None if unavailable
        """
        api = self._get_api()
        if not api:
            return None

        try:
            if not await self._ensure_authorized():
                return None

            portfolio_response = await api.portfolio()

            if portfolio_response and "portfolio" in portfolio_response:
                contracts = portfolio_response["portfolio"].get("contracts", [])
                
                # Enrich contracts with real-time profit data
                async def fetch_contract_details(contract):
                    try:
                        poc = await api.proposal_open_contract({"contract_id": contract["contract_id"]})
                        if poc and "proposal_open_contract" in poc:
                            details = poc["proposal_open_contract"]
                            contract["profit"] = details.get("profit", 0)
                            contract["current_price"] = details.get("bid_price", 0)
                    except Exception as e:
                        logger.warning(f"Failed to fetch details for contract {contract.get('contract_id')}: {e}")
                    return contract

                if contracts:
                    contracts = await asyncio.gather(*[fetch_contract_details(c) for c in contracts])

                return {
                    "positions_count": len(contracts),
                    "contracts": contracts
                }
        except Exception as e:
            logger.error(f"Failed to fetch portfolio: {e}")

        return None

    async def get_exchange_rates(self, base_currency: str = "USD") -> Optional[Dict[str, float]]:
        """
        Get exchange rates from Deriv.

        Args:
            base_currency: The base currency for rates

        Returns:
            Dictionary of currency rates, or None if unavailable
        """
        api = self._get_api()
        if not api:
            return None

        try:
            if not await self._ensure_authorized():
                return None

            rates_response = await api.exchange_rates({"base_currency": base_currency})

            if rates_response and "exchange_rates" in rates_response:
                return rates_response["exchange_rates"].get("rates", {})
        except Exception as e:
            logger.error(f"Failed to fetch exchange rates: {e}")

        return None

    async def get_market_context(self, preferred_assets: List[str] = None) -> str:
        """
        Build a market context string for AI prompts.

        Combines balance, portfolio, and market data into a formatted
        string suitable for including in LLM prompts.

        Args:
            preferred_assets: List of symbols the user prefers

        Returns:
            Formatted market context string
        """
        context_parts = []

        # Get account balance
        try:
            account = await self.get_account_balance()
            if account:
                context_parts.append(f"Account Balance: {account.currency} {account.balance:,.2f}")
        except Exception as e:
            logger.warning(f"Could not fetch account balance: {e}")

        # Get portfolio
        try:
            portfolio = await self.get_portfolio()
            if portfolio:
                positions = portfolio.get("positions_count", 0)
                context_parts.append(f"Open Positions: {positions}")

                if positions > 0 and "contracts" in portfolio:
                    contracts = portfolio["contracts"][:3]  # Show first 3
                    for contract in contracts:
                        symbol = contract.get("symbol", "Unknown")
                        pnl = contract.get("profit", 0)
                        context_parts.append(f"  - {symbol}: P&L ${pnl:,.2f}")
        except Exception as e:
            logger.warning(f"Could not fetch portfolio: {e}")

        # Get exchange rates for preferred assets
        if preferred_assets:
            try:
                rates = await self.get_exchange_rates()
                if rates:
                    context_parts.append("Current Rates:")
                    for asset in preferred_assets[:3]:  # Limit to 3
                        if asset in rates:
                            context_parts.append(f"  - {asset}: {rates[asset]:.4f}")
            except Exception as e:
                logger.warning(f"Could not fetch exchange rates: {e}")

        if context_parts:
            return "\n".join(context_parts)
        else:
            return "Market data temporarily unavailable"

    async def get_market_context_safe(self, preferred_assets: List[str] = None) -> str:
        """
        Safely get market context with fallback.

        This version catches all exceptions and returns a fallback message
        to ensure the chat service can continue operating.

        Args:
            preferred_assets: List of symbols the user prefers

        Returns:
            Formatted market context string or fallback message
        """
        try:
            return await asyncio.wait_for(
                self.get_market_context(preferred_assets),
                timeout=5.0  # 5 second timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Market data fetch timed out")
            return "Market data fetch timed out - using cached context"
        except Exception as e:
            logger.error(f"Error fetching market context: {e}")
            return "Market data temporarily unavailable"


# Singleton instance
_market_service: Optional[DerivMarketService] = None


def get_market_service() -> DerivMarketService:
    """Get the singleton DerivMarketService instance."""
    global _market_service
    if _market_service is None:
        _market_service = DerivMarketService()
    return _market_service
