from api_utils import get_station_data, get_station_transfer_dates
from datetime import datetime
from output_handler import output_found_routes_title,\
    output_origin,\
    output_destination_title,\
    output_destination_with_route_url,\
    output_available_dates,\
    output_stations_iteration,\
    output_stations_iteration_end_decorator_when_appropriate
from urllib.parse import quote

stations_data = {}
stations_with_returns = []


def print_routes_for_stations(stations: list):
    output_found_routes_title()
    for station in stations:
        print_station_destinations(station)


def print_station_destinations(station: list):
    output_origin(stations_data[station["id"]]["name"])
    for return_station_id in station["returns"]:
        print_station_destination_with_route_url(station, return_station_id)
        available_dates = get_station_transfer_dates(station["id"], return_station_id)
        print_available_dates(available_dates)


def print_station_destination_with_route_url(station: list, return_station_id: int):
    output_destination_title()
    origin_encoded_address = quote(station["address"], safe=':/')
    destination_encoded_address = quote(stations_data[return_station_id]["address"], safe=':/')
    output_destination_with_route_url(stations_data[return_station_id]["name"], origin_encoded_address, destination_encoded_address)


def print_available_dates(available_dates: list):
    for date in available_dates:
        start_date = datetime.strptime(date["startDate"][:10], "%Y-%m-%d")
        end_date = datetime.strptime(date["endDate"][:10], "%Y-%m-%d")
        output_available_dates(start_date.strftime("%d/%m/%Y"), end_date.strftime("%d/%m/%Y"))
    print()


def get_stations_with_returns(stations: list):
    for station in stations:
        output_stations_iteration("stations", len(stations))

        stations_data[station["id"]] = station
        station_data = get_station_data(station["id"])

        if not station_data.get("returns"):
            continue
        stations_with_returns.append(station_data)

    output_stations_iteration_end_decorator_when_appropriate("stations", len(stations))
    return stations_with_returns