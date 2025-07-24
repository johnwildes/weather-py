from flask import Blueprint, request, render_template
import os
import requests  # Add this import for making HTTP requests

home_bp = Blueprint('home', __name__)

@home_bp.route('', methods=['GET'])
def home():
    # Retrieve the API key for the weather service
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return "Weather API key is not configured", 500

    # Get user's location from request arguments or default to a specific location
    location = request.args.get('location', os.getenv('DEFAULT_ZIPCODE', 'auto:ip'))

    # Get the user's IP address
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Perform IP lookup using WeatherAPI's IP Lookup functionality
    ip_lookup_url = f"http://api.weatherapi.com/v1/ip.json?key={api_key}&q={user_ip}"
    user_info = {}
    try:
        response = requests.get(ip_lookup_url)
        if response.status_code == 200:
            user_info = response.json()
    except Exception as e:
        user_info = {"error": "Unable to fetch IP information"}

    # Get user's location for current weather
    location = user_info.get('city', 'London')  # Default to London if no city found
    
    # Disable weather map due to reliability issues with external map services
    weather_map_url = None
    
    # Get current weather for the user's location
    current_weather = None
    if location:
        try:
            weather_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=yes"
            weather_response = requests.get(weather_url)
            if weather_response.status_code == 200:
                current_weather = weather_response.json()
        except Exception as e:
            current_weather = None

    # Render the home page template with context data
    return render_template('home.html', 
                         user_info=user_info,
                         weather_map_url=weather_map_url,
                         current_weather=current_weather)
