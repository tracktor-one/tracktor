//! An API to recieve playlist information
#![deny(
    missing_docs, trivial_casts, trivial_numeric_casts, unused_import_braces, unused_qualifications
)]
extern crate actix_web;
#[macro_use]
extern crate failure;
#[macro_use]
extern crate lazy_static;
extern crate regex;
extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_json;
extern crate sha1;

use actix_web::{http, server, App, Path, Responder};

pub mod error;
pub mod models;

fn index(info: Path<(u32, String)>) -> impl Responder {
    format!("Hello {}! id:{}", info.1, info.0)
}

fn main() {
    server::new(|| App::new().route("/{id}/{name}/index.html", http::Method::GET, index))
        .bind("127.0.0.1:8080")
        .unwrap()
        .run();
}
