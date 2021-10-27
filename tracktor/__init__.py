"""
Main module for tracktor api
"""
from fastapi import FastAPI, logger
from fastapi.middleware.cors import CORSMiddleware

from tracktor.config import config
from tracktor.routers import admin, auth, version

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
