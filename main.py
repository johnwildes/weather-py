import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

app = Flask(__name__)

@app.route('/forecast', methods=['GET'])
def get_forecast():
    zip_code = request.args.get('zip')
    if not zip_code:
        # Retrieve the default ZIP code from the environment variable
        zip_code = os.getenv('DEFAULT_ZIP_CODE')
        if not zip_code:
            return jsonify({'error': 'ZIP code is required and no default is configured'}), 400

    # Retrieve the API key from the environment variable or .env file
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return jsonify({'error': 'Weather API key is not configured'}), 500

    weather_api_url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={zip_code}&days=10'

    try:
        response = requests.get(weather_api_url)
        response.raise_for_status()
        data = response.json()

        # Check the User-Agent header to determine the client type
        user_agent = request.headers.get('User-Agent', '').lower()
        is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])

        if not is_browser:
            # Return JSON response for CLI tools
            return jsonify(data), 200

        # Format the forecast data into an HTML table for browsers
        location = data.get('location', {}).get('name', 'Unknown location')
        forecast_days = data.get('forecast', {}).get('forecastday', [])
        if not forecast_days:
            return jsonify({'error': 'No forecast data available'}), 500

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
            </body>
        </html>
        """
        return html_response, 200

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        if response.status_code in [403, 429]:
            # Friendly banner for API key exhaustion or rate limiting
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
            return jsonify({'error': f'HTTP error occurred: {e}'}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)