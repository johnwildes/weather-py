"""
Home blueprint for the landing page.

This module handles the home page route, using the WeatherService
abstraction for weather data retrieval and 10-day forecast display.
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
    Render the home page with search and 10-day forecast.

    If a location parameter is provided, displays weather data for that location.
    Otherwise shows the search interface.
    """
    service = get_weather_service()
    
    # Get location from query parameter
    location = request.args.get('location')
    
    weather_data = None
    
    if location:
        try:
            # Get 10-day forecast data
            weather_data = service.get_detailed_forecast(location, days=10)
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            weather_data = None

    return render_template(
        'home.html',
        weather_data=weather_data
    )
