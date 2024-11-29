from flask import Blueprint, jsonify, request
import requests

weather_routes = Blueprint('weather_routes', __name__)

API_KEY = "03385cc121ba3bef13685ceacf062a00"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@weather_routes.route('/weather', methods=['GET'])
def get_weather():

    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    response = requests.get(
        BASE_URL,
        params={"q": city, "appid": API_KEY, "units": "metric"}
    )

    if response.status_code == 200:
        data = response.json()

        temperature = data["main"]["temp"]
        recommendation = ""

        if temperature > 30:
            recommendation = "It's hot outside. Consider indoor activities like yoga or gym workouts."
        elif 18 <= temperature <= 30:
            recommendation = "Great weather for outdoor activities like running or cycling."
        elif 10 <= temperature < 20:
            recommendation = "A bit chilly. Dress warmly if going outdoors for a walk or jog."
        else:
            recommendation = "It's cold outside. Prefer indoor workouts or a home exercise session."


        return jsonify({
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "weather": data["weather"][0]["description"],
            "recommendation": recommendation
        }), 200
    else:
        return jsonify({"error": response.json()}), response.status_code

