"""
V1 of the API - Tracks
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tracktor.models import ItemResponse, Item
from tracktor.utils.database import get_session

router = APIRouter(prefix="/tracks")


@router.get("/", response_model=List[ItemResponse])
async def get_all_tracks(session: AsyncSession = Depends(get_session)):
    """
    Request to return all tracks
    """
    return [ItemResponse(**x.__dict__) for x in await Item.get_all(session)]
