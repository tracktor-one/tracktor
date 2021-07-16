import sys
from operator import attrgetter

from flask import jsonify
from packaging.version import Version

from app import app


def _get_versions() -> dict:
    return {x: attrgetter(f"{x}.__CHANGELOG__")(sys.modules[__package__]) for x in dir(sys.modules[__package__]) if
            x.startswith("v") and x != "version"}


@app.route('/versions')
def list_versions():
    return jsonify(_get_versions())


@app.route('/version')
def latest_version():
    return jsonify(version=sorted([Version(x) for x in _get_versions().keys()])[0].__str__())
