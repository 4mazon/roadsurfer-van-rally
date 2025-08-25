from api_utils import get_stations_data
from data_utils import print_routes_for_stations,\
     get_stations_with_rally
from output_handler import output_obtaining_station_list_title


def main():
    output_obtaining_station_list_title()
    stations_json = get_stations_data()
    stations_with_rally = get_stations_with_rally(stations_json) 
    print_routes_for_stations(stations_with_rally)


if __name__ == "__main__":
    main()