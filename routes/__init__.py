"""
Route blueprints package.

This module exports all Flask blueprints for easy registration in the main app.
"""

from .forecast import forecast_bp
from .home import home_bp
from .chat import chat_bp

__all__ = ['forecast_bp', 'home_bp', 'chat_bp']
