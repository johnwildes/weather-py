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
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from datetime import datetime  # Add this import

# Load environment variables from a .env file if it exists
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

@app.route('/forecast', methods=['GET'])
def get_forecast():
    # Retrieve the ZIP code from the request arguments
    zip_code = request.args.get('zip')
    if not zip_code:
        # If no ZIP code is provided, try to use the default ZIP code from environment variables
        zip_code = os.getenv('DEFAULT_ZIP_CODE')
        if not zip_code:
            # Return an error if neither a ZIP code nor a default is configured
            return jsonify({'error': 'ZIP code is required and no default is configured'}), 400

    # Retrieve the API key for the weather service from environment variables
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        # Return an error if the API key is not configured
        return jsonify({'error': 'Weather API key is not configured'}), 500

    # Construct the URL for the weather API request
    weather_api_url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={zip_code}&days=10'

    try:
        # Make the HTTP GET request to the weather API
        response = requests.get(weather_api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()  # Parse the JSON response

        # Determine the client type based on the User-Agent header
        user_agent = request.headers.get('User-Agent', '').lower()
        is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])

        if not is_browser:
            # Return JSON response for CLI tools
            return jsonify(data), 200

        # Format the forecast data into an HTML table for browsers
        location = data.get('location', {}).get('name', 'Unknown location')
        forecast_days = data.get('forecast', {}).get('forecastday', [])
        if not forecast_days:
            # Return an error if no forecast data is available
            return jsonify({'error': 'No forecast data available'}), 500

        # Generate HTML table rows for each forecast day
        table_rows = ''.join(
            f"<tr>"
            f"<td><img src='{day['day']['condition']['icon']}' alt='icon'></td>"
            f"<td>{day['date']}</td>"
            f"<td>{day['day']['condition']['text']}</td>"
            f"<td>{day['day']['maxtemp_c']}°C / {day['day']['maxtemp_f']}°F</td>"
            f"<td>{day['day']['mintemp_c']}°C / {day['day']['mintemp_f']}°F</td>"
            f"</tr>"
            for day in forecast_days
        )

        # Get the current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Construct the full HTML response
        html_response = f"""
        <html>
            <head>
                <title>Weather Forecast</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="container my-4">
                <h1 class="text-center mb-4">Weather Forecast for {location}</h1>
                <table class="table table-bordered table-striped">
                    <thead class="table-dark">
                        <tr>
                            <th>Icon</th>
                            <th>Date</th>
                            <th>Condition</th>
                            <th>High Temp (°C / °F)</th>
                            <th>Low Temp (°C / °F)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <footer class="text-center mt-4">
                    <p>Current Date and Time: {current_datetime}</p>
                </footer>
            </body>
        </html>
        """
        return html_response, 200

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., API key exhaustion or rate limiting)
        if response.status_code in [403, 429]:
            # Return a friendly HTML banner for these errors
            html_response = """
            <html>
                <head>
                    <title>Weather Unavailable</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body class="container my-4">
                    <div class="alert alert-warning text-center" role="alert">
                        Weather data is currently unavailable. Please try again later.
                    </div>
                </body>
            </html>
            """
            return html_response, 503
        else:
            # Return a JSON error for other HTTP errors
            return jsonify({'error': f'HTTP error occurred: {e}'}), response.status_code

    except requests.exceptions.RequestException as e:
        # Handle general request exceptions
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get the port from the environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    # Determine whether to run in debug mode based on the environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=debug_mode)