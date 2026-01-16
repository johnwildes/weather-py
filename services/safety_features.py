"""
Safety Features Processing for Weather Application

This module provides functions to extract and format critical safety-related
weather data: UV Index, Air Quality Index (AQI), and Severe Weather Alerts.

Author: John Wildes
License: Apache License 2.0
"""

from typing import Optional, Dict, List, Any


def get_uv_info(current_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract and classify UV index information.
    
    Args:
        current_data: Current weather data dictionary from API
        
    Returns:
        Dictionary with UV value, level, color, and recommendation
    """
    uv_value = current_data.get('uv', 0)
    
    if uv_value <= 2:
        level = "Low"
        color = "#289500"  # Green
        recommendation = "Minimal protection needed. Wear sunglasses on bright days."
        icon = "🟢"
    elif uv_value <= 5:
        level = "Moderate"
        color = "#F7E400"  # Yellow
        recommendation = "Protection required. Wear sunscreen SPF 30+, hat, and sunglasses."
        icon = "🟡"
    elif uv_value <= 7:
        level = "High"
        color = "#F85900"  # Orange
        recommendation = "Protection essential. Seek shade during midday. Sunscreen, hat, and sunglasses required."
        icon = "🟠"
    elif uv_value <= 10:
        level = "Very High"
        color = "#D8001D"  # Red
        recommendation = "Extra protection required. Avoid sun 10am-4pm. Sunscreen SPF 50+, protective clothing required."
        icon = "🔴"
    else:  # 11+
        level = "Extreme"
        color = "#6B49C8"  # Purple
        recommendation = "Take all precautions. Avoid sun exposure. Unprotected skin can burn in minutes."
        icon = "🟣"
    
    return {
        'value': uv_value,
        'level': level,
        'color': color,
        'recommendation': recommendation,
        'icon': icon
    }


def get_aqi_info(current_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract and classify Air Quality Index information.
    
    Args:
        current_data: Current weather data dictionary from API
        
    Returns:
        Dictionary with AQI value, level, color, and health guidance
    """
    air_quality = current_data.get('air_quality', {})
    
    # WeatherAPI provides US EPA AQI
    aqi_value = air_quality.get('us-epa-index', 0)
    
    if aqi_value == 0:
        return None
    
    # EPA AQI levels (1-6)
    if aqi_value == 1:
        level = "Good"
        color = "#00E400"  # Green
        pm25 = air_quality.get('pm2_5', 0)
        pm10 = air_quality.get('pm10', 0)
        guidance = "Air quality is satisfactory. Air pollution poses little or no risk."
        icon = "🟢"
    elif aqi_value == 2:
        level = "Moderate"
        color = "#FFFF00"  # Yellow
        pm25 = air_quality.get('pm2_5', 0)
        pm10 = air_quality.get('pm10', 0)
        guidance = "Acceptable air quality. Unusually sensitive people should consider limiting prolonged outdoor exertion."
        icon = "🟡"
    elif aqi_value == 3:
        level = "Unhealthy for Sensitive Groups"
        color = "#FF7E00"  # Orange
        pm25 = air_quality.get('pm2_5', 0)
        pm10 = air_quality.get('pm10', 0)
        guidance = "People with respiratory or heart conditions, elderly, and children should limit prolonged outdoor exertion."
        icon = "🟠"
    elif aqi_value == 4:
        level = "Unhealthy"
        color = "#FF0000"  # Red
        pm25 = air_quality.get('pm2_5', 0)
        pm10 = air_quality.get('pm10', 0)
        guidance = "Everyone may begin to experience health effects. Sensitive groups should avoid prolonged outdoor exertion."
        icon = "🔴"
    elif aqi_value == 5:
        level = "Very Unhealthy"
        color = "#8F3F97"  # Purple
        pm25 = air_quality.get('pm2_5', 0)
        pm10 = air_quality.get('pm10', 0)
        guidance = "Health alert. Everyone should avoid prolonged outdoor exertion. Sensitive groups should avoid all outdoor activity."
        icon = "🟣"
    else:  # 6
        level = "Hazardous"
        color = "#7E0023"  # Maroon
        pm25 = air_quality.get('pm2_5', 0)
        pm10 = air_quality.get('pm10', 0)
        guidance = "Health warning of emergency conditions. Everyone should avoid all outdoor exertion."
        icon = "🟤"
    
    return {
        'value': aqi_value,
        'level': level,
        'color': color,
        'guidance': guidance,
        'icon': icon,
        'pm2_5': air_quality.get('pm2_5', 0),
        'pm10': air_quality.get('pm10', 0)
    }


def get_alerts_info(alerts_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract and format severe weather alerts.
    
    Args:
        alerts_data: Alerts data dictionary from API
        
    Returns:
        List of formatted alert dictionaries
    """
    alert_list = alerts_data.get('alert', [])
    
    if not alert_list:
        return []
    
    formatted_alerts = []
    
    for alert in alert_list:
        # Determine severity color
        severity = alert.get('severity', '').lower()
        if severity == 'extreme':
            color = "#D8001D"  # Red
            icon = "🔴"
        elif severity == 'severe':
            color = "#F85900"  # Orange
            icon = "🟠"
        elif severity == 'moderate':
            color = "#F7E400"  # Yellow
            icon = "🟡"
        else:
            color = "#289500"  # Green
            icon = "🟢"
        
        formatted_alerts.append({
            'headline': alert.get('headline', 'Weather Alert'),
            'event': alert.get('event', ''),
            'severity': severity.title(),
            'urgency': alert.get('urgency', '').title(),
            'areas': alert.get('areas', ''),
            'description': alert.get('desc', ''),
            'instruction': alert.get('instruction', ''),
            'effective': alert.get('effective', ''),
            'expires': alert.get('expires', ''),
            'color': color,
            'icon': icon
        })
    
    return formatted_alerts


def enrich_weather_data(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich weather data with safety features.
    
    Args:
        weather_data: Weather data dictionary from API
        
    Returns:
        Enhanced weather data with safety information
    """
    if not weather_data:
        return weather_data
    
    current = weather_data.get('current', {})
    alerts = weather_data.get('alerts', {})
    
    # Add safety features
    weather_data['uv_info'] = get_uv_info(current)
    weather_data['aqi_info'] = get_aqi_info(current)
    weather_data['alerts_info'] = get_alerts_info(alerts)
    
    return weather_data
