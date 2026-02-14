import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from app.routers import ai, deriv, users
from app.routers.education import router as education_router

app = FastAPI(title="TradePT Backend (with Python FastAPI + SQLite)")

# Configure CORS to allow extension requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
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
app.include_router(education_router)

# Resolve extension directory for static files
EXTENSION_DIR = Path(__file__).resolve().parent.parent.parent / "extension"

@app.get("/")
def health():
    return {"status": "ok"}

# Style-profiling page route
@app.get("/style-profiling", response_class=HTMLResponse)
async def style_profiling(request: Request):
    html_path = EXTENSION_DIR / "views" / "questionnaire.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

# Serve static files from extension directory (must be AFTER API routes)
if EXTENSION_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(EXTENSION_DIR)), name="static")
