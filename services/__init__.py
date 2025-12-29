"""
Weather services package.

This module provides an abstraction layer for weather data providers,
allowing easy switching between different weather APIs.
"""

from .weather_service import WeatherService, WeatherServiceError
from .weatherapi_provider import WeatherAPIProvider

__all__ = ['WeatherService', 'WeatherServiceError', 'WeatherAPIProvider']
