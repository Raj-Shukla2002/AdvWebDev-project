# Import necessary modules from Flask and requests library
from flask import Blueprint, jsonify, request  # Flask utilities for HTTP requests, responses, and route management
import requests  # For making HTTP requests to external APIs

# Create a Blueprint for weather-related routes
weather_routes = Blueprint('weather_routes', __name__)

# OpenWeatherMap API configuration
API_KEY = "03385cc121ba3bef13685ceacf062a00"  # API key to access the OpenWeatherMap API
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"  # Base URL for weather API

# Route to get weather information for a specific city
@weather_routes.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch the current weather data for a given city and provide a recommendation
    based on the temperature.
    """
    # Extract the 'city' parameter from the request's query string
    city = request.args.get('city')
    if not city:
        # Return an error if the city parameter is missing
        return jsonify({"error": "City parameter is required"}), 400

    # Make a GET request to the OpenWeatherMap API with the city name and API key
    response = requests.get(
        BASE_URL,
        params={"q": city, "appid": API_KEY, "units": "metric"}  # Units are set to metric (Celsius)
    )

    # If the API request is successful, process the response
    if response.status_code == 200:
        data = response.json()  # Parse the response JSON

        # Extract the temperature and generate a workout recommendation
        temperature = data["main"]["temp"]  # Current temperature in Celsius
        recommendation = ""

        # Generate recommendations based on temperature ranges
        if temperature > 30:
            recommendation = "It's hot outside. Consider indoor activities like yoga or gym workouts."
        elif 18 <= temperature <= 30:
            recommendation = "Great weather for outdoor activities like running or cycling."
        elif 10 <= temperature < 18:
            recommendation = "A bit chilly. Dress warmly if going outdoors for a walk or jog."
        else:
            recommendation = "It's cold outside. Prefer indoor workouts or a home exercise session."

        # Return the weather details and recommendation
        return jsonify({
            "city": data["name"],  # City name from the API response
            "temperature": data["main"]["temp"],  # Current temperature
            "weather": data["weather"][0]["description"],  # Weather description (e.g., "clear sky")
            "recommendation": recommendation  # Activity recommendation based on temperature
        }), 200
    else:
        # If the API request fails, return the error message and status code
        return jsonify({"error": response.json()}), response.status_code
