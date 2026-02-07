"""
Weather Web Server - Local Flask server for weather forecasts
Accepts city/state names and returns current weather forecast
Run: python weather_server.py
Visit: http://localhost:5000

Files referenced:
- weather_index.html: The HTML template for the main page where users can input a location and 
view the forecast.
- weather_debug.py: A debug script to test geocoding and NWS API calls, which can be used to 
verify that the APIs are working correctly. (NOT REFERENCED DIRECTLY IN THIS FILE)
"""



from flask import Flask, render_template, request, jsonify
import httpx
import asyncio
from typing import Any

app = Flask(__name__)

# Constants
NWS_API_BASE = "https://api.weather.gov"
NOMINATIM_API_BASE = "https://nominatim.openstreetmap.org"
USER_AGENT = "weather-app/1.0"


async def make_request(url: str, headers: dict = None) -> dict[str, Any] | None:
    """Make an async HTTP request with error handling."""
    if headers is None:
        headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0, follow_redirects=True)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None


async def geocode_location(location: str) -> tuple[float, float] | None:
    """Convert city/state name to coordinates using Nominatim."""
    url = f"{NOMINATIM_API_BASE}/search?q={location}&format=json&limit=1&countrycodes=us"
    headers = {"User-Agent": "WeatherApp/1.0 (weather-server)"}
    data = await make_request(url, headers)
    
    if data and len(data) > 0:
        result = data[0]
        return float(result["lat"]), float(result["lon"])
    
    return None


async def get_forecast_for_location(location: str) -> dict:
    """Get weather forecast for a city/state or state name."""
    # Try to geocode the location
    coords = await geocode_location(location)
    
    if not coords:
        return {
            "success": False,
            "error": f"Could not find location '{location}'. Please try a valid US city or state name."
        }
    
    latitude, longitude = coords
    
    try:
        # Get the forecast grid points
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await make_request(points_url)
        
        if not points_data:
            return {
                "success": False,
                "error": "This location is not in a US forecast area."
            }
        
        properties = points_data.get("properties", {})
        
        if "forecast" not in properties:
            return {
                "success": False,
                "error": "Forecast data not available for this location."
            }
        
        # Get the forecast
        forecast_url = properties["forecast"]
        forecast_data = await make_request(forecast_url)
        
        if not forecast_data:
            return {
                "success": False,
                "error": "Unable to fetch forecast data."
            }
        
        # Get alerts for the location
        points_props = points_data.get("properties", {})
        relative_location = points_props.get("relativeLocation", {}).get("properties", {})
        city = relative_location.get("city", "Unknown")
        state = relative_location.get("state", "Unknown")
        
        # Format forecast periods
        periods = forecast_data["properties"]["periods"]
        forecast_periods = []
        
        for period in periods[:5]:  # Next 5 periods
            forecast_periods.append({
                "name": period["name"],
                "temperature": f"{period['temperature']}°{period['temperatureUnit']}",
                "windSpeed": period["windSpeed"],
                "windDirection": period["windDirection"],
                "detailedForecast": period["detailedForecast"],
                "icon": period.get("icon", "")
            })
        
        return {
            "success": True,
            "location": f"{city}, {state}",
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "forecast": forecast_periods
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching forecast: {str(e)}"
        }


@app.route("/")
def index():
    """Serve the main weather page."""
    return render_template("weather_index.html")


@app.route("/api/forecast")
def get_forecast():
    """API endpoint to get forecast for a location."""
    location = request.args.get("location", "").strip()
    
    if not location:
        return jsonify({
            "success": False,
            "error": "Please provide a location (city or state name)"
        }), 400
    
    # Run async function in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(get_forecast_for_location(location))
    finally:
        loop.close()
    
    return jsonify(result)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("🌦️  Starting Weather Server on http://localhost:5000")
    print("Type a US city or state name to get the weather forecast")
    app.run(debug=True, host="localhost", port=5000)
