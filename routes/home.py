"""
Home blueprint for the landing page.

This module handles the home page route, using the WeatherService
abstraction for weather data retrieval and 10-day forecast display.
"""

import logging
from flask import Blueprint, request, render_template

from services import WeatherAPIProvider
from services.safety_features import enrich_weather_data
from services.astronomy_features import enrich_with_astronomy

home_bp = Blueprint('home', __name__)
logger = logging.getLogger(__name__)

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
    error_message = None
    
    if location:
        try:
            # Get 10-day forecast data
            weather_data = service.get_detailed_forecast(location, days=10)
            # Enrich with safety features
            weather_data = enrich_weather_data(weather_data)
            # Enrich with astronomy features
            weather_data = enrich_with_astronomy(weather_data)
        except Exception as e:
            logger.error(f"Error fetching weather data for location '{location}': {e}", exc_info=True)
            error_message = f"Unable to fetch weather data for '{location}'. Please try a different location."
            weather_data = None

    return render_template(
        'home.html',
        weather_data=weather_data,
        error_message=error_message
    )
