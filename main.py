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

# Load environment variables from a .env file if it exists
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Register blueprints
app.register_blueprint(forecast_bp, url_prefix='/forecast')
app.register_blueprint(home_bp, url_prefix='/')

if __name__ == '__main__':
    # Get the port from the environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    # Determine whether to run in debug mode based on the environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=debug_mode)