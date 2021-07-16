from app import app


@app.route('/v1/playlists')
def v1_playlists():
    pass


@app.route('/v1/playlists/<playlist_id>')
def v1_playlist(playlist_id: str):
    pass


@app.route('/v1/playlists/<playlist_id>/tracks')
def v1_playlist_tracks(playlist_id: str):
    pass


@app.route('/v1/categories')
def v1_categories():
    pass


@app.route('/v1/<category_name>')
def v1_category(category_name: str):
    pass


@app.route('/v1/tracks')
def v1_tracks():
    pass


@app.route('/v1/sources')
def v1_sources():
    pass
