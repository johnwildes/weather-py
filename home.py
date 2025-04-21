from flask import Blueprint, request, render_template_string
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

    # Construct the weather map URL
    weather_map_url = f"https://maps.weatherapi.com/v1/map.png?key={api_key}&q={location}&zoom=6"

    # Render the home page with the weather map and user information
    html_response = f"""
    <html>
        <head>
            <title>Weather Map</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="container my-4">
            <h1 class="text-center mb-4">Weather Map</h1>
            <div class="text-center">
                <img src="{weather_map_url}" alt="Weather Map" class="img-fluid">
            </div>
            <div class="mt-4">
                <h2>User Information</h2>
                <table class="table table-bordered">
                    <tr><th>IP Address</th><td>{user_info.get('ip', 'N/A')}</td></tr>
                    <tr><th>City</th><td>{user_info.get('city', 'N/A')}</td></tr>
                    <tr><th>Region</th><td>{user_info.get('region', 'N/A')}</td></tr>
                    <tr><th>Country</th><td>{user_info.get('country', 'N/A')}</td></tr>
                    <tr><th>Location</th><td>{user_info.get('loc', 'N/A')}</td></tr>
                    <tr><th>Organization</th><td>{user_info.get('org', 'N/A')}</td></tr>
                </table>
            </div>
            <footer class="text-center mt-4">
                <a href="/forecast" class="btn btn-primary">View 10-Day Forecast</a>
            </footer>
        </body>
    </html>
    """
    return html_response, 200
