import os
import logging
import requests
import random
from google.auth import default as google_default_auth
from google.auth.transport.requests import Request as GoogleRequest
from functools import reduce
from flask import Flask, request
from firebase_admin import initialize_app
from firebase_functions import https_fn


initialize_app()
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Google Auth
creds, project = google_default_auth()
auth_req = GoogleRequest()

# Environment Variables
GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

# Constants
DEFAULT_PAGE_SIZE = 3
DEFAULT_NUM_RESULTS = 6
DEFAULT_ACTIVITY = "tourist attractions"


def get_request_params(param, default=None):
    request_json = request.get_json(silent=True)
    request_args = request.args

    return (request_json or {}).get(param, default) or request_args.get(param, default)


def get_places(city, activity, page_size=DEFAULT_PAGE_SIZE):
    text_query = f"{activity} in {city}"
    try:
        places_resp = requests.get(
            f"https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={
                "query": text_query,
                "key": GOOGLE_PLACES_API_KEY,
            },
        )
        places_resp.raise_for_status()

    except requests.RequestException as e:
        logging.error(f"Error fetching places: {e}")
        return []

    places = places_resp.json().get("results", [])
    places_info = [
        {
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "place_id": place.get("place_id"),
        }
        for place in places
    ][:page_size]

    logging.info(
        f"Get places -- {text_query}, returning array of {len(places)}: {places_info}"
    )

    return places_info


@app.route("/tourist_attractions", methods=["GET", "POST"])
def tourist_attractions():
    city = get_request_params("city")

    return {"results": get_places(city, DEFAULT_ACTIVITY)}


@app.route("/places_search", methods=["GET", "POST"])
def places_search():
    city = get_request_params("city")
    activity = get_request_params("activity", DEFAULT_ACTIVITY)

    return {"results": get_places(city, activity)}


@app.route("/hotel_search", methods=["GET", "POST"])
def hotel_search():
    city = get_request_params("city")
    num_results = get_request_params("num_results", DEFAULT_NUM_RESULTS)

    return {"results": get_places(city, "hotels", page_size=num_results)}


@app.route("/places_search_tool", methods=["GET", "POST"])
def places_search_tool():
    """Args:
        city: name of the city
        place: name of the place (e.g. Hilton hotel)
        preferences: comma separated list of user preference
        pageSize: number of places to return

    Returns:
        Results with a list of activities
    """

    city = get_request_params("city")
    place = get_request_params("place")
    city_query = f"{place} {city}" if place and city else city

    activities_str = get_request_params("preferences", DEFAULT_ACTIVITY)
    activities = activities_str.split(",")

    page_size = get_request_params("page_size", DEFAULT_PAGE_SIZE)
    activity_page_size = round(page_size / len(activities)) + 1

    outputs = [
        get_places(city_query, activity, activity_page_size) for activity in activities
    ]
    output = reduce(lambda a, b: a + b, outputs)
    random.shuffle(output)
    return {"results": output[:page_size]}


@https_fn.on_request()
def main(req: https_fn.Request) -> https_fn.Response:
    creds.refresh(auth_req)
    with app.request_context(req.environ):
        return app.full_dispatch_request()