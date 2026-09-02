"""
WeatherGPT Backend — SIH26068
Conversational AI for Weather Forecasting, Alerts, and Climate Information

Quick start:
    pip install flask flask-cors requests
    python app.py

This starter uses Open-Meteo (no API key needed) for live weather data,
and a simple rule-based responder you can swap for an LLM call
(OpenAI, Anthropic Claude API, or any open-weight model) in generate_reply().
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
import requests

app = Flask(__name__)
CORS(app)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail",
}


def geocode_place(place_name):
    """Resolve a place name to lat/lon using Open-Meteo's free geocoder."""
    resp = requests.get(GEOCODE_URL, params={"name": place_name, "count": 1}, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None
    top = results[0]
    return {
        "name": top["name"],
        "country": top.get("country", ""),
        "lat": top["latitude"],
        "lon": top["longitude"],
    }


def get_weather(lat, lon):
    """Fetch current + short forecast weather from Open-Meteo."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
        "timezone": "auto",
        "forecast_days": 5,
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def friendly_day(date_str):
    """Turn '2026-08-30' into 'Today', 'Tomorrow', or 'Sunday' etc."""
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = date.today()
    diff = (d - today).days
    if diff == 0:
        return "Today"
    if diff == 1:
        return "Tomorrow"
    return d.strftime("%A")


def generate_reply(place, weather_json, user_message):
    current = weather_json.get("current", {})
    daily = weather_json.get("daily", {})

    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    code = current.get("weather_code")
    condition = WEATHER_CODES.get(code, "unknown conditions")

    reply = (
        f"Right now in {place['name']}, it's {temp}°C with {condition}. "
        f"Humidity is {humidity}% and wind speed is {wind} km/h.\n\n"
    )

    if daily.get("time"):
        reply += "Next few days:\n"
        for i, date_str in enumerate(daily["time"][:5]):
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            rain_chance = daily["precipitation_probability_max"][i]
            day_code = daily["weather_code"][i]
            day_condition = WEATHER_CODES.get(day_code, "unknown")
            day_label = friendly_day(date_str)
            reply += f"  • {day_label}: {tmin}–{tmax}°C, {day_condition}, {rain_chance}% chance of rain\n"

    max_rain_chance = max(daily.get("precipitation_probability_max", [0]))
    if max_rain_chance and max_rain_chance >= 70:
        reply += "\n⚠️ Heavy rain likely in the coming days — consider planning around it."

    return reply


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    place_name = data.get("place", "").strip()

    if not place_name:
        return jsonify({"error": "Please specify a place name."}), 400

    try:
        place = geocode_place(place_name)
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            return jsonify({"error": "Weather service is busy right now (rate limited). Please wait a minute and try again."}), 503
        return jsonify({"error": "Could not look up that location right now. Please try again."}), 502
    except requests.exceptions.RequestException:
        return jsonify({"error": "Could not reach the location service. Please try again."}), 502

    if not place:
        return jsonify({"error": f"Could not find location '{place_name}'."}), 404

    try:
        weather_json = get_weather(place["lat"], place["lon"])
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            return jsonify({"error": "Weather service is busy right now (rate limited). Please wait a minute and try again."}), 503
        return jsonify({"error": "Could not fetch weather data right now. Please try again."}), 502
    except requests.exceptions.RequestException:
        return jsonify({"error": "Could not reach the weather service. Please try again."}), 502

    reply = generate_reply(place, weather_json, user_message)

    return jsonify({
        "place": place,
        "reply": reply,
        "raw_weather": weather_json,
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
