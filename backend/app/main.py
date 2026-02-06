from fastapi import FastAPI
from app.config.db import SessionLocal
from app.routers import users

app = FastAPI(title="TradePT Backend (with Python FastAPI + SQLite)")

app.include_router(users.router)

@app.get("/")
def health():
    return {"status": "ok"}
