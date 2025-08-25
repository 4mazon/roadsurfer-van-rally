"""
Main script to display available Roadsurfer Rally routes.

Gets the list of stations, filters those that allow rally, and shows the routes and dates.
"""
from api_utils import get_stations_data
from data_utils import get_stations_with_rally, print_routes_for_stations
from output_handler import output_obtaining_station_list_title


def main() -> None:
    """Run the main script to retrieve and display rally routes."""
    output_obtaining_station_list_title()
    stations_json = get_stations_data()
    stations_with_rally = get_stations_with_rally(stations_json)
    print_routes_for_stations(stations_with_rally)


if __name__ == "__main__":
    main()
