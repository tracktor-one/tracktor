"""
Module for parsing yaml files in filestructure for import and export them
"""

import os
from typing import Dict, List

import yaml
from sqlalchemy import select
from sqlmodel import Session

from tracktor.config import config
from tracktor.error import PlaylistImportError
from tracktor.models import Category, Playlist, ItemBase
from tracktor.utils.database import get_sync_session

try:
    from yaml import CLoader as Loader
    # from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader
    # from yaml import Dumper


async def parse_categories() -> Dict[str, Category]:
    """
    Parse directory structure to get directories
    """
    session: Session = next(get_sync_session())
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
    import_categories = await parse_categories()
    for category_name, category in import_categories.items():
        category_path = os.path.join(config.PLAYLIST_PATH, category_name)
        yaml_to_import = [
            p for p in os.listdir(category_path) if p.endswith((".yml", ".yaml"))
        ]
        for playlist in yaml_to_import:
            with open(os.path.join(category_path, playlist), encoding='utf-8') as playlist_file:
                content = yaml.load(playlist_file, Loader)
                content["items"] = [ItemBase(**x) for x in content["items"]]
                content["category"] = category
                playlists.append(
                    await Playlist.create(next(get_sync_session()), **content)
                )
    return playlists
