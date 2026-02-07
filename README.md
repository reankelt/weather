# Weather Forcast

Weather Web Server - Local Flask server for weather forecasts
Accepts city/state names and returns current weather forecast
Run: python weather_server.py
Visit: http://localhost:5000

This file implements a local Flask web server that provides weather forecasts for US cities 
and states. 
- It uses the National Weather Service (NWS) API to fetch forecast data and the Nominatim API for geocoding city/state names to coordinates. 

- The server has an API endpoint at /api/forecast that accepts a location query parameter and returns a JSON response with the forecast data. 

- The main page served at / allows users to input a location and view the forecast in a user-friendly format. 

- This file does not use MCP or FastAPI, but it can be tested using the test_mcp_client.py script by sending requests to the /api/forecast endpoint.

## Files referenced:
- weather_index.html: The HTML template for the main page where users can input a location and 
view the forecast.
- weather_debug.py: A debug script to test geocoding and NWS API calls, which can be used to verify that the APIs are working correctly. (NOT REFERENCED DIRECTLY weather.py)
