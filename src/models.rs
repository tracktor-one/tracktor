use error::*;
use regex::Regex;
use std::path::Path;

pub struct Playlist {
    id: i32,
    title: String,
    spotify: SpotifyUrl,
    amusic: AmusicUrl,
    tracks: Vec<Track>,
    image: Path,
}

pub struct SpotifyUrl {
    user: String,
    id: String,
}

pub struct AmusicUrl {
    link_name: String,
    id: String,
}

pub struct Track {
    uid:
    title: String,
    interpret: String,
}

// https://itunes.apple.com/de/playlist/mafia-ii-empire-central-radio/pl.u-WBYGFvpeKLk
// https://tools.applemusic.com/embed/v1/playlist/pl.u-WBYGFvpeKLk

impl SpotifyUrl {
    pub fn new(url: &str) -> APIResult<SpotifyUrl> {
        lazy_static! {
            static ref SPOTIFY: Regex =
                Regex::new(r"https://open.spotify.com/(?:embed/)?user/(?P<user>[^/]*)/playlist/(?P<id>.*)").unwrap();
        }
        ensure!(SPOTIFY.is_match(url), ValidationError::NoValidSpoityUrl);

        let capture = SPOTIFY.captures(url).unwrap();
        Ok(SpotifyUrl {
            user: capture["user"].to_string(),
            id: capture["id"].to_string(),
        })
    }
}
