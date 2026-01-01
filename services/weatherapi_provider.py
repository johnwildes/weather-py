"""
WeatherAPI.com provider implementation.

This module implements the WeatherService interface for weatherapi.com,
handling all API communication, error handling, and response formatting.
Includes server-side caching to reduce API calls and improve response times.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional
from cachetools import TTLCache

from .weather_service import (
    WeatherService,
    WeatherServiceError,
    APIKeyMissingError,
    LocationNotFoundError,
    APIRequestError,
    SearchResult
)

# Cache configuration
# Weather data caches (5-minute TTL for frequently changing data)
WEATHER_CACHE_TTL = 300  # 5 minutes
WEATHER_CACHE_MAXSIZE = 100

# Location caches (longer TTL since locations don't change)
LOCATION_CACHE_TTL = 3600  # 1 hour
LOCATION_CACHE_MAXSIZE = 200

# Search cache (10-minute TTL)
SEARCH_CACHE_TTL = 600  # 10 minutes
SEARCH_CACHE_MAXSIZE = 100


class WeatherAPIProvider(WeatherService):
    """
    Weather service implementation using WeatherAPI.com.

    Provides forecast, historical, and location search capabilities
    through the WeatherAPI REST API.
    """

    BASE_URL = "http://api.weatherapi.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the WeatherAPI provider.

        Args:
            api_key: WeatherAPI key. If not provided, reads from
                     WEATHER_API_KEY environment variable.
        """
        self._api_key = api_key or os.getenv('WEATHER_API_KEY')

        # Initialize caches
        self._weather_cache = TTLCache(maxsize=WEATHER_CACHE_MAXSIZE, ttl=WEATHER_CACHE_TTL)
        self._forecast_cache = TTLCache(maxsize=WEATHER_CACHE_MAXSIZE, ttl=WEATHER_CACHE_TTL)
        self._location_cache = TTLCache(maxsize=LOCATION_CACHE_MAXSIZE, ttl=LOCATION_CACHE_TTL)
        self._search_cache = TTLCache(maxsize=SEARCH_CACHE_MAXSIZE, ttl=SEARCH_CACHE_TTL)
        self._hourly_cache = TTLCache(maxsize=WEATHER_CACHE_MAXSIZE, ttl=WEATHER_CACHE_TTL)
        self._current_cache = TTLCache(maxsize=WEATHER_CACHE_MAXSIZE, ttl=WEATHER_CACHE_TTL)

    @staticmethod
    def _cache_key(*args) -> str:
        """Generate a cache key from arguments."""
        return ':'.join(str(arg).lower().strip() for arg in args)

    @property
    def api_key(self) -> str:
        """Get the API key, raising an error if not configured."""
        if not self._api_key:
            raise APIKeyMissingError("WEATHER_API_KEY is not configured")
        return self._api_key

    def _make_request(self, endpoint: str, params: dict) -> Optional[dict]:
        """
        Make an API request to WeatherAPI.

        Args:
            endpoint: API endpoint (e.g., 'forecast.json')
            params: Query parameters (api key added automatically)

        Returns:
            JSON response as dict, or None on failure

        Raises:
            APIKeyMissingError: If API key is not configured
            APIRequestError: If the request fails
        """
        params['key'] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                # Location not found or invalid query
                return None
            raise APIRequestError(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"Request failed: {e}")

    def get_weather_data(self, location: str) -> Optional[dict]:
        """
        Get current weather, 3-day forecast, and 7-day history for a location.

        Args:
            location: Location query (city, ZIP, coordinates, etc.)

        Returns:
            Dictionary with location, current, forecast, alerts, and history data.
            Returns None if the location is invalid.
        """
        cache_key = self._cache_key('weather', location)

        # Check cache first
        if cache_key in self._weather_cache:
            return self._weather_cache[cache_key]

        try:
            # Get forecast with alerts and air quality
            forecast_data = self._make_request('forecast.json', {
                'q': location,
                'days': 3,
                'aqi': 'yes',
                'alerts': 'yes'
            })

            if not forecast_data:
                return None

            # Get historical data for the past 7 days
            history_data = self._get_history(location, days=7)

            result = {
                'location': forecast_data.get('location', {}),
                'current': forecast_data.get('current', {}),
                'forecast': forecast_data.get('forecast', {}),
                'alerts': forecast_data.get('alerts', {}),
                'history': history_data
            }

            # Cache the result
            self._weather_cache[cache_key] = result
            return result

        except WeatherServiceError:
            return None
        except Exception as e:
            print(f"Error fetching weather data for {location}: {e}")
            return None

    def _get_history(self, location: str, days: int = 7) -> list[dict]:
        """
        Fetch historical weather data for the past N days.

        Args:
            location: Location query
            days: Number of days of history to fetch

        Returns:
            List of historical weather data dictionaries
        """
        history_data = []
        for i in range(1, days + 1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            try:
                data = self._make_request('history.json', {
                    'q': location,
                    'dt': date
                })
                if data:
                    history_data.append(data)
            except WeatherServiceError:
                # Continue even if some history requests fail
                continue
        return history_data

    def validate_location(self, location: str) -> tuple[bool, Optional[dict]]:
        """
        Validate if a location exists using the current weather endpoint.

        Args:
            location: Location query to validate

        Returns:
            Tuple of (is_valid, location_info or None)
        """
        cache_key = self._cache_key('validate', location)

        # Check cache first
        if cache_key in self._location_cache:
            return self._location_cache[cache_key]

        try:
            data = self._make_request('current.json', {'q': location})
            if data:
                result = (True, data.get('location', {}))
                # Cache only successful validations
                self._location_cache[cache_key] = result
                return result

            # For invalid or empty responses, do not cache the negative result
            return False, None
        except WeatherServiceError:
            # On API errors, also avoid caching so callers can retry quickly
            return False, None

    def search_locations(self, query: str, limit: int = 10) -> list[SearchResult]:
        """
        Search for locations matching a query.

        Args:
            query: Search string (partial city name, etc.)
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        if not query or len(query) < 2:
            return []

        cache_key = self._cache_key('search', query, limit)

        # Check cache first
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        try:
            data = self._make_request('search.json', {'q': query})
            if not data:
                return []

            results = []
            for item in data[:limit]:
                results.append(SearchResult(
                    name=item.get('name', ''),
                    region=item.get('region', ''),
                    country=item.get('country', ''),
                    display=f"{item.get('name', '')}, {item.get('region', '')}, {item.get('country', '')}",
                    value=item.get('name', '')
                ))

            # Cache the results
            self._search_cache[cache_key] = results
            return results

        except WeatherServiceError:
            return []

    def get_detailed_forecast(self, location: str, days: int = 10) -> Optional[dict]:
        """
        Get extended forecast with astronomy and hourly data.

        Args:
            location: Location query
            days: Number of forecast days (max 10 for free tier)

        Returns:
            Dictionary with detailed forecast, astronomy, and hourly data
        """
        cache_key = self._cache_key('detailed', location, days)

        # Check cache first
        if cache_key in self._forecast_cache:
            return self._forecast_cache[cache_key]

        try:
            data = self._make_request('forecast.json', {
                'q': location,
                'days': days,
                'aqi': 'yes',
                'alerts': 'yes'
            })

            if not data:
                return None

            # Extract astronomy and hourly data from forecast days
            astronomy = []
            hourly = []

            for day in data.get('forecast', {}).get('forecastday', []):
                astronomy.append({
                    'date': day.get('date'),
                    'astro': day.get('astro', {}),
                    'moon_phase': day.get('astro', {}).get('moon_phase', ''),
                    'moon_illumination': day.get('astro', {}).get('moon_illumination', '')
                })

                # Include hourly data for first 3 days
                if len(hourly) < 3:
                    hourly.append({
                        'date': day.get('date'),
                        'hours': day.get('hour', [])
                    })

            result = {
                'location': data.get('location', {}),
                'current': data.get('current', {}),
                'forecast': data.get('forecast', {}),
                'alerts': data.get('alerts', {}),
                'astronomy': astronomy,
                'hourly': hourly
            }

            # Cache the result
            self._forecast_cache[cache_key] = result
            return result

        except WeatherServiceError:
            return None

    def get_hourly_forecast(self, location: str, date: str) -> Optional[dict]:
        """
        Get hourly weather data for a specific date.

        Uses forecast endpoint for future dates, history endpoint for past dates.

        Args:
            location: Location query
            date: Date in YYYY-MM-DD format

        Returns:
            Dictionary with hourly breakdown, day summary, and astronomy
        """
        cache_key = self._cache_key('hourly', location, date)

        # Check cache first
        if cache_key in self._hourly_cache:
            return self._hourly_cache[cache_key]

        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
            today = datetime.now().date()

            # Choose appropriate endpoint based on date
            if target_date > today:
                endpoint = 'forecast.json'
            else:
                endpoint = 'history.json'

            data = self._make_request(endpoint, {
                'q': location,
                'dt': date
            })

            if not data:
                return None

            # Extract forecast day data
            forecast_days = data.get('forecast', {}).get('forecastday', [])
            forecast_day = forecast_days[0] if forecast_days else {}

            result = {
                'location': data.get('location', {}),
                'date': date,
                'hourly': forecast_day.get('hour', []),
                'day_summary': forecast_day.get('day', {}),
                'astronomy': forecast_day.get('astro', {})
            }

            # Cache the result
            self._hourly_cache[cache_key] = result
            return result

        except (WeatherServiceError, ValueError):
            return None

    def get_current_location_by_ip(self, ip: Optional[str] = None) -> Optional[dict]:
        """
        Get location and current weather based on IP address.

        Args:
            ip: IP address to lookup. Uses 'auto:ip' for auto-detection if None.

        Returns:
            Dictionary with user_info and current_weather
        """
        query = ip if ip else 'auto:ip'

        try:
            # Get IP-based location info
            ip_data = self._make_request('ip.json', {'q': query})

            if not ip_data:
                return None

            # Get current weather for the detected location
            city = ip_data.get('city', 'London')
            weather_data = self._make_request('current.json', {
                'q': city,
                'aqi': 'yes'
            })

            return {
                'user_info': ip_data,
                'current_weather': weather_data
            }

        except WeatherServiceError:
            return None

    def get_current_weather(self, location: str) -> Optional[dict]:
        """
        Get only current weather conditions for a location.

        Args:
            location: Location query

        Returns:
            Full current weather response including location data
        """
        cache_key = self._cache_key('current', location)

        # Check cache first
        if cache_key in self._current_cache:
            return self._current_cache[cache_key]

        try:
            result = self._make_request('current.json', {
                'q': location,
                'aqi': 'yes'
            })

            if result:
                # Cache the result
                self._current_cache[cache_key] = result

            return result
        except WeatherServiceError:
            return None
