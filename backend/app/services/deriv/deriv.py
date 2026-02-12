"""
Deriv Market Data Service

Fetches real-time market data from Deriv API to provide context
for AI-generated responses and insights.
"""

from typing import Dict, Any, Optional, List
from app.services.logger.logger import logger
from app.config.deriv import deriv_api_token, DerivAPI, deriv_app_id
from app.services.deriv.typings import AccountInfo
import asyncio

# TODO: check typings and update as needed

class DerivService:
    """
    Service for fetching market data from Deriv API.

    Uses the python-deriv-api to get real-time prices, account balance,
    and portfolio information to enhance AI context.
    """

    def __init__(self):
        """Initialize the market service."""
        self._token = deriv_api_token
        self._is_authorized = False
        self._api = None

    def _get_deriv_api(self):
        """Get the configured Deriv API instance, lazy-loaded and reconnect if closed."""
        reconnect = False

        if self._api is None:
            reconnect = True
        else:
            # Check if the WebSocket inside DerivAPI exists and is open
            try:
                # Some DerivAPI clients use self.ws.sock.connected
                if not getattr(self._api, 'ws', None) or not getattr(self._api.ws, 'sock', None) or not self._api.ws.sock.connected:
                    reconnect = True
            except Exception:
                reconnect = True

        if reconnect:
            self._api = DerivAPI(app_id=deriv_app_id)

    async def get_account_balance(self) -> Optional[AccountInfo]:
        """
        Get user's account balance from Deriv.

        Returns:
            AccountInfo with balance details, or None if unavailable
        """
        self._get_deriv_api()
        if not self._api:
            return None

        try:
            await self._api.authorize(self._token)
            balance_response = await self._api.balance()
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
        self._get_deriv_api()
        if not self._api:
            return None

        try:
            await self._api.authorize(self._token)
            portfolio_response = await self._api.portfolio()

            if portfolio_response and "portfolio" in portfolio_response:
                contracts = portfolio_response["portfolio"].get("contracts", [])
                
                # Enrich contracts with real-time profit data
                async def fetch_contract_details(contract):
                    try:
                        poc = await self._api.proposal_open_contract({"contract_id": contract["contract_id"]})
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
        self._get_deriv_api()
        if not self._api:
            return None

        try:
            await self._api.authorize(self._token)
            rates_response = await self._api.exchange_rates({"base_currency": base_currency})

            if rates_response and "exchange_rates" in rates_response:
                return rates_response["exchange_rates"].get("rates", {})
        except Exception as e:
            logger.error(f"Failed to fetch exchange rates: {e}")

        return None

    async def get_recent_trades(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent completed trades (profit table).

        Args:
            limit: Number of trades to return

        Returns:
            List of trade dictionaries
        """
        self._get_deriv_api()
        if not self._api:
            return []

        try:
            # API call for profit table
            # "description": 1 gets full details, "sort": "DESC" puts newest first usually, 
            # but standard API might just return list. We'll slice it.
            await self._api.authorize(self._token)
            response = await self._api.profit_table({"limit": limit, "description": 1})
            
            if response and "profit_table" in response:
                transactions = response["profit_table"].get("transactions", [])
                # Ensure they are sorted by purchase_time descending if API doesn't guarantee
                # transactions.sort(key=lambda x: x.get('purchase_time', 0), reverse=True)
                return transactions[:limit]
        except Exception as e:
            logger.error(f"Failed to fetch profit table: {e}")
        
        return []

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
_deriv_service: Optional[DerivService] = None

def get_deriv_service() -> DerivService:
    """Get the singleton DerivService instance."""
    global _deriv_service
    if _deriv_service is None:
        _deriv_service = DerivService()
    return _deriv_service

# Example usage
if __name__ == "__main__":
    service = get_deriv_service()
    account_balance = asyncio.get_event_loop().run_until_complete(service.get_account_balance())
    print(f"Account Balance: {account_balance}")
    portfolio = asyncio.get_event_loop().run_until_complete(service.get_portfolio())
    print(f"Portfolio: {portfolio}")
    exchange_rates = asyncio.get_event_loop().run_until_complete(service.get_exchange_rates())
    print(f"Exchange Rates: {exchange_rates}")
    recent_trades = asyncio.get_event_loop().run_until_complete(service.get_recent_trades())
    print(f"Recent Trades: {recent_trades}")
    market_context = asyncio.get_event_loop().run_until_complete(service.get_market_context(preferred_assets=["EURUSD", "GBPUSD", "USDJPY"]))
    print(f"Market Context:\n{market_context}")
    market_context_safe = asyncio.get_event_loop().run_until_complete(service.get_market_context_safe(preferred_assets=["EURUSD", "GBPUSD", "USDJPY"]))
    print(f"Market Context Safe:\n{market_context_safe}")