//! This Module is for all models
use error::*;
use regex::Regex;
use sha1::Sha1;
use std::path::PathBuf;

/// The playlist is a collection of tracks and urls where to find it
#[derive(Debug, Serialize, Deserialize)]
pub struct Playlist {
    /// Id of the playlist
    pub id: String,
    /// Title of the playlist
    pub title: String,
    /// Link to Spotify
    pub spotify: SpotifyUrl,
    /// Link to Apple music
    pub amusic: AmusicUrl,
    /// List of all tracks
    pub tracks: Vec<Track>,
    /// Playlist image
    pub image: PathBuf,
}

impl Playlist {
    /// Create a new Playlist instance
    pub fn new(
        title: &str,
        spotify: SpotifyUrl,
        amusic: AmusicUrl,
        tracks: Vec<Track>,
        image: PathBuf,
    ) -> APIResult<Playlist> {
        ensure!(!title.is_empty(), PlaylistError::EmptyTitle);
        ensure!(tracks.capacity() > 0, PlaylistError::EmptyTrack);
        Ok(Playlist {
            id: sha_short(&Sha1::from(title).digest().to_string()),
            title: title.to_string(),
            spotify: spotify,
            amusic: amusic,
            tracks: tracks,
            image: image,
        })
    }
}

/// Return the last 10 characters of a string.
pub fn sha_short(s: &str) -> String {
    s.char_indices()
        .rev()
        .nth(10)
        .map(|(i, _)| &s[i..])
        .unwrap()
        .to_string()
}

/// The SpotifyUrl is a representation of a link to a spotify playlist
#[derive(Debug, Serialize, Deserialize)]
pub struct SpotifyUrl {
    user: String,
    id: String,
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
    /// Return url to playlist.
    pub fn url(&self) -> String {
        format!(
            "https://open.spotify.com/user/{}/playlist/{}",
            self.user, self.id
        )
    }
    /// Return embed url to playlist.
    pub fn embed_url(&self) -> String {
        format!(
            "https://open.spotify.com/embed/user/{}/playlist/{}",
            self.user, self.id
        )
    }
}

/// The AmusicUrl is a representation of a link to an apple music playlist
#[derive(Debug, Serialize, Deserialize)]
pub struct AmusicUrl {
    link_name: String,
    id: String,
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
    /// Return url to playlist.
    pub fn url(&self) -> String {
        match self.link_name.len() {
            0 => format!("https://itunes.apple.com/de/playlist/{}", self.id),
            _ => format!(
                "https://itunes.apple.com/de/playlist/{}/{}",
                self.link_name, self.id
            ),
        }
    }
    /// Return embed url to playlist.
    pub fn embed_url(&self) -> String {
        format!("https://tools.applemusic.com/embed/v1/playlist/{}", self.id)
    }
}

/// The Track represents a track in a playlist
#[derive(Debug, Serialize, Deserialize)]
pub struct Track {
    title: String,
    interpret: String,
}

impl Track {
    /// Create a new Track element.
    pub fn new(title: &str, interpret: &str) -> APIResult<Track> {
        ensure!(
            !title.is_empty() && !interpret.is_empty(),
            PlaylistError::EmptyTrackValue
        );
        Ok(Track {
            title: title.to_string(),
            interpret: interpret.to_string(),
        })
    }
}

#[cfg(test)]
mod playlist_tests {
    use super::*;
    #[test]
    fn create_playlist() {
        let tracks = vec![Track::new("test title", "test interpret").unwrap()];
        let playlist = Playlist::new(
            "title",
            SpotifyUrl::new("https://open.spotify.com/user/marauderxtreme/playlist/6YZJnIXDOHyY0eu6PEFLUQ").unwrap(),
            AmusicUrl::new("https://itunes.apple.com/de/playlist/mafia-ii-empire-central-radio/pl.u-WBYGFvpeKLk").unwrap(),
            tracks,
            PathBuf::new()
        ).unwrap();
        assert_eq!(
            playlist.id,
            sha_short(&Sha1::from("title").digest().to_string())
        );
    }
}

#[cfg(test)]
mod spotify_tests {
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
    fn spotify_url_generation() {
        let playlist = SpotifyUrl::new(
            "https://open.spotify.com/user/marauderxtreme/playlist/6YZJnIXDOHyY0eu6PEFLUQ",
        ).unwrap();
        assert_eq!(
            playlist.url(),
            String::from(
                "https://open.spotify.com/user/marauderxtreme/playlist/6YZJnIXDOHyY0eu6PEFLUQ"
            )
        );
        assert_eq!(playlist.embed_url(), String::from("https://open.spotify.com/embed/user/marauderxtreme/playlist/6YZJnIXDOHyY0eu6PEFLUQ"));
    }
}

#[cfg(test)]
mod amusic_tests {
    use super::*;
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

        #[test]
    fn amusic_url_generation() {
        let playlist = AmusicUrl::new(
            "https://itunes.apple.com/de/playlist/mafia-ii-empire-central-radio/pl.u-WBYGFvpeKLk",
        ).unwrap();
        assert_eq!(
            playlist.url(),
            String::from(
                "https://itunes.apple.com/de/playlist/mafia-ii-empire-central-radio/pl.u-WBYGFvpeKLk"
            )
        );
        let playlist2 = AmusicUrl::new(
            "https://tools.applemusic.com/embed/v1/playlist/pl.u-WBYGFvpeKLk",
        ).unwrap();
        assert_eq!(
            playlist2.url(),
            String::from(
                "https://itunes.apple.com/de/playlist/pl.u-WBYGFvpeKLk"
            )
        );

        assert_eq!(playlist.embed_url(), String::from("https://tools.applemusic.com/embed/v1/playlist/pl.u-WBYGFvpeKLk"));
        assert_eq!(playlist2.embed_url(), String::from("https://tools.applemusic.com/embed/v1/playlist/pl.u-WBYGFvpeKLk"));
    }
}
