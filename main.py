"""
Weather Forecast Application

This software provides a weather forecast service using the WeatherAPI. Users can retrieve a 10-day weather forecast by providing a ZIP code. The application supports both JSON responses for CLI tools and HTML responses for browsers.

Author: John Wildes
Contact: johnwildes@decklatedev.com

License: Apache License 2.0
Created with GitHub Copilot
"""

# Import necessary modules for Flask application, environment variable handling, and HTTP requests
import os
from flask import Flask
from dotenv import load_dotenv

# Import blueprints
from forecast import forecast_bp  # Import forecast blueprint
from home import home_bp  # Import home blueprint
from datetime import datetime, timedelta

# Load environment variables from a .env file if it exists
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Template filters for better date formatting
@app.template_filter('format_date')
def format_date_filter(date_string):
    """Format date string for display"""
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        today = datetime.now().date()
        date_date = date_obj.date()
        
        if date_date == today:
            return 'Today'
        elif date_date == today + timedelta(days=1):
            return 'Tomorrow'
        elif date_date == today - timedelta(days=1):
            return 'Yesterday'
        else:
            return date_obj.strftime('%a, %b %d')
    except:
        return date_string

# Register blueprints
app.register_blueprint(forecast_bp, url_prefix='/forecast')
app.register_blueprint(home_bp, url_prefix='/')

# Register API routes directly to the main app for cleaner URLs
from forecast import get_bulk_weather, validate_location, search_locations, get_detailed_forecast, get_hourly_forecast

app.add_url_rule('/api/weather/bulk', 'bulk_weather', get_bulk_weather, methods=['POST'])
app.add_url_rule('/api/validate-location', 'validate_location', validate_location, methods=['GET'])
app.add_url_rule('/api/search-locations', 'search_locations', search_locations, methods=['GET'])
app.add_url_rule('/api/detailed-forecast', 'detailed_forecast', get_detailed_forecast, methods=['GET'])
app.add_url_rule('/api/hourly-forecast', 'hourly_forecast', get_hourly_forecast, methods=['GET'])

if __name__ == '__main__':
    # Get the port from the environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    # Determine whether to run in debug mode based on the environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=debug_mode)