"""
V1 of the API - Playlist
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tracktor.error import ItemNotFoundException
from tracktor.models import PlaylistResponse, ItemResponse, Playlist
from tracktor.utils.database import get_session

router = APIRouter(prefix="/playlist")


@router.get("/", response_model=List[PlaylistResponse])
async def get_all_playlists(session: AsyncSession = Depends(get_session)):
    """
    Request to return all playlists
    """
    return [PlaylistResponse(**x.__dict__) for x in await Playlist.get_all(session)]


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(playlist_id: str, session: AsyncSession = Depends(get_session)):
    """
    Request to return a playlist
    """
    if playlist := await Playlist.get_by_entity_id(playlist_id, session):
        return PlaylistResponse(**playlist.__dict__)
    raise ItemNotFoundException(message=f"No playlist fount with id {playlist_id}")


@router.get("/{playlist_id}/tracks", response_model=List[ItemResponse])
async def get_playlist_items_of_playlist(
    playlist_id: str, session: AsyncSession = Depends(get_session)
):
    """
    Request to return all items of a playlist
    """
    if playlist := await Playlist.get_by_entity_id(playlist_id, session):
        return [ItemResponse(**x.__dict__) for x in playlist.items]
    raise ItemNotFoundException(message=f"No playlist fount with id {playlist_id}")
