"""
Utility functions to process and display information about Roadsurfer Rally routes and stations.
Includes functions to print routes, destinations, and available dates.
"""
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


def print_routes_for_stations(stations: list):
    """
    Prints all available routes for a list of stations.

    Args:
    ----
        stations (list): List of stations with relevant information.

    """
    output_found_routes_title()
    for station in stations:
        print_station_destinations(station)


def print_station_destinations(station: dict):
    """
    Prints possible destinations and dates for an origin station.

    Args:
    ----
        station (dict): Dictionary with origin station data.

    """
    output_origin(station["name"])
    for return_station_id in station["returns"]:
        print_station_destination_with_route_url(station, return_station_id)
        available_dates = get_station_transfer_dates(station["id"], return_station_id)
        print_available_dates(available_dates)


def print_station_destination_with_route_url(station: dict, return_station_id: int):
    """
    Prints the destination and the route URL between two stations.

    Args:
    ----
        station (dict): Dictionary with origin station data.
        return_station_id (int): ID of the destination station.

    """
    output_destination_title()
    origin_encoded_address = quote(station["address"], safe=":/")
    destination_station = get_station_data(return_station_id)
    destination_encoded_address = quote(destination_station["address"], safe=":/")
    output_destination_with_route_url(destination_station["name"], origin_encoded_address, destination_encoded_address)


def print_available_dates(available_dates: list):
    """
    Prints the available dates for a route between two stations.

    Args:
    ----
        available_dates (list): List of dictionaries with start and end dates.

    """
    for date in available_dates:
        start_date = datetime.strptime(date["startDate"][:10], "%Y-%m-%d")
        end_date = datetime.strptime(date["endDate"][:10], "%Y-%m-%d")
        output_available_dates(start_date.strftime("%d/%m/%Y"), end_date.strftime("%d/%m/%Y"))
    print()


def get_stations_with_rally(stations: list):
    """
    Filters and gets the stations that allow rally (one_way).

    Args:
    ----
        stations (list): List of stations.

    Returns:
    -------
        list: List of stations with rally.

    """
    filtered_stations = [station for station in stations if station.get("one_way", False)]
    stations_with_rally = []
    for station in filtered_stations:
        station_data = get_station_data(station["id"])
        stations_with_rally.append(station_data)
    return stations_with_rally
