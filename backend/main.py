import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import Base, engine, run_compat_migrations
from backend import models  # noqa: F401
from backend.routers import (
    auth_routes,
    bots,
    commands,
    webhook,
    points,
    error_logs,
    broadcast,
    schedule,
    settings as settings_router,
    custom_webhook,
    broadcast_v2,
    import_export,
    matrix_api,
)
from backend.scheduler.scheduler import start_scheduler

run_compat_migrations()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BOT MATRIX Platform", version="2.0.0")


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


_default_origins = "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:3000,http://localhost:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(bots.router)
app.include_router(commands.router)
app.include_router(webhook.router)
app.include_router(points.router)
app.include_router(error_logs.router)
app.include_router(broadcast.router)
app.include_router(schedule.router)
app.include_router(settings_router.router)
app.include_router(custom_webhook.router)
app.include_router(broadcast_v2.router)
app.include_router(import_export.router)
app.include_router(matrix_api.router)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))
else:
    @app.get("/")
    def root():
        return {"platform": "BOT MATRIX", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health")
ndef health():
    return {"status": "ok", "platform": "BOT MATRIX Engine", "version": "2.0.0"}


@app.on_event("startup")
def on_startup():
    start_scheduler()
