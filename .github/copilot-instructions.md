# Weather-Py Copilot Instructions

## Architecture Overview

This is a **Flask-based weather application** using the WeatherAPI.com service with a Microsoft Fluent UI frontend.

### Backend Structure
- **Entry point**: [main.py](../main.py) - Flask app initialization, blueprint registration, and API route mounting
- **Blueprints**: Routes split into `forecast.py` (weather data) and `home.py` (landing page)
- **Service layer**: [services/](../services/) implements the Provider pattern:
  - `WeatherService` (ABC) - abstract interface for weather providers
  - `WeatherAPIProvider` - concrete implementation for weatherapi.com
  - Swap providers by implementing `WeatherService` interface

### Frontend Architecture
- **Fluent UI Web Components** via CDN (not npm)
- **State Management**: [static/js/state-manager.js](../static/js/state-manager.js) - central state with localStorage persistence and event emitter pattern
- **API Layer**: [static/js/weather-api.js](../static/js/weather-api.js) - request deduplication, caching (5min TTL), error handling
- **Templates**: Jinja2 in [templates/](../templates/) with reusable components in `templates/components/`

## Key Patterns

### Weather Service Singleton
```python
# In forecast.py/home.py - lazy initialization pattern
_weather_service = None
def get_weather_service():
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherAPIProvider()
    return _weather_service
```

### Response Format Detection
Routes return HTML for browsers, JSON for CLI tools (based on User-Agent):
```python
is_browser = any(b in user_agent for b in ['mozilla', 'chrome', 'safari', 'firefox', 'edge'])
```

### Dataclasses for API Models
Use dataclasses in [services/weather_service.py](../services/weather_service.py):
- `LocationInfo` - standardized location data with `from_dict()`/`to_dict()` methods
- `SearchResult` - autocomplete results

## Development Commands

```bash
# Quick start (creates venv if needed)
./start.sh

# Manual run
python main.py              # Runs on port 5000
FLASK_DEBUG=true python main.py  # Enable hot reload

# Testing
pytest                      # Run all tests
pytest test_main.py -v      # Verbose single file

# Docker
docker build -t weather-py .
docker run -e WEATHER_API_KEY=xxx -p 80:80 weather-py
```

## Environment Variables

Required in `.env`:
```
WEATHER_API_KEY=your_key    # Required - from weatherapi.com
DEFAULT_ZIP_CODE=12345      # Optional - fallback for CLI requests
FLASK_DEBUG=true            # Optional - enables reload
PORT=5000                   # Optional - defaults to 5000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/forecast` | GET | HTML page or JSON (zip query param) |
| `/api/weather/bulk` | POST | Batch weather for `{locations: [...]}` |
| `/api/validate-location` | GET | Check if location exists |
| `/api/search-locations` | GET | Autocomplete (q param, min 2 chars) |
| `/api/detailed-forecast` | GET | Extended forecast with astronomy |
| `/api/hourly-forecast` | GET | Hourly data (location + date params) |

## Testing Conventions

- Tests use `pytest` with Flask test client
- Mock external API calls: `@patch('services.weatherapi_provider.requests.get')`
- Reset singleton between tests (see `reset_weather_service` fixture in [test_main.py](../test_main.py))
- Test files prefixed with `test_`

## Adding a New Weather Provider

1. Create `services/newprovider.py` implementing `WeatherService` ABC
2. Implement required methods: `get_weather_data()`, `validate_location()`, `search_locations()`, `get_bulk_weather()`
3. Export in `services/__init__.py`
4. Update `get_weather_service()` factory to use new provider
