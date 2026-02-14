from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai, deriv, users

app = FastAPI(title="TradePT Backend (with Python FastAPI + SQLite)")

# Configure CORS to allow extension requests
# FOR DEVELOPMENT: Allow all origins
# FOR PRODUCTION: Replace "*" with your specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "*",
    "https://app.deriv.com",
        "http://localhost:3000",  # For development
        "http://127.0.0.1:3000",
        "chrome-extension://*",   # Allow any Chrome extension
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(ai.router)
app.include_router(deriv.router)

@app.get("/")
def health():
    return {"status": "ok"}