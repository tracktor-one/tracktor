"""
Module for parsing yaml files in filestructure for import and export them
"""
import datetime
import os
from typing import Dict, List

import yaml
from sqlalchemy import select
from sqlmodel import Session
from datetime import datetime

from tracktor.config import config
from tracktor.error import PlaylistImportError, PlaylistExportError
from tracktor.models import Category, Playlist, ItemBase
from tracktor.utils.database import get_sync_session

try:
    from yaml import CLoader as Loader, Dumper
except ImportError:
    from yaml import Loader, Dumper


async def parse_categories(session: Session) -> Dict[str, Category]:
    """
    Parse directory structure to get directories
    """
    if not os.path.isdir(config.PLAYLIST_PATH):
        raise PlaylistImportError("Path does not exist")
    import_categories = {}
    for directory in os.listdir(config.PLAYLIST_PATH):
        if (
            category := session.execute(
                select(Category).where(Category.name == directory)
            )
            .scalars()
            .first()
        ):
            import_categories[directory] = category
        else:
            category = await Category.create(session, directory)
            import_categories[directory] = category
    return import_categories


async def parse_playlists() -> List[Playlist]:
    """
    Parse all yaml files in the given path, match them to categories and import them
    """
    playlists = []
    session: Session = next(get_sync_session())
    import_categories = await parse_categories(session)
    for category_name, category in import_categories.items():
        category_path = os.path.join(config.PLAYLIST_PATH, category_name)
        yaml_to_import = [
            p for p in os.listdir(category_path) if p.endswith((".yml", ".yaml"))
        ]
        for playlist in yaml_to_import:
            with open(
                os.path.join(category_path, playlist), encoding="utf-8"
            ) as playlist_file:
                content = yaml.load(playlist_file, Loader)
                content["items"] = [ItemBase(**x) for x in content["items"]]
                content["category"] = category
                if content.get("release_date"):
                    content["release_date"] = datetime.strptime(
                        content["release_date"], "%Y-%m-%d %H:%M"
                    )
                playlists.append(await Playlist.create(session, **content))
    return playlists


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
        # TODO: Add image to dump
        with open(
            os.path.join(
                config.PLAYLIST_PATH, playlist.category.name, playlist.name + ".yml"
            ),
            "w",
            encoding="utf-8",
        ) as playlist_file:
            yaml.dump(playlist_dump, playlist_file, Dumper)
