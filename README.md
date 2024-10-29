# StreamChecker

Scrapes TMDB to find streaming options for movies and TV shows.

To use this project, you can either `pip install` the repository or use the provided Dockerfile to create a Docker container that runs the application.

## Environmental Variables

This utility depends on TMDB (and, in turn, JustWatch for streaming information).  An API key is required, and multiple environmental variables are used to authenticate to TMDB and narrow searches appropriately.

Set environmental variables as follows:

```bash
export TMDB_API_KEY="YOUR_API_KEY"
export TMDB_API_TOKEN="YOUR_BEARER_TOKEN"
export TMDB_REGION="YOUR_TMDB_REGION"
export YOUR_TMDB_PROVIDERS="YOUR_STREAMING_PROVIDERS"
```

Your TMDB API key and bearer token can be found on the [TMDB website](https://www.themoviedb.org/settings/api?language=en-US) once logged in.

The `TMDB_REGION` variable defaults to "US", and does not need to be set.

The `TMDB_PROVIDERS` variable defaults to "Netflix,Hulu,Peacock,Paramount Plus,Max", and does not need to be set.  If set, it should be a list of comma-separated provider names.

## CLI Tool

You can install this project like any other Python package:

```python
pip install .
```

This will install a CLI tool called `streamCheck`, which you can use as follows:

```bash
streamCheck
```

This will allow you to interactively search for a movie's current streaming platforms, assuming you've provided the correct credentials.

## Docker

Build the Dockerfile into a container:

```bash
git clone https://github.com/ezfman/StreamChecker.git
docker build -t sc:latest .
```

Then run the container:

```bash
docker run -it sc:latest
```
