import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app)

amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
)


def parse_duration(iso_duration):
    """Convert PT2H30M to '2h 30m'."""
    duration = iso_duration.replace("PT", "")
    result = ""
    if "H" in duration:
        parts = duration.split("H")
        result += parts[0] + "h "
        duration = parts[1]
    if "M" in duration:
        result += duration.replace("M", "") + "m"
    return result.strip()


def format_offer(offer):
    itineraries = []
    for itinerary in offer["itineraries"]:
        segments = itinerary["segments"]
        first = segments[0]
        last = segments[-1]
        stops = len(segments) - 1
        itineraries.append(
            {
                "departure": first["departure"]["iataCode"],
                "arrival": last["arrival"]["iataCode"],
                "departureTime": first["departure"]["at"],
                "arrivalTime": last["arrival"]["at"],
                "duration": parse_duration(itinerary["duration"]),
                "stops": stops,
                "stopLabel": "Non-stop" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}",
                "carrier": first["carrierCode"],
                "flightNumber": f"{first['carrierCode']}{first['number']}",
            }
        )
    price = offer["price"]
    return {
        "id": offer["id"],
        "price": float(price["grandTotal"]),
        "currency": price["currency"],
        "itineraries": itineraries,
        "seats": offer.get("numberOfBookableSeats"),
    }


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/flights")
def search_flights():
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    departure_date = request.args.get("departureDate")
    return_date = request.args.get("returnDate")
    adults = int(request.args.get("adults", 1))
    children = int(request.args.get("children", 0))
    trip_type = request.args.get("tripType", "one-way")

    if not origin or not destination or not departure_date:
        return jsonify({"error": "origin, destination and departureDate are required"}), 400

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "max": 20,
        "currencyCode": "GBP",
    }
    if children > 0:
        params["children"] = children
    if trip_type == "round-trip" and return_date:
        params["returnDate"] = return_date

    try:
        response = amadeus.shopping.flight_offers_search.get(**params)
        offers = [format_offer(o) for o in response.data]
        offers.sort(key=lambda x: x["price"])
        return jsonify({"offers": offers, "count": len(offers)})
    except ResponseError as e:
        return jsonify({"error": str(e.response.body)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/airport-search")
def airport_search():
    keyword = request.args.get("keyword", "")
    if len(keyword) < 2:
        return jsonify({"results": []})
    try:
        response = amadeus.reference_data.locations.get(
            keyword=keyword,
            subType="AIRPORT,CITY",
            page={"limit": 8},
        )
        results = [
            {
                "iataCode": loc["iataCode"],
                "name": loc["name"],
                "cityName": loc.get("address", {}).get("cityName", ""),
                "countryName": loc.get("address", {}).get("countryName", ""),
            }
            for loc in response.data
        ]
        return jsonify({"results": results})
    except ResponseError:
        return jsonify({"results": []})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
