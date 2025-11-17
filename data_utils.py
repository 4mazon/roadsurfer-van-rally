"""
Utility functions to process and display information about Roadsurfer Rally routes and stations.

Includes functions to print routes, destinations, and available dates.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import quote

from api_utils import get_station_data, get_station_transfer_dates
from output_handler import (
    output_available_dates,
    output_destination_title,
    output_destination_with_route_url,
    output_found_routes_title,
    output_origin,
)


def print_routes_for_stations(stations: list) -> None:
    """
    Print all available routes for a list of stations.

    Args:
    ----
        stations (list): List of stations with relevant information.

    """
    output_found_routes_title()
    for station in stations:
        print_station_destinations(station)


def print_station_destinations(station: dict) -> None:
    """
    Print possible destinations and dates for an origin station.

    Fetches transfer dates concurrently for multiple destinations.

    Args:
    ----
        station (dict): Dictionary with origin station data.

    """
    output_origin(station["name"])

    # Fetch all transfer dates concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_dest = {
            executor.submit(get_station_transfer_dates, station["id"], dest_id): dest_id
            for dest_id in station["returns"]
        }

        # Process results as they complete
        for future in as_completed(future_to_dest):
            return_station_id = future_to_dest[future]
            available_dates = future.result()

            print_station_destination_with_route_url(station, return_station_id)
            print_available_dates(available_dates)


def print_station_destination_with_route_url(station: dict, return_station_id: int) -> None:
    """
    Print the destination and the route URL between two stations.

    Args:
    ----
        station (dict): Dictionary with origin station data.
        return_station_id (int): ID of the destination station.

    """
    output_destination_title()
    origin_encoded_address = quote(station["address"], safe=":/")
    destination_station = get_station_data(return_station_id)
    destination_encoded_address = quote(destination_station["address"], safe=":/")
    output_destination_with_route_url(
        destination_station["name"], origin_encoded_address, destination_encoded_address
    )


def print_available_dates(available_dates: list) -> None:
    """
    Print the available dates for a route between two stations.

    Args:
    ----
        available_dates (list): List of dictionaries with start and end dates.

    """
    for date in available_dates:
        start_date = datetime.strptime(date["startDate"][:10], "%Y-%m-%d")
        end_date = datetime.strptime(date["endDate"][:10], "%Y-%m-%d")
        output_available_dates(start_date.strftime("%d/%m/%Y"), end_date.strftime("%d/%m/%Y"))
    print()


def get_stations_with_rally(stations: list) -> list:
    """
    Filter and get the stations that allow rally (one_way).

    Fetches station details concurrently for all rally-capable stations.

    Args:
    ----
        stations (list): List of stations.

    Returns:
    -------
        list: List of stations with rally, ordered by original list.

    """
    filtered_stations = [station for station in stations if station.get("one_way", False)]

    if not filtered_stations:
        return []

    # Fetch all station details concurrently
    stations_with_rally = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_station_id = {
            executor.submit(get_station_data, station["id"]): station["id"]
            for station in filtered_stations
        }

        for future in as_completed(future_to_station_id):
            station_id = future_to_station_id[future]
            station_data = future.result()
            if station_data:
                stations_with_rally[station_id] = station_data

    # Return results in original order
    return [stations_with_rally[s["id"]] for s in filtered_stations if s["id"] in stations_with_rally]
