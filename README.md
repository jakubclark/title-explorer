# Title Explorer

Search for movies and TV Shows

# Endpoints

* `GET /api/search?title={title}`
    * Search by a Title
    * Returns a list of results

* `GET /api/search?id={id}`
    * Search for a specific Movie or TV Show, using a IMDb ID
    * Returns information on the specific Movie or TV Show

# Goals

* [x] Get acquainted with `asyncio` in Python
* [ ] Store data in a graph database

# Running Locally

Prerequisites:
* Install the dependencies with `pipenv install --dev`

1. Start the `neo4j` Docker Container
    * `docker run --name neo4j-container -v $PWD/neo4j/data:/data -v $PWD/neo4j/logs:/logs --env NEO4J_AUTH="neo4j/pass" -p 7474:7474 -p 7687:7687 neo4j:3.5.3`
2. Start the application
    * `pipenv run python -m title_explorer`
