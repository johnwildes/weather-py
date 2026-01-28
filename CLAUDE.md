# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Quick start (creates venv, installs deps, runs app)
./start.sh

# Manual run
python main.py                        # Runs on port 5000
FLASK_DEBUG=true python main.py       # With hot reload

# Testing
pytest                                # All tests
pytest test_main.py -v                # Single file, verbose
pytest test_main.py::test_name -v     # Single test

# Docker
docker build -t weather-py .
docker run -e WEATHER_API_KEY=xxx -p 80:80 weather-py
```

## Environment Variables

Required: `WEATHER_API_KEY` (from weatherapi.com). Optional: `DEFAULT_ZIP_CODE`, `FLASK_DEBUG`, `PORT` (default 5000), `WEATHER_DEBUG_MODE` (enables debug panel). Chat features require `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`. See `.env.example`.

## Architecture

**Flask backend** with **Fluent UI Web Components frontend** (CDN, not npm). Weather data from weatherapi.com API.

### Backend (Python/Flask)

- **Entry point**: `main.py` — Flask app init, blueprint registration, API route mounting, template filters
- **Blueprints**: `forecast.py` (weather data routes), `home.py` (home page), `chat.py` (AI assistant via Azure OpenAI)
- **Service layer** (`services/`): Provider pattern with abstract base class
  - `weather_service.py` — `WeatherService` ABC defining the interface, plus dataclasses (`LocationInfo`, `SearchResult`) and custom exceptions (`WeatherServiceError`, `APIKeyMissingError`, `LocationNotFoundError`, `APIRequestError`)
  - `weatherapi_provider.py` — Concrete implementation using weatherapi.com with TTL caching (`cachetools.TTLCache`: weather 5min, location 1hr, search 10min)
  - `astronomy_features.py` — Sun/moon data enrichment (moon phase emojis, daylight duration)
  - `safety_features.py` — UV Index (WHO), Air Quality (EPA), Weather Alerts (NOAA/NWS)
- **Singleton pattern**: Weather service and Azure client are lazily initialized module-level singletons. Tests must reset these between runs (see `reset_weather_service` autouse fixture in `test_main.py`)
- **Response format detection**: Routes check User-Agent to return HTML for browsers, JSON for CLI tools

### Frontend (JavaScript/Jinja2)

- `static/js/weather-app.js` — Main app class, event coordination, initializes all other modules
- `static/js/state-manager.js` — Central state with localStorage persistence, event emitter pattern for reactivity
- `static/js/weather-api.js` — API layer with request deduplication, 5min client-side cache, error handling
- `static/js/chat-agent.js` — Chat UI and Azure OpenAI integration
- `static/js/debug-panel.js` — Dev tools panel (toggle: Ctrl+Shift+D), conditional on `WEATHER_DEBUG_MODE`
- `static/js/sw.js` — Service worker for PWA offline support
- `templates/` — Jinja2 templates; reusable components in `templates/components/`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page (`?location=<query>`) |
| `/forecast` | GET | HTML or JSON based on User-Agent |
| `/api/weather/bulk` | POST | Batch weather for `{locations: [...]}` |
| `/api/validate-location` | GET | Check if location exists |
| `/api/search-locations` | GET | Autocomplete (q param, min 2 chars) |
| `/api/detailed-forecast` | GET | Extended forecast with astronomy |
| `/api/hourly-forecast` | GET | Hourly data (location + date params) |
| `/api/debug/info` | GET | Debug info (requires `WEATHER_DEBUG_MODE=true`) |
| `/api/chat/send-message` | POST | AI chat endpoint |

## Testing Conventions

- Framework: pytest with Flask test client
- Test files are in the project root (e.g., `test_main.py`, `test_chat.py`, `test_safety_features.py`)
- Mock external API calls with `@patch('services.weatherapi_provider.requests.get')`
- Singleton must be reset between tests via autouse fixture
- Tests cover both browser (HTML) and CLI (JSON) response paths

## Adding a New Weather Provider

1. Create `services/newprovider.py` implementing `WeatherService` ABC
2. Implement all required methods: `get_weather_data()`, `validate_location()`, `search_locations()`, `get_detailed_forecast()`, `get_hourly_forecast()`, `get_current_location_by_ip()`, `get_bulk_weather()`
3. Export in `services/__init__.py`
4. Update `get_weather_service()` factory function in the consuming modules

## CI/CD

- **Deploy to Azure**: `.github/workflows/deploy-to-azure.yml` — triggers on push to `master`, builds Docker image, pushes to GHCR, deploys to Azure Container Apps
- **Issue Review Agent**: `.github/workflows/issue-review-agent.yml` — custom TypeScript GitHub Action (`.github/actions/issue-review/`) that auto-assesses issue severity
