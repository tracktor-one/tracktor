"""tracktor api"""
from fastapi import FastAPI

import tracktor.sql
from tracktor.routers import admin, auth, version
from tracktor.utils.startup import app_startup, app_shutdown

app = FastAPI()
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
