"""
Functions to display messages and results in the console for the user.

Includes titles, routes, dates, and visual decorators.
"""

from api_utils import get_url_directions
from translations import translations

iterators = {}
iterator_character = "."
iterators_width = 32


def output_obtaining_station_list_title() -> None:
    """Display the title for obtaining the station list."""
    print(translations["obtaining_station_list"])


def output_found_routes_title() -> None:
    """Display the title for found routes."""
    print(f"\n{translations['found_routes']}")


def output_origin(origin: str) -> None:
    """Display the name of the origin station."""
    print(f"\n\n{translations['origin']}: {origin}")


def output_destination_title() -> None:
    """Display the destination title."""
    print(f"\n{translations['destination']}: ", end="")


def output_destination_with_route_url(
    station_name: str, origin_encoded_address: str, destination_encoded_address: str
) -> None:
    """Display the destination and the Google Maps route URL."""
    print(f"{station_name} - {translations['route']}: ", end="")
    url_directions = get_url_directions()
    print(f"{url_directions}/{origin_encoded_address}/{destination_encoded_address}")


def output_available_dates(start_date: str, end_date: str) -> None:
    """Display a range of available dates for a route."""
    print(f"[{start_date} - {end_date}]", end=" ")


def print_no_stations_with_rally_found() -> None:
    """Print a message indicating that no stations with rally were found."""
    print(translations["no_stations_with_rally_found"])
