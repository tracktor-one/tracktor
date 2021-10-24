import json

from sqlalchemy import UniqueConstraint

from app import db
from app.error import PlaylistItemConflict


class Playlist(db.Model):
    __tablename__ = 'playlist'


class PlaylistItem(db.Model):
    __tablename__ = 'playlist_item'
    __table_args__ = (
        UniqueConstraint('title', 'artist'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True)
    artist = db.Column(db.String(50), unique=True)

    @staticmethod
    def from_json(json_string: str):
        json_obj = json.loads(json_string)
        title = json_obj.get("title")
        artist = json_obj.get("artist")
        if not title or not artist:
            raise PlaylistItemConflict("Malformed PlaylistItem")
        check_item = PlaylistItem.query.filter_by(title=title, artist=artist).first()
        if check_item:
            return check_item
        new_item = PlaylistItem(
            title=title,
            artist=artist
        )
        db.session.add(new_item)
        db.session.commit()
        return new_item

    def to_json(self) -> dict:
        return {
            "id": self.id, "title": self.title,
            "artist": self.artist
        }
