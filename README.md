# Weather Forecast Application

This project provides a modern weather forecast web application using the WeatherAPI.com service. It has been **completely rebuilt using Blazor** (.NET 10) with a **Microsoft Fluent UI** interface.

![Weather App Screenshot](https://github.com/user-attachments/assets/37e297ac-57a1-48b2-b628-880ed1f7c550)

## ✨ Features

### Core Weather Functionality
- 10-day weather forecast with detailed conditions
- Current weather conditions (temperature, humidity, wind, visibility, pressure)
- Astronomy data (sunrise/sunset, moon phase & illumination)
- Weather alerts with collapsible detail cards

### Safety Metrics
- **UV Index** classification (Low → Extreme) with WHO recommendations
- **Air Quality Index** (EPA scale) with health guidance and PM2.5/PM10 readings

### Modern User Interface
- **Microsoft Fluent UI for Blazor** components
- **Location autocomplete** search powered by WeatherAPI
- **Temperature unit toggle** — switch between °C and °F
- **Dark/Light theme** toggle
- Responsive layout for desktop and mobile

## Prerequisites

- [.NET 10 SDK](https://dotnet.microsoft.com/download)
- A WeatherAPI key (sign up at [WeatherAPI.com](https://www.weatherapi.com/))

## Getting Started

### 1. Configure your API key

Set your WeatherAPI key via one of these methods:

**Option A — `appsettings.json`** (development only; keep out of source control):
```json
{
  "WeatherApiKey": "your_key_here"
}
```

**Option B — Environment variable** (recommended for production):
```bash
export WEATHER_API_KEY=your_key_here
```

### 2. Run the application

```bash
cd WeatherBlazor
dotnet run
```

Then open your browser at `http://localhost:5155/`.

### Run tests

```bash
cd WeatherBlazor.Tests
dotnet test
```

## Project Structure

```
WeatherBlazor/                        ← Blazor Web App (.NET 10)
├── Components/
│   ├── Layout/
│   │   ├── MainLayout.razor          ← Header, search bar, theme toggle
│   │   └── ReconnectModal.razor
│   ├── Pages/
│   │   ├── Home.razor                ← Main weather page
│   │   └── NotFound.razor
│   └── Weather/
│       ├── SearchBar.razor           ← Autocomplete location search
│       ├── CurrentWeatherCard.razor  ← Current conditions
│       ├── ForecastList.razor        ← 10-day forecast
│       ├── AstronomyCard.razor       ← Sun/moon information
│       ├── SafetyMetrics.razor       ← UV Index + Air Quality
│       └── AlertsSection.razor       ← Collapsible weather alerts
├── Models/
│   └── WeatherModels.cs              ← All data models (C# records/classes)
├── Services/
│   ├── IWeatherService.cs            ← Service interface
│   ├── WeatherApiService.cs          ← WeatherAPI.com implementation
│   ├── SafetyFeaturesService.cs      ← UV + AQI enrichment
│   └── AstronomyService.cs           ← Moon phase + daylight enrichment
└── wwwroot/
    └── app.css                       ← Weather app styles (light + dark)

WeatherBlazor.Tests/                  ← xUnit unit tests
├── SafetyFeaturesServiceTests.cs
└── AstronomyServiceTests.cs
```

## Architecture

The application uses **Blazor Server** with interactive server-side rendering:

- **`IWeatherService`** — abstraction layer; swap providers by implementing this interface
- **`WeatherApiService`** — concrete implementation using `HttpClient` + `System.Text.Json`
- **`SafetyFeaturesService`** — static enrichment for UV Index and Air Quality
- **`AstronomyService`** — static enrichment for astronomy data and moon phases
- Dependency injection via `Program.cs`; API key read from `WeatherApiKey` config or `WEATHER_API_KEY` env var


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
