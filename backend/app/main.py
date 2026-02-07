from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.db import SessionLocal
from app.routers import users, ai_insights

app = FastAPI(
    title="TradePT Backend (with Python FastAPI + SQLite)",
    description="AI-powered trading education platform API",
    version="1.0.0"
)

# CORS middleware for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(ai_insights.router)

@app.get("/")
def health():
    return {"status": "ok"}
