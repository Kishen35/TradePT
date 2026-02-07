from fastapi import FastAPI
from app.routers import ai, deriv, users

app = FastAPI(title="TradePT Backend (with Python FastAPI + SQLite)")

app.include_router(users.router)
app.include_router(ai.router)
app.include_router(deriv.router)

@app.get("/")
def health():
    return {"status": "ok"}
