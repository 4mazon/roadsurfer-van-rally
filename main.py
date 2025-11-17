"""
Main script to display available Roadsurfer Rally routes.

Gets the list of stations, filters those that allow rally, and shows the routes and dates.
"""

from api_utils import get_stations_data
from data_utils import get_stations_with_rally, print_routes_for_stations
from output_handler import output_obtaining_station_list_title, print_no_stations_with_rally_found


def main() -> None:
    """Run the main script to retrieve and display rally routes."""
    output_obtaining_station_list_title()
    stations_json = get_stations_data()

    if stations_json is None:
        print_no_stations_with_rally_found()
        return

    stations_with_rally = get_stations_with_rally(stations_json)

    if len(stations_with_rally) == 0:
        print_no_stations_with_rally_found()
        return

    print_routes_for_stations(stations_with_rally)


if __name__ == "__main__":
    main()
