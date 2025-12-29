"""
Home blueprint for the landing page.

This module handles the home page route, using the WeatherService
abstraction for IP-based location detection and current weather.
"""

from flask import Blueprint, request, render_template

from services import WeatherAPIProvider

home_bp = Blueprint('home', __name__)

# Initialize the weather service
_weather_service = None


def get_weather_service():
    """Get or create the weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherAPIProvider()
    return _weather_service


@home_bp.route('', methods=['GET'])
def home():
    """
    Render the home page with user location and current weather.

    Uses IP-based geolocation to detect the user's location and
    display current weather conditions.
    """
    service = get_weather_service()

    # Get the user's IP address
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Get location and weather based on IP
    user_info = {}
    current_weather = None

    try:
        location_data = service.get_current_location_by_ip(user_ip)
        if location_data:
            user_info = location_data.get('user_info', {})
            current_weather = location_data.get('current_weather')
    except Exception:
        user_info = {"error": "Unable to fetch IP information"}

    # Disable weather map due to reliability issues
    weather_map_url = None

    return render_template(
        'home.html',
        user_info=user_info,
        weather_map_url=weather_map_url,
        current_weather=current_weather
    )
