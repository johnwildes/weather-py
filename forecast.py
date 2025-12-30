"""
Forecast blueprint for weather data routes.

This module handles all forecast-related routes, using the WeatherService
abstraction for API calls.
"""

from flask import Blueprint, request, jsonify, redirect
import os

from services import WeatherAPIProvider

forecast_bp = Blueprint('forecast', __name__)

# Initialize the weather service
# In a larger app, this could be injected via dependency injection
_weather_service = None


def get_weather_service():
    """Get or create the weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherAPIProvider()
    return _weather_service


@forecast_bp.route('', methods=['GET'])
def get_forecast():
    """
    Get forecast page or JSON data.

    Returns HTML for browser clients, JSON for API clients.
    """
    zip_code = request.args.get('zip')
    service = get_weather_service()

    # Determine client type from User-Agent
    user_agent = request.headers.get('User-Agent', '').lower()
    is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])

    if is_browser:
        # Redirect to home page with location parameter
        if zip_code:
            return redirect(f'/?location={zip_code}')
        return redirect('/')

    # JSON response for non-browser clients
    if not zip_code:
        zip_code = os.getenv('DEFAULT_ZIP_CODE')
        if not zip_code:
            return jsonify({'error': 'ZIP code is required and no default is configured'}), 400

    weather_info = service.get_weather_data(zip_code)
    if weather_info:
        return jsonify({
            'forecast': weather_info['forecast'],
            'history': weather_info.get('history', [])
        }), 200
    else:
        return jsonify({'error': 'Unable to fetch weather data'}), 500


@forecast_bp.route('/api/weather/bulk', methods=['POST'])
def get_bulk_weather():
    """Get weather data for multiple locations."""
    try:
        data = request.get_json()
        if not data or 'locations' not in data:
            return jsonify({'error': 'No locations provided'}), 400

        locations = data['locations']
        service = get_weather_service()

        weather_results = service.get_bulk_weather(locations)
        return jsonify(weather_results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@forecast_bp.route('/api/validate-location', methods=['GET'])
def validate_location():
    """Validate if a location exists."""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'No location provided'}), 400

    service = get_weather_service()

    try:
        is_valid, location_info = service.validate_location(location)
        if is_valid:
            return jsonify({'valid': True, 'location': location_info}), 200
        return jsonify({'valid': False}), 200
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 200


@forecast_bp.route('/api/search-locations', methods=['GET'])
def search_locations():
    """Search for locations using autocomplete."""
    query = request.args.get('q')
    if not query or len(query) < 2:
        return jsonify([]), 200

    service = get_weather_service()

    try:
        results = service.search_locations(query, limit=10)
        return jsonify([r.to_dict() for r in results]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@forecast_bp.route('/api/detailed-forecast', methods=['GET'])
def get_detailed_forecast():
    """Get detailed forecast with astronomy and hourly data."""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'No location provided'}), 400

    service = get_weather_service()

    try:
        data = service.get_detailed_forecast(location, days=10)
        if data:
            return jsonify(data), 200
        return jsonify({'error': 'Unable to fetch detailed forecast'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@forecast_bp.route('/api/hourly-forecast', methods=['GET'])
def get_hourly_forecast():
    """Get hourly forecast for a specific location and date."""
    location = request.args.get('location')
    date = request.args.get('date')

    if not location or not date:
        return jsonify({'error': 'Location and date required'}), 400

    service = get_weather_service()

    try:
        data = service.get_hourly_forecast(location, date)
        if data:
            return jsonify(data), 200
        return jsonify({'error': 'Unable to fetch hourly forecast'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
