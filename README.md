
# Roadsurfer Van-Rally Routes Checker

This is a simple script to check all rally routes offered by **Roadsurfer**.

## Why?

Currently, the company offers no way to filter by return location. This script outputs every route with available dates, making it easier to find the ones that interest you.

## How to Use

1. Clone the repository:

    ```sh
    git clone https://github.com/4mazon/roadsurfer-van-rally.git
    cd roadsurfer-van-rally
    ```

2. Run the script:

    ```sh
    python main.py
    ```

    The routes will appear in the terminal.

3. (Optional) Save the output to a file:

    ```sh
    python main.py > routes.txt
    ```

Once you know the route you want, go to [Roadsurfer Rally Booking](https://booking.roadsurfer.com/en/rally/) and book your van!

## Notes

> **Warning**
> Use this responsibly. The script will make more requests to Roadsurfer servers than a normal user would. As per my tests, available dates and routes do not change very often.

This software will be available until I receive a request from **Roadsurfer** to remove it.

There are also standard rates at [Roadsurfer.com](https://roadsurfer.com) ;)
