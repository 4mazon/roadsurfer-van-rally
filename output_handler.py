from translations import translations
from api_utils import url_directions

iterators = dict()
iterator_character = "."
iterators_width = 32


def output_obtaining_station_list_title():
    print(translations['obtaining_station_list'])


def output_found_routes_title():
    print(f"\n{translations['found_routes']}")


def output_origin(origin: str):
    print(f"\n\n{translations['origin']}: {origin}")


def output_destination_title():
    print(f"\n{translations['destination']}: ", end="")


def output_destination_with_route_url(station_name: str, origin_encoded_address: str, destination_encoded_address: str):
    print(f"{station_name} - {translations['route']}: ", end="")
    print(f"{url_directions}/{origin_encoded_address}/{destination_encoded_address}")


def output_available_dates(start_date: str, end_date: str):
    print(f"[{start_date} - {end_date}]", end=" ")


def output_stations_iteration(iterator: str, number_of_stations: int):
    if iterator not in iterators:
        iterators[iterator] = 0
    iterators[iterator] += 1
    print(iterator_character, end="", flush=True)

    if iterators[iterator] % iterators_width != 0:
        return
    print("".ljust(5) + f"({iterators[iterator]} / {number_of_stations})")


def output_stations_iteration_end_decorator_when_appropriate(iterator: str, number_of_stations: int):
    if iterators[iterator] % iterators_width == 0:
        return

    print("".ljust(5 + iterators[iterator] % iterators_width) + f"({iterators[iterator]} / {number_of_stations})")