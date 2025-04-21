# Weather Forecast Application

This project is a Flask-based web application that provides weather forecasts using the WeatherAPI. Users can retrieve a 10-day weather forecast by providing a ZIP code. The application supports both JSON responses for CLI tools and HTML responses for browsers.

## Features

- Retrieve weather forecasts for a given ZIP code.
- Supports both JSON (for CLI tools) and HTML (for browsers) responses.
- Displays weather conditions, high/low temperatures, and forecast icons.
- Handles errors gracefully, including missing API keys or ZIP codes.

## Prerequisites

- Python 3.13 or higher
- A WeatherAPI key (sign up at [WeatherAPI](https://www.weatherapi.com/) to get one)
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/weather-py.git
   cd weather-py
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add the following:
   ```
   WEATHER_API_KEY=your_weather_api_key
   DEFAULT_ZIP_CODE=your_default_zip_code
   FLASK_DEBUG=true
   ```

## Usage

### Running Locally

1. Start the Flask application:
   ```bash
   python main.py
   ```

2. Open your browser and navigate to `http://localhost:5000/forecast?zip=12345` (replace `12345` with your desired ZIP code).

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t weather-py .
   ```

2. Run the container:
   ```bash
   docker run -p 80:80 -e WEATHER_API_KEY=your_weather_api_key weather-py
   ```

3. Access the application at `http://localhost/forecast?zip=12345`.

## Testing

Run the test suite using `pytest`:
```bash
pytest
```

## Deployment

This project includes a GitHub Actions workflow (`.github/workflows/deploy-to-azure.yml`) for deploying to Azure Container Apps. Ensure the required secrets are configured in your repository.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contact

Author: John Wildes  
Email: johnwildes@decklatedev.com
