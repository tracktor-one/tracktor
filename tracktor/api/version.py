import sys
from operator import attrgetter
from typing import List

from tracktor import app
from tracktor.models import VersionModel


def _get_versions() -> List[VersionModel]:
    return [VersionModel(version=x, changelog=attrgetter(f"{x}.__CHANGELOG__")(sys.modules[__package__])) for x in
            dir(sys.modules[__package__]) if
            x.startswith("v") and x != "version"]


@app.get('/versions', response_model=List[VersionModel])
async def list_versions():
    return _get_versions()


@app.get('/version')
def latest_version():
    return sorted([x.version for x in _get_versions()])[0]
