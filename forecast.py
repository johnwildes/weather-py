from flask import Blueprint, request, jsonify
import os
import requests
from datetime import datetime, timedelta

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('', methods=['GET'])
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
    weather_api_url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={zip_code}&days=3'
    history_api_url = f'http://api.weatherapi.com/v1/history.json?key={api_key}&q={zip_code}'

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
            history_response.raise_for_status()
            history_data.append(history_response.json())

        # Determine the client type based on the User-Agent header
        user_agent = request.headers.get('User-Agent', '').lower()
        is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])

        if not is_browser:
            # Return JSON response for CLI tools
            return jsonify({'forecast': forecast_data, 'history': history_data}), 200

        # Format the forecast data into an HTML table for browsers
        location = forecast_data.get('location', {}).get('name', 'Unknown location')
        forecast_days = forecast_data.get('forecast', {}).get('forecastday', [])
        if not forecast_days:
            # Return an error if no forecast data is available
            return jsonify({'error': 'No forecast data available'}), 500

        # Generate HTML table rows for each forecast day
        forecast_table_rows = ''.join(
            f"<tr>"
            f"<td><img src='{day['day']['condition']['icon']}' alt='icon'></td>"
            f"<td>{day['date']}</td>"
            f"<td>{day['day']['condition']['text']}</td>"
            f"<td>{day['day']['maxtemp_c']}°C / {day['day']['maxtemp_f']}°F</td>"
            f"<td>{day['day']['mintemp_c']}°C / {day['day']['mintemp_f']}°F</td>"
            f"</tr>"
            for day in forecast_days
        )

        # Generate HTML table rows for each history day
        history_table_rows = ''.join(
            f"<tr>"
            f"<td><img src='{day['forecast']['forecastday'][0]['day']['condition']['icon']}' alt='icon'></td>"
            f"<td>{day['forecast']['forecastday'][0]['date']}</td>"
            f"<td>{day['forecast']['forecastday'][0]['day']['condition']['text']}</td>"
            f"<td>{day['forecast']['forecastday'][0]['day']['maxtemp_c']}°C / {day['forecast']['forecastday'][0]['day']['maxtemp_f']}°F</td>"
            f"<td>{day['forecast']['forecastday'][0]['day']['mintemp_c']}°C / {day['forecast']['forecastday'][0]['day']['mintemp_f']}°F</td>"
            f"</tr>"
            for day in history_data
        )

        # Construct the full HTML response
        html_response = f"""
        <html>
            <head>
                <title>Weather Forecast</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="container my-4">
                <h1 class="text-center mb-4">Weather Forecast for {location}</h1>
                <h2>3-Day Forecast</h2>
                <div class="table-responsive">
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
                            {forecast_table_rows}
                        </tbody>
                    </table>
                </div>
                <h2>Previous 7 Days</h2>
                <div class="table-responsive">
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
                            {history_table_rows}
                        </tbody>
                    </table>
                </div>
            </body>
        </html>
        """
        return html_response, 200

    except requests.exceptions.RequestException as e:
        # Handle general request exceptions
        return jsonify({'error': str(e)}), 500
