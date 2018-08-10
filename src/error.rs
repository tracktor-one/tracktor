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
    /// The regex could not match to a spotify url.
    #[fail(display = "No matching apple music url")]
    NoValidAmusicUrl,
}
