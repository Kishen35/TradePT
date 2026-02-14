from fastapi import APIRouter
from app.config.deriv import deriv_api_token
from app.services.deriv.deriv import get_deriv_service

router = APIRouter(prefix="/deriv", tags=["deriv"])

# Get Deriv account balance
@router.get("/balance")
async def get_deriv_balance():
    api = get_deriv_service()
    return await api.get_account_balance()

# Get Deriv account portfolio
@router.get("/portfolio")
async def get_deriv_portfolio():
    api = get_deriv_service()
    return await api.get_portfolio()

# Get Deriv exchange rates
@router.get("/exchange-rates")
async def get_deriv_exchange_rates(base_currency: str = "USD"):
    api = get_deriv_service()
    return await api.get_exchange_rates(base_currency)

# Get Deriv asset indexes
# @router.get("/asset-indexes")
# async def get_deriv_asset_indexes():
#     api = get_deriv_service()
#     return await api.get_asset_indexes()

# # Get Deriv active symbols
# @router.get("/active-symbols")
# async def get_deriv_active_symbols():
#     api = get_deriv_service()
#     return await api.get_active_symbols()

# Get Deriv profit table
# @router.get("/profit-table")
# async def get_deriv_profit_table():
#     api = get_deriv_service()
#     return await api.get_profit_table()

# # Get Deriv transaction statement
# @router.get("/transaction-statement")
# async def get_deriv_transaction_statement():
#     api = get_deriv_service()
#     return await api.get_transaction_statement()