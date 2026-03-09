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
   WEATHER_DEBUG_MODE=true  # Optional: Enable debug panel
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

## Debug Panel

When `WEATHER_DEBUG_MODE=true` is set in your `.env` file, a debug panel becomes available. The panel is hidden by default and can be opened by:
- Clicking the "🔧 DEBUG" tab on the left edge of the screen
- Pressing `Ctrl+Shift+D`

The debug panel provides:
- **Weather JSON** - Raw API response for the current city with syntax highlighting
- **Cache** - View cached API requests with TTL countdown
- **State** - Live StateManager state and event log
- **Requests** - API call history with timing and status
- **Environment** - Server info and safe environment variables

> **Note**: The debug panel is hidden on mobile devices (screens ≤ 768px).

## Deployment

This project includes a GitHub Actions workflow (`.github/workflows/deploy-to-azure.yml`) that deploys **both** the Python/Flask app and the Blazor Server app to Azure Container Apps on every push to `master`.

### Python / Flask App

The existing `Dockerfile` builds the Flask app. It is deployed to the Azure Container App specified by the `CONTAINER_APP_NAME` repository secret.

### Blazor Server App (`WeatherBlazor/`)

The `Dockerfile.blazor` file contains the multi-stage build definition for the .NET 10 Blazor Server application located in `WeatherBlazor/`.

#### Building the Blazor container locally

```bash
# Build the image (run from the repository root)
docker build -f Dockerfile.blazor -t weather-blazor:latest .

# Run the container locally
docker run -p 8080:80 \
  -e WeatherApiKey=your_weather_api_key \
  -e AzureOpenAI__ApiKey=your_openai_key \
  -e AzureOpenAI__Endpoint=your_openai_endpoint \
  -e AzureOpenAI__Deployment=your_deployment_name \
  weather-blazor:latest
# Visit http://localhost:8080
```

#### CI/CD — Blazor deployment

The `build-and-deploy-blazor` job in the workflow builds and pushes the Blazor image to GitHub Container Registry as `weather-blazor:latest`, then deploys it to a **separate** Azure Container App (distinct from the Python app) so Azure generates a unique URL for the Blazor front-end.

On first run the job **creates** the Container App; subsequent runs **update** it.

#### Required repository secrets for the Blazor job

| Secret | Description |
|---|---|
| `AZURE_CLIENT_ID` | Azure service-principal / app registration client ID (shared) |
| `AZURE_TENANT_ID` | Azure AD tenant ID (shared) |
| `AZURE_SUB_ID` | Azure subscription ID (shared) |
| `GHCR_USERNAME` | GitHub username for GHCR authentication (shared) |
| `GHCR_PAT` | GitHub personal access token with `write:packages` scope (shared) |
| `RESOURCE_GROUP` | Azure resource group name (shared) |
| `CONTAINER_APP_ENVIRONMENT` | Name of the existing Azure Container Apps managed environment (shared) |
| `BLAZOR_CONTAINER_APP_NAME` | **New** — unique name for the Blazor Container App (e.g. `weather-blazor`) |
| `WEATHER_API_KEY` | **New** — API key for [weatherapi.com](https://www.weatherapi.com/) |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key (shared) |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL (shared) |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment/model name (shared) |

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contact

Author: John Wildes  
Email: johnwildes@decklatedev.com
