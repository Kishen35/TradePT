from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai, deriv, users

app = FastAPI(title="TradePT Backend (with Python FastAPI + SQLite)")

# CORS middleware - allows Chrome extension to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(ai.router)
app.include_router(deriv.router)

@app.get("/")
def health():
    return {"status": "ok"}
