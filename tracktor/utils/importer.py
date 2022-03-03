"""
Module for parsing yaml files in filestructure for import and export them
"""
import base64
import datetime
import os
from datetime import datetime
from typing import Dict, List

import yaml
from sqlalchemy import select
from sqlmodel import Session

from tracktor.config import config
from tracktor.error import PlaylistImportError
from tracktor.models import Category, Playlist, ItemBase, Image
from tracktor.utils.database import get_sync_session

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


async def parse_categories(
    session: Session = next(get_sync_session()),
) -> Dict[str, Category]:
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


async def parse_playlists(
    session: Session = next(get_sync_session()),
) -> List[Playlist]:
    """
    Parse all yaml files in the given path, match them to categories and import them
    """
    playlists = []
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

                content["items"] = [ItemBase(**x) for x in content.get("items", [])]
                content["category"] = category
                if content.get("release_date"):
                    content["release_date"] = datetime.strptime(
                        content["release_date"], "%Y-%m-%d %H:%M"
                    )
                if content.get("image"):
                    with open(
                        os.path.join(category_path, content["image"]), "rb"
                    ) as image_file:
                        content["image"] = await Image.create(
                            session,
                            content["image"],
                            base64.b64encode(image_file.read()),
                        )
                playlists.append(await Playlist.create(session, **content))
    return playlists
