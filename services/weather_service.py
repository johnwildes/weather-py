"""
Abstract base class for weather service providers.

This module defines the interface that all weather providers must implement,
enabling easy switching between different weather APIs (WeatherAPI, OpenWeather, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class APIKeyMissingError(WeatherServiceError):
    """Raised when the API key is not configured."""
    pass


class LocationNotFoundError(WeatherServiceError):
    """Raised when a location cannot be found."""
    pass


class APIRequestError(WeatherServiceError):
    """Raised when an API request fails."""
    pass


@dataclass
class LocationInfo:
    """Standardized location information."""
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str = ""
    localtime: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'LocationInfo':
        return cls(
            name=data.get('name', ''),
            region=data.get('region', ''),
            country=data.get('country', ''),
            lat=data.get('lat', 0.0),
            lon=data.get('lon', 0.0),
            tz_id=data.get('tz_id', ''),
            localtime=data.get('localtime', '')
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'region': self.region,
            'country': self.country,
            'lat': self.lat,
            'lon': self.lon,
            'tz_id': self.tz_id,
            'localtime': self.localtime
        }


@dataclass
class SearchResult:
    """Standardized location search result."""
    name: str
    region: str
    country: str
    display: str
    value: str

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'region': self.region,
            'country': self.country,
            'display': self.display,
            'value': self.value
        }


class WeatherService(ABC):
    """
    Abstract base class defining the interface for weather data providers.

    All weather providers (WeatherAPI, OpenWeather, etc.) must implement
    these methods to ensure consistent behavior across the application.
    """

    @abstractmethod
    def get_weather_data(self, location: str) -> Optional[dict]:
        """
        Get current weather and forecast data for a location.

        Args:
            location: Location query (city name, ZIP code, coordinates, etc.)

        Returns:
            Dictionary containing:
                - location: LocationInfo dict
                - current: Current conditions
                - forecast: Multi-day forecast
                - alerts: Weather alerts (if any)
                - history: Historical data (if available)
            Returns None if the request fails.
        """
        pass

    @abstractmethod
    def validate_location(self, location: str) -> tuple[bool, Optional[dict]]:
        """
        Validate if a location exists and can be queried.

        Args:
            location: Location query to validate

        Returns:
            Tuple of (is_valid, location_info_dict or None)
        """
        pass

    @abstractmethod
    def search_locations(self, query: str, limit: int = 10) -> list[SearchResult]:
        """
        Search for locations matching a query string.

        Args:
            query: Search query (partial city name, etc.)
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects
        """
        pass

    @abstractmethod
    def get_detailed_forecast(self, location: str, days: int = 10) -> Optional[dict]:
        """
        Get extended forecast with astronomy and hourly data.

        Args:
            location: Location query
            days: Number of forecast days (provider-dependent maximum)

        Returns:
            Dictionary containing detailed forecast data, or None on failure
        """
        pass

    @abstractmethod
    def get_hourly_forecast(self, location: str, date: str) -> Optional[dict]:
        """
        Get hourly forecast/history for a specific date.

        Args:
            location: Location query
            date: Date in YYYY-MM-DD format

        Returns:
            Dictionary containing hourly data, or None on failure
        """
        pass

    @abstractmethod
    def get_current_location_by_ip(self, ip: Optional[str] = None) -> Optional[dict]:
        """
        Get location information based on IP address.

        Args:
            ip: IP address to lookup (None for auto-detect)

        Returns:
            Dictionary with location and current weather, or None on failure
        """
        pass

    def get_bulk_weather(self, locations: list[str]) -> list[dict]:
        """
        Get weather data for multiple locations.

        Default implementation calls get_weather_data for each location.
        Providers may override with batch API support.

        Args:
            locations: List of location queries

        Returns:
            List of weather data dictionaries (excludes failed requests)
        """
        results = []
        for location in locations:
            data = self.get_weather_data(location)
            if data:
                results.append(data)
        return results
