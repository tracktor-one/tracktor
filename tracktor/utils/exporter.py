"""
Module for parsing yaml files in filestructure for import and export them
"""
import os
from typing import List
import base64

import yaml
from sqlmodel import Session

from tracktor.config import config
from tracktor.error import PlaylistExportError
from tracktor.models import Category, Playlist
from tracktor.utils.database import get_sync_session

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

async def dump_categories(session: Session) -> List[Category]:
    """ "
    Create directories for all categories
    """
    categories: List[Category] = await Category.get_all(session)
    for category in categories:
        os.makedirs(os.path.join(config.PLAYLIST_PATH, category.name), exist_ok=True)
    return categories


async def dump_playlists():
    """ "
    Dump all playlists existing into yaml files in the corresponding categories
    """
    session: Session = next(get_sync_session())
    exported_categories = await dump_categories(session)
    all_playlists = await Playlist.get_all(session)
    for playlist in all_playlists:
        if playlist.category not in exported_categories:
            raise PlaylistExportError(message="")
        playlist_dump = {
            "items": [{"title": x.title, "artist": x.artist} for x in playlist.items],
            "name": playlist.name,
        }
        if playlist.spotify:
            playlist_dump["spotify"] = playlist.spotify
        if playlist.amazon:
            playlist_dump["amazon"] = playlist.amazon
        if playlist.apple_music:
            playlist_dump["apple_music"] = playlist.apple_music
        if playlist.release_date:
            playlist_dump["release_date"] = playlist.release_date.strftime(
                "%Y-%m-%d %H:%M"
            )
        if playlist.image:
            with open(
                os.path.join(
                    config.PLAYLIST_PATH,
                    playlist.category.name,
                    playlist.image.file_name,
                ),
                "wb",
            ) as image_file:
                image_file.write(base64.b64decode(playlist.image.image))
            playlist_dump["image"] = playlist.image.file_name

        with open(
            os.path.join(
                config.PLAYLIST_PATH, playlist.category.name, playlist.name + ".yml"
            ),
            "w",
            encoding="utf-8",
        ) as playlist_file:
            yaml.dump(playlist_dump, playlist_file, Dumper)
