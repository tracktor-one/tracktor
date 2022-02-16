# Tracktor API

| A playlist information API written with FastAPI

## Why use an API?

[Christoph Kepler](https://github.com/MarauderXtreme) and [Felix Döring](https://github.com/h4llow3En) are cooperation in creating playlists. Both had the idea to include a description and the contents of those playlists on their websites.  
To reduce redundant information an API is the easiest way to get them.

## Usage

### Run with Docker

1. Clone this Repository
2. Run `docker-compose up --build`

### For development

1. Clone this Repository
2. Install GraphicsMagic (e.g. `apt-get install g++ libgraphicsmagick++1-dev libboost-python-dev`)
3. Create a venv or simply run `pip install -r requirements.txt`
4. Run `uvicorn tracktor:main --reload`

## API Endpoints and Models

FasAPI generates an openapi.json.  
To use a automatically build one have a look at the artifacts of the [OpenAPI generation Workflow](https://github.com/tracktor-one/tracktor/actions/workflows/openapi.yml)
