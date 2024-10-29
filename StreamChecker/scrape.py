import os
import httpx

from http import HTTPStatus
from itertools import zip_longest
from typing import Any, Iterable


def http_handler(status_code: int) -> None:
    """Handles various status codes for HTTP/HTTPS requests.

    Args:
        status_code (int): HTTP request status code.

    Raises:
        httpx.HTTPError: Client error
        httpx.HTTPError: Server error
        httpx.HTTPError: Other error
    """
    match status_code:
        case _ as status if status >= HTTPStatus.OK and status < HTTPStatus.BAD_REQUEST:
            return None
        case _ as status if status >= HTTPStatus.BAD_REQUEST and status < HTTPStatus.INTERNAL_SERVER_ERROR:
            raise httpx.HTTPError(f"CLIENT ERROR: {HTTPStatus(status)}")
        case _ as status if status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise httpx.HTTPError(f"SERVER ERROR: {HTTPStatus(status)}")
        case _ as status:
            raise httpx.HTTPError(f"OTHER ERROR: {HTTPStatus(status)}")


def grouper(iterable: Iterable[Any], n: int, fillvalue: Any = None):
    """Grouper recipe from itertools; returns a generator with n elements at a time.

    Args:
        iterable (Iterable[Any]): Generic iterable
        n (int): Number of elements to yield at a time.
        fillvalue (Any, optional): Padding value for incomplete final groups. Defaults to None.

    Returns:
        generator: Generator which yields n elements at a time
    """
    iterators = [iter(iterable)] * n
    return zip_longest(*iterators, fillvalue = fillvalue)
    

def movie_query(api_key: str, headers: dict) -> tuple:
    """Interactively queries movies from TMDB to find movie ID and title

    Args:
        headers (dict): Headers for TMDB requests, including API token

    Raises:
        httpx.HTTPError: HTTP client, server, or catch-all error
        IndexError: User requested invalid option from query results.
        ValueError: No matching movies found for query.

    Returns:
        tuple: Tuple of (movie_id, movie_title) from TMDB
    """
    choice = input("Query a movie: ")
    if not choice:
        exit()

    url = f"https://api.themoviedb.org/3/search/movie?query={choice.replace(' ', '+')}&api_key={api_key}"
    response = httpx.get(url, headers=headers)
    http_handler(response.status_code)

    movie_info = response.json().get("results", [])

    for movie_chunk in grouper(movie_info, 5):
        print(*[f"{n + 1}. {record['title']}" for n, record in enumerate(movie_chunk) if record], sep="\n")
        movie_idx = input("Are any of these the movie you're looking for? (#/n)\n\t>> ")

        match movie_idx:
            case movie_idx if movie_idx.isdecimal():
                try:
                    movie_data = movie_info[int(movie_idx) - 1]
                except IndexError as e:
                    raise IndexError("Requested index not valid.") from e
            case movie_idx if movie_idx in ["n", "N", "no", "No", "NO", None]:
                continue

        movie_id = movie_data.get("id")
        movie_title = movie_data.get("title")
        return movie_id, movie_title

    raise ValueError("No matching movies found.")


def streamer_fetch(
    movie_id: int,
    movie_title: str,
    tmdb_region: str,
    media_providers: list[str],
    headers: dict
) -> None:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"

    response = httpx.get(url, headers=headers)
    http_handler(response.status_code)
    watch_options = response.json().get("results", {}).get(tmdb_region, {})

    available_streamers = [provider for provider in watch_options.get("flatrate", []) if provider.get("provider_name") in media_providers]
    
    if available_streamers:
        print(f"Movie is available!  You can stream {movie_title} at:")
        print(*[f"{n + 1}. {record.get('provider_name')}" for n, record in enumerate(available_streamers)], sep="\n")
    else:
        print("Not available on your platforms.")


def fetch_title(movie_id: int, api_key: str, headers: dict) -> str:
    """Fetches movie title from TMDB movie ID.

    Args:
        api_key (str): TMDB API key.
        headers (dict): HTTP request headers.

    Returns:
        str: Movie title from TMDB.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = httpx.get(url, headers = headers)
    http_handler(response.status_code)
    return response.json().get("title")


def fetch_providers(region: str, headers: dict) -> list[str]:
    url = "https://api.themoviedb.org/3/watch/providers/movie?language=en-US"
    if region:
        url += f"&watch_region={region}"
    response = httpx.get(url, headers = headers)
    http_handler(response.status_code)
    return [provider["provider_name"] for provider in response.json().get("results", [])]


def main():
    api_key = os.getenv("TMDB_API_KEY")
    api_token = os.getenv("TDB_API_TOKEN")
    tmdb_region = os.getenv("TMDB_REGION", default="US")
    media_providers = os.getenv("TMDB_PROVIDERS", default="Netflix,Hulu,Peacock,Paramount Plus,Max").split(",")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    if not (movie_title := os.getenv("MOVIE_TITLE")):
        if not (movie_id := os.getenv("MOVIE_ID")):
            movie_id, movie_title = movie_query(api_key, headers)
        else:
            movie_title = fetch_title(movie_id, api_key, headers)
    
    streamer_fetch(movie_id, movie_title, tmdb_region, media_providers, headers)
