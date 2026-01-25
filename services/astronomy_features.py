"""
Astronomy features module for processing sun and moon data.

This module enriches weather data with astronomy information including
sunrise, sunset, moonrise, moonset, moon phase with emojis, and daylight duration.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


def get_moon_phase_emoji(phase: str) -> str:
    """
    Get emoji representation for moon phase.
    
    Args:
        phase: Moon phase name (e.g., "New Moon", "First Quarter")
    
    Returns:
        Emoji string representing the moon phase
    """
    phase_lower = phase.lower() if phase else ""
    
    moon_phases = {
        "new moon": "🌑",
        "waxing crescent": "🌒",
        "first quarter": "🌓",
        "waxing gibbous": "🌔",
        "full moon": "🌕",
        "waning gibbous": "🌖",
        "last quarter": "🌗",
        "waning crescent": "🌘",
        "third quarter": "🌗",  # Alias for last quarter
    }
    
    return moon_phases.get(phase_lower, "🌙")


def calculate_daylight_duration(sunrise: str, sunset: str) -> Optional[str]:
    """
    Calculate daylight duration from sunrise and sunset times.
    
    Args:
        sunrise: Sunrise time in format "HH:MM AM/PM"
        sunset: Sunset time in format "HH:MM AM/PM"
    
    Returns:
        Formatted string like "14h 23m" or None if calculation fails
    """
    if not sunrise or not sunset:
        return None
    
    try:
        # Parse 12-hour format times
        sunrise_time = datetime.strptime(sunrise, "%I:%M %p")
        sunset_time = datetime.strptime(sunset, "%I:%M %p")
        
        # Calculate duration
        duration = sunset_time - sunrise_time
        
        # Handle cases where sunset is "before" sunrise (crosses midnight)
        if duration.total_seconds() < 0:
            duration = timedelta(days=1) + duration
        
        # Convert to hours and minutes
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
    except (ValueError, AttributeError):
        return None


def process_astronomy_day(day_data: Dict[str, Any], is_current_day: bool = False) -> Dict[str, Any]:
    """
    Process astronomy data for a single day.
    
    Args:
        day_data: Forecast day data containing 'astro' field
        is_current_day: Whether this is the current day
    
    Returns:
        Dictionary with processed astronomy information
    """
    astro = day_data.get('astro', {})
    
    sunrise = astro.get('sunrise', '')
    sunset = astro.get('sunset', '')
    moonrise = astro.get('moonrise', '')
    moonset = astro.get('moonset', '')
    moon_phase = astro.get('moon_phase', '')
    moon_illumination = astro.get('moon_illumination', '')
    
    # Calculate daylight duration
    daylight_duration = calculate_daylight_duration(sunrise, sunset)
    
    # Get moon phase emoji
    moon_emoji = get_moon_phase_emoji(moon_phase)
    
    return {
        'date': day_data.get('date', ''),
        'is_current_day': is_current_day,
        'sunrise': sunrise,
        'sunset': sunset,
        'moonrise': moonrise,
        'moonset': moonset,
        'has_moonrise': bool(moonrise and moonrise.lower() != 'no moonrise'),
        'has_moonset': bool(moonset and moonset.lower() != 'no moonset'),
        'moon_phase': moon_phase,
        'moon_phase_emoji': moon_emoji,
        'moon_illumination': moon_illumination,
        'daylight_duration': daylight_duration
    }


def get_astronomy_data(weather_data: Optional[Dict[str, Any]], include_current_day: bool = True) -> List[Dict[str, Any]]:
    """
    Extract and process astronomy data from weather forecast.
    
    Args:
        weather_data: Weather data dictionary from API
        include_current_day: Whether to include today in the results
    
    Returns:
        List of processed astronomy data dictionaries
    """
    if not weather_data or 'forecast' not in weather_data:
        return []
    
    forecast = weather_data['forecast']
    if not forecast or 'forecastday' not in forecast:
        return []
    
    forecastdays = forecast['forecastday']
    if not forecastdays:
        return []
    
    astronomy_data = []
    today = datetime.now().date()
    
    for idx, day_data in enumerate(forecastdays):
        try:
            day_date = datetime.strptime(day_data.get('date', ''), '%Y-%m-%d').date()
            is_current_day = (day_date == today)
            
            # Skip current day if requested
            if is_current_day and not include_current_day:
                continue
            
            processed = process_astronomy_day(day_data, is_current_day)
            astronomy_data.append(processed)
            
        except (ValueError, AttributeError):
            # Skip days with invalid date format
            continue
    
    return astronomy_data


def enrich_with_astronomy(weather_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Enrich weather data with processed astronomy information.
    
    Adds 'astronomy_info' field with current day astronomy and
    'astronomy_forecast' with 5-day forecast (excluding current day).
    
    Args:
        weather_data: Weather data dictionary from API
    
    Returns:
        Enriched weather data or None if input is None
    """
    if not weather_data:
        return None
    
    # Get current day astronomy
    current_astronomy = get_astronomy_data(weather_data, include_current_day=True)
    if current_astronomy:
        weather_data['astronomy_info'] = current_astronomy[0]
    
    # Get multi-day astronomy forecast (excluding current day, next 5 days)
    all_astronomy = get_astronomy_data(weather_data, include_current_day=False)
    # Limit to next 5 days
    weather_data['astronomy_forecast'] = all_astronomy[:5]
    
    return weather_data
