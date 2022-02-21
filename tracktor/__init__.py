"""
Main module for tracktor api
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tracktor.config import config
from tracktor.routers import admin, auth, version, v1
from tracktor.utils.exporter import dump_playlists
from tracktor.utils.importer import parse_playlists


app = FastAPI()

if config.CORS_DOMAIN:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[f"http://{config.CORS_DOMAIN}", f"https://{config.CORS_DOMAIN}"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(version.router)
app.include_router(v1.router)


@app.on_event("startup")
async def startup():
    """
    Run on application startup
    """
    await parse_playlists()


@app.on_event("shutdown")
async def shutdown():
    """
    Run on application startup
    """
    await dump_playlists()
