"""Debug script to test geocoding and NWS API calls."""

import httpx
import asyncio
from typing import Any

NOMINATIM_API_BASE = "https://nominatim.openstreetmap.org"
NWS_API_BASE = "https://api.weather.gov"


async def make_request(url: str, headers: dict = None) -> dict[str, Any] | None:
    """Make an async HTTP request with error handling."""
    async with httpx.AsyncClient() as client:
        try:
            print(f"Fetching: {url}")
            response = await client.get(url, headers=headers, timeout=30.0, follow_redirects=True)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_location(location: str):
    """Test geocoding and forecast for a location."""
    print(f"\n{'='*60}")
    print(f"Testing: {location}")
    print(f"{'='*60}\n")
    
    # Test geocoding
    print(f"1. Geocoding '{location}'...")
    url = f"{NOMINATIM_API_BASE}/search?q={location}&format=json&limit=1&countrycodes=us"
    headers = {"User-Agent": "WeatherApp/1.0 (weather-debug)"}
    geocode_data = await make_request(url, headers)
    
    if not geocode_data or len(geocode_data) == 0:
        print("❌ Geocoding failed - no results found")
        return
    
    result = geocode_data[0]
    latitude = float(result["lat"])
    longitude = float(result["lon"])
    print(f"[OK] Found: {result.get('display_name', 'Unknown')}")
    print(f"   Coordinates: {latitude}, {longitude}\n")
    
    # Test NWS points
    print(f"2. Fetching NWS points data...")
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_request(points_url)
    
    if not points_data:
        print("[FAIL] NWS points request failed")
        return
    
    print(f"[OK] Points data received")
    properties = points_data.get("properties", {})
    
    if "forecast" not in properties:
        print(f"[FAIL] No 'forecast' property in response")
        print(f"   Available properties: {list(properties.keys())}")
        return
    
    forecast_url = properties["forecast"]
    print(f"   Forecast URL: {forecast_url}\n")
    
    # Test forecast
    print(f"3. Fetching forecast data...")
    forecast_data = await make_request(forecast_url)
    
    if not forecast_data:
        print("[FAIL] Forecast request failed")
        return
    
    print(f"[OK] Forecast data received")
    periods = forecast_data.get("properties", {}).get("periods", [])
    print(f"   Number of periods: {len(periods)}")
    
    if periods:
        print(f"\n   First 2 periods:")
        for period in periods[:2]:
            print(f"   - {period['name']}: {period['temperature']}°{period['temperatureUnit']}, {period['detailedForecast'][:60]}...")


async def main():
    locations = ["New York", "San Francisco", "Los Angeles", "Texas"]
    
    for loc in locations:
        await test_location(loc)


if __name__ == "__main__":
    asyncio.run(main())
