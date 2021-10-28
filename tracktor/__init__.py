"""
Main module for tracktor api
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import tracktor.sql
from tracktor.config import config
from tracktor.routers import admin, auth, version
from tracktor.utils.startup import app_startup, app_shutdown

app = FastAPI()

if config.CORS_DOMAIN:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            f"http://{config.CORS_DOMAIN}",
            f"https://{config.CORS_DOMAIN}"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(version.router)


@app.on_event("startup")
async def startup():
    """Connect to database and initialize admin user if not present"""
    await app_startup()


@app.on_event("shutdown")
async def shutdown():
    """Close connection to database on shutdown"""
    await app_shutdown()
