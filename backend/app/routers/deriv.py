from fastapi import APIRouter
from app.config.deriv import deriv_api, deriv_api_token

router = APIRouter(prefix="/deriv", tags=["deriv"])

# Get Deriv account balance
@router.get("/balance")
async def get_deriv_balance():
    await deriv_api.authorize(deriv_api_token)
    return await deriv_api.balance()

# Get Deriv account portfolio
@router.get("/portfolio")
async def get_deriv_portfolio():
    await deriv_api.authorize(deriv_api_token)
    return await deriv_api.portfolio()

# Get Deriv exchange rates
@router.get("/exchange-rates")
async def get_deriv_exchange_rates(base_currency: str = "USD"):
    await deriv_api.authorize(deriv_api_token)
    return await deriv_api.exchange_rates({"base_currency": base_currency})

# Get Deriv asset indexes
@router.get("/asset-indexes")
async def get_deriv_asset_indexes():
    await deriv_api.authorize(deriv_api_token)
    return await deriv_api.asset_index()

# Get Deriv active symbols
@router.get("/active-symbols")
async def get_deriv_active_symbols():
    await deriv_api.authorize(deriv_api_token)
    return await deriv_api.active_symbols({"active_symbols": "full"})

# Get Deriv profit table
@router.get("/profit-table")
async def get_deriv_profit_table():
    await deriv_api.authorize(deriv_api_token)
    return await deriv_api.profit_table()

# Get Deriv transaction statement
@router.get("/transaction-statement")
async def get_deriv_transaction_statement():
    await deriv_api.authorize(deriv_api_token)
    return await deriv_api.statement({"statement": 1})