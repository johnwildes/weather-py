from flask import Blueprint, request, jsonify, render_template
import os
import requests
from datetime import datetime, timedelta
import json

forecast_bp = Blueprint('forecast', __name__)

def get_weather_data(location):
    """Helper function to get weather data for a single location"""
    # Retrieve the API key for the weather service from environment variables
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return None

    # Construct the URL for the weather API request with alerts
    weather_api_url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=3&aqi=yes&alerts=yes'
    history_api_url = f'http://api.weatherapi.com/v1/history.json?key={api_key}&q={location}'

    try:
        # Make the HTTP GET request to the weather API for forecast
        response = requests.get(weather_api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        forecast_data = response.json()  # Parse the JSON response

        # Make the HTTP GET requests for the previous 7 days of history
        history_data = []
        for i in range(1, 8):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            history_response = requests.get(f"{history_api_url}&dt={date}")
            if history_response.status_code == 200:
                history_data.append(history_response.json())

        return {
            'location': forecast_data.get('location', {}),
            'current': forecast_data.get('current', {}),
            'forecast': forecast_data.get('forecast', {}),
            'alerts': forecast_data.get('alerts', {}),
            'history': history_data
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data for {location}: {str(e)}")
        return None

@forecast_bp.route('', methods=['GET'])
def get_forecast():
    # Retrieve the ZIP code from the request arguments
    zip_code = request.args.get('zip')
    
    # Determine the client type based on the User-Agent header
    user_agent = request.headers.get('User-Agent', '').lower()
    is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])
    
    if is_browser:
        # For browsers, render the forecast template
        weather_data = []
        
        if zip_code:
            # Get weather data for the specified ZIP code
            weather_info = get_weather_data(zip_code)
            if weather_info:
                weather_data.append(weather_info)
        
        return render_template('forecast.html', weather_data=weather_data)
    
    # For non-browser clients, continue with original JSON logic
    if not zip_code:
        # If no ZIP code is provided, try to use the default ZIP code from environment variables
        zip_code = os.getenv('DEFAULT_ZIP_CODE')
        if not zip_code:
            # Return an error if neither a ZIP code nor a default is configured
            return jsonify({'error': 'ZIP code is required and no default is configured'}), 400

    # Get weather data and return JSON
    weather_info = get_weather_data(zip_code)
    if weather_info:
        return jsonify({'forecast': weather_info['forecast'], 'history': weather_info.get('history', [])}), 200
    else:
        return jsonify({'error': 'Unable to fetch weather data'}), 500

# New API endpoints for multi-location support

@forecast_bp.route('/api/weather/bulk', methods=['POST'])
def get_bulk_weather():
    """Get weather data for multiple locations"""
    try:
        data = request.get_json()
        if not data or 'locations' not in data:
            return jsonify({'error': 'No locations provided'}), 400
        
        locations = data['locations']
        temp_unit = data.get('tempUnit', 'celsius')
        
        weather_results = []
        for location in locations:
            weather_data = get_weather_data(location)
            if weather_data:
                weather_results.append(weather_data)
        
        return jsonify(weather_results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forecast_bp.route('/api/validate-location', methods=['GET'])
def validate_location():
    """Validate if a location exists"""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'No location provided'}), 400
    
    # Use a simple forecast request to validate the location
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 500
    
    try:
        # Use current weather endpoint for faster validation
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}'
        response = requests.get(url)
        
        if response.status_code == 200:
            return jsonify({'valid': True, 'location': response.json().get('location', {})}), 200
        else:
            return jsonify({'valid': False}), 200
            
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 200

@forecast_bp.route('/api/search-locations', methods=['GET'])
def search_locations():
    """Search for locations using WeatherAPI search"""
    query = request.args.get('q')
    if not query or len(query) < 2:
        return jsonify([]), 200
    
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 500
    
    try:
        # Use WeatherAPI search endpoint
        url = f'http://api.weatherapi.com/v1/search.json?key={api_key}&q={query}'
        response = requests.get(url)
        
        if response.status_code == 200:
            results = response.json()
            # Format results for frontend consumption
            formatted_results = []
            for result in results[:10]:  # Limit to 10 results
                formatted_results.append({
                    'name': result.get('name', ''),
                    'region': result.get('region', ''),
                    'country': result.get('country', ''),
                    'display': f"{result.get('name', '')}, {result.get('region', '')}, {result.get('country', '')}",
                    'value': result.get('name', '')
                })
            return jsonify(formatted_results), 200
        else:
            return jsonify([]), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forecast_bp.route('/api/detailed-forecast', methods=['GET'])
def get_detailed_forecast():
    """Get detailed forecast for a specific location"""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'No location provided'}), 400
    
    # Get extended weather data (up to 10 days if available)
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 500
    
    try:
        # Get 10-day forecast with air quality and alerts
        url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=10&aqi=yes&alerts=yes'
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Enhanced data with additional details
        detailed_data = {
            'location': data.get('location', {}),
            'current': data.get('current', {}),
            'forecast': data.get('forecast', {}),
            'alerts': data.get('alerts', {}),
            'astronomy': [],
            'hourly': []
        }
        
        # Get astronomy data and hourly forecasts for each forecast day
        for day in data.get('forecast', {}).get('forecastday', []):
            detailed_data['astronomy'].append({
                'date': day.get('date'),
                'astro': day.get('astro', {}),
                'moon_phase': day.get('astro', {}).get('moon_phase', ''),
                'moon_illumination': day.get('astro', {}).get('moon_illumination', '')
            })
            
            # Add hourly data for the first 3 days
            if len(detailed_data['hourly']) < 3:
                detailed_data['hourly'].append({
                    'date': day.get('date'),
                    'hours': day.get('hour', [])
                })
        
        return jsonify(detailed_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New endpoint for hourly forecast data
@forecast_bp.route('/api/hourly-forecast', methods=['GET'])
def get_hourly_forecast():
    """Get hourly forecast for a specific location and date"""
    location = request.args.get('location')
    date = request.args.get('date')
    
    if not location or not date:
        return jsonify({'error': 'Location and date required'}), 400
    
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 500
    
    try:
        # Check if date is in the future (forecast) or past (history)
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        if target_date > today:
            # Use forecast endpoint
            url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&dt={date}'
        else:
            # Use history endpoint
            url = f'http://api.weatherapi.com/v1/history.json?key={api_key}&q={location}&dt={date}'
            
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract hourly data
        if 'forecast' in data:
            forecast_day = data['forecast']['forecastday'][0] if data['forecast']['forecastday'] else {}
        else:
            forecast_day = data.get('forecast', {}).get('forecastday', [{}])[0] if data.get('forecast') else {}
            
        hourly_data = {
            'location': data.get('location', {}),
            'date': date,
            'hourly': forecast_day.get('hour', []),
            'day_summary': forecast_day.get('day', {}),
            'astronomy': forecast_day.get('astro', {})
        }
        
        return jsonify(hourly_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
