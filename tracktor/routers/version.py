"""
Module for version router

Contains functions and api endpoints for version listing
"""
import sys
from operator import attrgetter
from typing import List

from fastapi import APIRouter

from tracktor.error import ItemNotFoundException
from tracktor.models import VersionModel

router = APIRouter(
    prefix="/versions",
    tags=["version"]
)


def _get_versions() -> List[VersionModel]:
    return [VersionModel(version=x,
                         changelog=attrgetter(f"{x}.__CHANGELOG__")(sys.modules[__package__]))
            for x in dir(sys.modules[__package__]) if
            x.startswith("v") and x != "version" and x != "version_router"]


@router.get('/', response_model=List[VersionModel])
async def list_versions():
    """
    Request to list all versions
    """
    return _get_versions()


@router.get('/latest')
def latest_version():
    """
    Request to return the latest version
    """
    try:
        return sorted([x.version for x in _get_versions()])[0]
    except IndexError as err:
        raise ItemNotFoundException from err
