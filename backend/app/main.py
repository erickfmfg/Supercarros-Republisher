from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, brands, schedules, stats, users, manual
from app.core.config import settings
from app.db.session import init_db
from app.services.scheduler import start_scheduler, shutdown_scheduler


def create_app() -> FastAPI:
    app = FastAPI(title="SuperCarros Republishing Scheduler")

    # CORS (ajusta origins según tu red)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # en producción limita esto
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rutas
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
    app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
    app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(manual.router, prefix="/api/manual", tags=["manual"])

    # ✅ Health check para EB / Load Balancer
    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok", "app": settings.APP_NAME}

    @app.on_event("startup")
    async def on_startup():
        init_db()
        start_scheduler()

    @app.on_event("shutdown")
    async def on_shutdown():
        shutdown_scheduler()

    return app


app = create_app()
