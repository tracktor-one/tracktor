//! This Module is for all models
use error::*;
use regex::Regex;
use std::path::Path;

/// The playlist is a collection of tracks and urls where to find it
#[derive(Debug)]
pub struct Playlist {
    id: i32,
    title: String,
    spotify: SpotifyUrl,
    amusic: AmusicUrl,
    tracks: Vec<Track>,
    image: Path,
}

/// The SpotifyUrl is a representation of a link to a spotify playlist
#[derive(Debug)]
pub struct SpotifyUrl {
    user: String,
    id: String,
}

/// The AmusicUrl is a representation of a link to an apple music playlist
#[derive(Debug)]
pub struct AmusicUrl {
    link_name: String,
    id: String,
}

/// The Track represents a track in a playlist
#[derive(Debug)]
pub struct Track {
    title: String,
    interpret: String,
}

impl Track {
    /// Create a new Track element.
    pub fn new(title: &str, interpret: &str) -> Track {
        Track {
            title: title.to_string(),
            interpret: interpret.to_string(),
        }
    }
}

impl SpotifyUrl {
    /// Create a new SpotifyUrl element.
    pub fn new(url: &str) -> APIResult<SpotifyUrl> {
        lazy_static! {
            static ref SPOTIFY: Regex = Regex::new(
                r"https://open\.spotify\.com/(?:embed/)?user/(?P<user>[^/]+)/playlist/(?P<id>.+)"
            ).unwrap();
        }
        ensure!(SPOTIFY.is_match(url), ValidationError::NoValidSpoityUrl);

        let capture = SPOTIFY.captures(url).unwrap();
        Ok(SpotifyUrl {
            user: capture["user"].to_string(),
            id: capture["id"].to_string(),
        })
    }
}

impl AmusicUrl {
    /// Create a new AmusicUrl element.
    pub fn new(url: &str) -> APIResult<AmusicUrl> {
        lazy_static! {
            static ref AMUSIC: Regex = Regex::new(
                r"https://(?:itunes\.apple|tools\.applemusic)\.com/(?:.{2}|embed/v1)/playlist/(?:(?P<name>[^/]*)/?)(?P<id>pl\.u-.+)"
            ).unwrap();
        }
        ensure!(AMUSIC.is_match(url), ValidationError::NoValidAmusicUrl);

        let capture = AMUSIC.captures(url).unwrap();
        Ok(AmusicUrl {
            link_name: capture["name"].to_string(),
            id: capture["id"].to_string(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn spotify_url() {
        let playlist = SpotifyUrl::new(
            "https://open.spotify.com/user/marauderxtreme/playlist/6YZJnIXDOHyY0eu6PEFLUQ",
        ).unwrap();
        assert_eq!(playlist.id, String::from("6YZJnIXDOHyY0eu6PEFLUQ"));
        assert_eq!(playlist.user, String::from("marauderxtreme"));
    }

    #[test]
    fn spotify_url_embedded() {
        let playlist = SpotifyUrl::new(
            "https://open.spotify.com/embed/user/marauderxtreme/playlist/6YZJnIXDOHyY0eu6PEFLUQ",
        ).unwrap();
        assert_eq!(playlist.id, String::from("6YZJnIXDOHyY0eu6PEFLUQ"));
        assert_eq!(playlist.user, String::from("marauderxtreme"));
    }

    #[test]
    #[should_panic]
    fn spotify_wrong_url() {
        let _ = SpotifyUrl::new("https://open.spotify.com/wrong/url/pattern").unwrap();
    }

    #[test]
    fn amusic_url() {
        let playlist = AmusicUrl::new(
            "https://itunes.apple.com/de/playlist/mafia-ii-empire-central-radio/pl.u-WBYGFvpeKLk",
        ).unwrap();
        assert_eq!(playlist.id, String::from("pl.u-WBYGFvpeKLk"));
        assert_eq!(
            playlist.link_name,
            String::from("mafia-ii-empire-central-radio")
        );
    }

    #[test]
    fn amusic_url_embedded() {
        let playlist = AmusicUrl::new(
            "https://tools.applemusic.com/embed/v1/playlist/pl.u-WBYGFvpeKLk",
        ).unwrap();
        assert_eq!(playlist.id, String::from("pl.u-WBYGFvpeKLk"));
        assert_eq!(playlist.link_name, String::from(""));
    }

    #[test]
    #[should_panic]
    fn amusic_wrong_url() {
        let _ = AmusicUrl::new("https://tools.applemusic.com/embed/v1/noplaylist/pl.u-WBYGFvpeKLk")
            .unwrap();
    }
}
