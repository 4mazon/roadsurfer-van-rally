"""
Main script to display available Roadsurfer Rally routes.

Gets the list of stations, filters those that allow rally, and shows the routes and dates.
"""

import argparse

from api_utils import get_stations_data
from config_utils import get_config
from data_utils import get_stations_with_rally, print_routes_for_stations
from output_handler import output_obtaining_station_list_title, print_no_stations_with_rally_found
from translations import DEFAULT_LANGUAGE, load_translations


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
        argparse.Namespace: Parsed arguments.

    """
    parser = argparse.ArgumentParser(
        description="Display available Roadsurfer Rally routes.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default=DEFAULT_LANGUAGE,
        help=f"Language for output (e.g., 'en', 'es'). Default: {DEFAULT_LANGUAGE}",
    )
    return parser.parse_args()


def main() -> None:
    """Run the main script to retrieve and display rally routes."""
    # Parse command-line arguments
    args = parse_arguments()

    # Load translations for the selected language
    load_translations(args.language)

    # Set language for API calls
    get_config().set_language(args.language)

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
