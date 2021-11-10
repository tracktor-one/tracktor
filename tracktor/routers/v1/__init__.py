"""
V1 of the API
"""

__CHANGELOG__ = """Initial Version"""

from fastapi import APIRouter

from tracktor.routers.v1.category import router as category_router
from tracktor.routers.v1.playlist import router as playlist_router
from tracktor.routers.v1.tracks import router as tracks_router

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(category_router)
router.include_router(playlist_router)
router.include_router(tracks_router)
