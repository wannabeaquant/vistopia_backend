import requests
import logging
import time

API_KEY = "AIzaSyCAcyu0-omgTK-rJ869Nkyrea3qiKFY55k"
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

logger = logging.getLogger(__name__)

EXCLUDED_KEYWORDS = ["flat", "pg"]

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Add new function for transport routes
def get_transport_routes(origin: str, destination: str, mode: str):
    DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": API_KEY,
        "alternatives": "true"
    }
    response = requests.get(DIRECTIONS_URL, params=params)
    data = response.json()
    if data["status"] != "OK":
        return []
    
    routes = []
    for route in data.get("routes", []):
        leg = route["legs"][0]
        distance_km = leg["distance"]["value"] / 1000
        duration = leg["duration"]["text"]
        
        # Estimate cost based on mode
        if mode == "driving":
            price = distance_km * 0.5  # $0.50 per km
        elif mode == "transit":
            price = 3.0  # Default fare
        else:
            price = 0.0  # Walking/bicycling
        routes.append({
            "transport_type": mode,
            "duration": duration,
            "distance": distance_km,
            "price": price
        })
    return routes

def geocode_location(location_str):
    params = {
        "address": location_str,
        "key": API_KEY
    }
    response = requests.get(GEOCODE_URL, params=params)
    data = response.json()
    if data.get("status") != "OK" or not data.get("results"):
        logger.error(f"Geocoding failed for location: {location_str}")
        return None, None
    location = data["results"][0]["geometry"]["location"]
    return (location["lat"], location["lng"])

def get_nearby_housing(lat, lng, keyword=None, radius=3000, max_results=60):
    """
    Fetches up to `max_results` places from Google Places API using pagination.
    """
    default_keywords = "hostel|pg|student housing"
    keyword = f"{default_keywords}|{keyword}" if keyword else default_keywords  

    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": keyword,
        "key": API_KEY
    }

    all_places = []
    while len(all_places) < max_results:
        response = requests.get(PLACES_URL, params=params)
        data = response.json()
        
        if "results" not in data:
            logger.error("No results found from Google Places API")
            break
        
        for place in data["results"]:
            name = place.get("name", "").lower()
            if any(excluded in name for excluded in EXCLUDED_KEYWORDS):
                continue  

            location = place.get("geometry", {}).get("location", {})
            all_places.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "lat": location.get("lat"),
                "lng": location.get("lng"),
                "rating": place.get("rating"),
                "total_reviews": place.get("user_ratings_total"),
                "price": place.get("price_level"),
                "amenities": place.get("types"),
                "place_id": place.get("place_id")
            })

        # Check if there's another page of results
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break  # No more pages

        params["pagetoken"] = next_page_token
        time.sleep(2)  # Google API requires a short delay before using next_page_token

    return all_places[:max_results]  # Limit results to max_results
