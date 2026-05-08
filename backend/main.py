"""
F1 Analytics Platform — FastAPI Backend.

Wraps existing Python ML modules as REST endpoints for the Next.js frontend.
Includes request timeout protection and concurrency limits.
"""
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.routers import telemetry, laps, results, tracks, ml

app = FastAPI(title="F1 Analytics API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Concurrency limiter for heavy FastF1 loads ──────────────────────────────
_semaphore = asyncio.Semaphore(3)  # max 3 concurrent session loads

@app.middleware("http")
async def limit_concurrency(request: Request, call_next):
    """Limit concurrent heavy requests and add timeout protection."""
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        try:
            async with asyncio.timeout(180):  # 3 minute timeout
                async with _semaphore:
                    return await call_next(request)
        except TimeoutError:
            return JSONResponse(status_code=504, content={"detail": "Request timed out (180s). FastF1 download may be slow."})
    return await call_next(request)

app.include_router(telemetry.router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(laps.router, prefix="/api/laps", tags=["Laps"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(tracks.router, prefix="/api/tracks", tags=["Tracks"])
app.include_router(ml.router, prefix="/api/ml", tags=["ML Pipeline"])

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
