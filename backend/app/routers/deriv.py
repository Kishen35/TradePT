from fastapi import APIRouter
from app.config.deriv import get_deriv_api, deriv_api_token

router = APIRouter(prefix="/deriv", tags=["deriv"])

# Get Deriv account balance
@router.get("/balance")
async def get_deriv_balance():
    api = get_deriv_api()
    await api.authorize(deriv_api_token)
    return await api.balance()

# Get Deriv account portfolio
@router.get("/portfolio")
async def get_deriv_portfolio():
    api = get_deriv_api()
    await api.authorize(deriv_api_token)
    return await api.portfolio()

# Get Deriv exchange rates
@router.get("/exchange-rates")
async def get_deriv_exchange_rates(base_currency: str = "USD"):
    api = get_deriv_api()
    await api.authorize(deriv_api_token)
    return await api.exchange_rates({"base_currency": base_currency})

# Get Deriv asset indexes
@router.get("/asset-indexes")
async def get_deriv_asset_indexes():
    api = get_deriv_api()
    await api.authorize(deriv_api_token)
    return await api.asset_index()

# Get Deriv active symbols
@router.get("/active-symbols")
async def get_deriv_active_symbols():
    api = get_deriv_api()
    await api.authorize(deriv_api_token)
    return await api.active_symbols({"active_symbols": "full"})

# Get Deriv profit table
@router.get("/profit-table")
async def get_deriv_profit_table():
    api = get_deriv_api()
    await api.authorize(deriv_api_token)
    return await api.profit_table()

# Get Deriv transaction statement
@router.get("/transaction-statement")
async def get_deriv_transaction_statement():
    api = get_deriv_api()
    await api.authorize(deriv_api_token)
    return await api.statement({"statement": 1})
