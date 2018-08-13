//! Custom Errors for handling request, matching urls, etc.
use failure;

/// Own Result type to make things a bit easier.
pub type APIResult<T> = Result<T, failure::Error>;

/// Validation of given spotify or apple music urls
#[derive(Debug, Fail)]
pub enum ValidationError {
    /// The regex could not match to a spotify url.
    #[fail(display = "No matching spotify url")]
    NoValidSpoityUrl,
    /// The regex could not match to a apple music url.
    #[fail(display = "No matching apple music url")]
    NoValidAmusicUrl,
}

/// Errors that could happen on playlist creation
#[derive(Debug, Fail)]
pub enum PlaylistError {
    /// This error is thrown if there is no track on playlist cration.
    #[fail(display = "There must be at least one track in a playlist")]
    EmptyTrack,
    /// This error is thrown if the fiels of a track are empty.
    #[fail(display = "There must be a title and an interpret.")]
    EmptyTrackValue,
    /// This error is thrown if the title of a playlist is empty
    #[fail(display = "Title must not be empty")]
    EmptyTitle,
}
