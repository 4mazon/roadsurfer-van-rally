"""
Module to interact with the Roadsurfer Rally API.

Includes functions to obtain station data, transfer dates, and network utilities.
"""

from json import loads
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cache_utils import get_cached, set_cache

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
    "X-Requested-Alias": "rally.startStations",
}


def get_json_from_url(url: str, headers: dict, use_cache: bool = False) -> dict | None:
    """
    Get a JSON response from a URL using a GET request.

    Args:
    ----
        url (str): URL to send the request to.
        headers (dict): HTTP headers to include in the request.
        use_cache (bool): Whether to use cache for this request. Defaults to False.

    Returns:
    -------
        dict: Decoded JSON response, or None if there is an error.

    """
    # Check cache first if enabled
    if use_cache and (cached_data := get_cached(url)):
        return cached_data

    req = Request(url, headers=headers)
    try:
        with urlopen(req) as response:
            data = loads(response.read().decode())
            # Store in cache if enabled
            if use_cache:
                set_cache(url, data)
            return data
    except HTTPError as e:
        print("HTTP Error:", e.code)
    except URLError as e:
        print("URL Error:", e.reason)


def get_station_data(station_id: int) -> dict | None:
    """
    Get the data for a specific station or all stations if station_id is None.

    Args:
    ----
        station_id (int): Station ID or None for all stations.

    Returns:
    -------
        dict: Data for the station or stations.

    """
    headers = base_headers
    if station_id is not None:
        url = f"{url_stations}/{station_id}"
        headers.update({"X-Requested-Alias": "rally.fetchRoutes"})
        # Cache individual station details (non-critical data)
        return get_json_from_url(url, headers, use_cache=True)
    else:
        url = url_stations
        headers.update({"X-Requested-Alias": "rally.startStations"})
        # Do NOT cache the initial station list (critical for rally identification)
        return get_json_from_url(url, headers, use_cache=False)


def get_stations_data() -> dict | None:
    """
    Get the list of all available stations.

    Returns
    -------
        dict: Data for all stations.

    """
    return get_station_data(None)


def get_station_transfer_dates(origin_station_id: int, destination_station_id: int) -> dict | None:
    """
    Get the available transfer dates between two stations.

    Args:
    ----
        origin_station_id (int): Origin station ID.
        destination_station_id (int): Destination station ID.

    Returns:
    -------
        dict: Available transfer dates.

    """
    url = f"{url_timeframes}/{origin_station_id}-{destination_station_id}"
    headers = {**base_headers, "X-Requested-Alias": "rally.timeframes"}
    # Cache transfer dates (non-critical data)
    return get_json_from_url(url, headers, use_cache=True)
