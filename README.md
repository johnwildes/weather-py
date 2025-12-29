# Weather Forecast Application

This project is a modern Flask-based web application that provides weather forecasts using the WeatherAPI. The application features a contemporary **Microsoft Fluent UI** interface with support for multiple locations, interactive weather cards, and both JSON (for CLI tools) and HTML (for browsers) responses.

## ✨ Features

### Core Weather Functionality
- Retrieve weather forecasts for multiple locations simultaneously
- 3-day weather forecast with detailed conditions
- 7-day historical weather data
- Current weather conditions with comprehensive details
- Weather maps and geolocation support

### Modern User Interface
- **Microsoft Fluent UI** components for a contemporary, accessible design
- **Multi-location Management** - Add, remove, and monitor multiple locations
- **Interactive Toolbar** - Smart location input with validation and search
- **Responsive Design** - Optimized for desktop, tablet, and mobile devices
- **Dark/Light Theme** support with system preference detection

### Advanced Features
- **Location Search** - Auto-complete suggestions for cities worldwide
- **Geolocation Support** - "Use Current Location" functionality
- **Persistent Settings** - Remembers your selected locations and preferences
- **Temperature Units** - Switch between Celsius and Fahrenheit
- **View Modes** - Grid view and comparison table for multiple locations
- **Detailed Forecasts** - Expandable cards with extended weather information

### API Support
- RESTful API endpoints for programmatic access
- Bulk weather data retrieval for multiple locations
- Location validation and search endpoints
- Both JSON and HTML responses based on client type

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

### Quick Start

1. Run the quick start script:
   ```bash
   ./start.sh
   ```

### Manual Setup

1. Start the Flask application:
   ```bash
   python main.py
   ```

2. **Web Interface**: Open your browser and navigate to:
   - **Home**: `http://localhost:5000/` - Weather map and location info
   - **Forecast**: `http://localhost:5000/forecast` - Multi-location weather dashboard
   - **Legacy**: `http://localhost:5000/forecast?zip=12345` - Single location (legacy mode)

3. **Using the Toolbar**:
   - Enter a ZIP code, city name, or coordinates in the location input
   - Click "Add Location" or press Enter to add to your dashboard
   - Use "Current Location" to add your geographic location
   - Manage multiple locations with the toolbar controls

### API Endpoints

The application provides several API endpoints for programmatic access:

```bash
# Validate a location
curl "http://localhost:5000/api/validate-location?location=New York"

# Search for locations
curl "http://localhost:5000/api/search-locations?q=London"

# Get bulk weather data for multiple locations
curl -X POST http://localhost:5000/api/weather/bulk \
  -H "Content-Type: application/json" \
  -d '{"locations": ["New York", "London", "Tokyo"], "tempUnit": "celsius"}'

# Get detailed forecast for a location
curl "http://localhost:5000/api/detailed-forecast?location=Paris"
```

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
