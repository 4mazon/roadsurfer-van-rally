from json import loads
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

url_stations = "https://booking.roadsurfer.com/api/es/rally/stations"
url_timeframes = "https://booking.roadsurfer.com/api/es/rally/timeframes"
url_directions = "https://www.google.com/maps/dir"

base_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "https://booking.roadsurfer.com/es/rally?currency=EUR",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-Alias": "rally.startStations"
}


def get_json_from_url(url: str, headers: dict):
    req = Request(url, headers=headers)

    try:
        with urlopen(req) as response:
            data = loads(response.read().decode())
            return data
    except HTTPError as e:
        print("HTTP Error:", e.code)
    except URLError as e:
        print("URL Error:", e.reason)


def get_station_data(station_id: int):
    headers = base_headers
    if station_id is not None:
        url = f"{url_stations}/{station_id}"
        headers.update({"X-Requested-Alias": "rally.fetchRoutes"})
    else:
        url = url_stations
        headers.update({"X-Requested-Alias": "rally.startStations"})

    return get_json_from_url(url, headers)


def get_stations_data():
    return get_station_data(None)


def get_station_transfer_dates(origin_station_id: int, destination_station_id: int):
    url = f"{url_timeframes}/{origin_station_id}-{destination_station_id}"
    headers = {**base_headers, **{"X-Requested-Alias": "rally.timeframes"}}
    return get_json_from_url(url, headers)