"""
Safety Features Implementation for Weather Application

This module provides production-ready implementations for displaying critical
safety-related weather attributes that are currently missing from the application:
1. UV Index
2. Air Quality Index (AQI)
3. Severe Weather Alerts

Author: Weather Safety Enhancement
Created: 2024
License: Apache License 2.0
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# FEATURE 1: UV INDEX
# ============================================================================

class UVLevel(Enum):
    """UV Index safety levels based on WHO standards."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


@dataclass
class UVIndexInfo:
    """
    UV Index information with safety classification.
    
    Attributes:
        value: UV index value (0-11+)
        level: Safety level classification
        color: Hex color code for display
        recommendation: Safety advice for users
    """
    value: float
    level: UVLevel
    color: str
    recommendation: str
    icon: str
    
    @classmethod
    def from_uv_value(cls, uv_value: float) -> 'UVIndexInfo':
        """
        Create UVIndexInfo from a UV index value.
        
        Args:
            uv_value: UV index (typically 0-11+)
            
        Returns:
            UVIndexInfo with appropriate safety classification
        """
        if uv_value < 0:
            uv_value = 0
            
        if uv_value <= 2:
            return cls(
                value=uv_value,
                level=UVLevel.LOW,
                color="#289500",  # Green
                recommendation="Minimal protection needed. Wear sunglasses on bright days.",
                icon="🟢"
            )
        elif uv_value <= 5:
            return cls(
                value=uv_value,
                level=UVLevel.MODERATE,
                color="#F7E400",  # Yellow
                recommendation="Protection required. Wear sunscreen SPF 30+, hat, and sunglasses.",
                icon="🟡"
            )
        elif uv_value <= 7:
            return cls(
                value=uv_value,
                level=UVLevel.HIGH,
                color="#F85900",  # Orange
                recommendation="Protection essential. Seek shade during midday. Sunscreen, hat, and sunglasses required.",
                icon="🟠"
            )
        elif uv_value <= 10:
            return cls(
                value=uv_value,
                level=UVLevel.VERY_HIGH,
                color="#D8001D",  # Red
                recommendation="Extra protection required. Avoid sun 10am-4pm. Sunscreen SPF 50+, protective clothing required.",
                icon="🔴"
            )
        else:  # 11+
            return cls(
                value=uv_value,
                level=UVLevel.EXTREME,
                color="#6B49C8",  # Violet
                recommendation="Avoid sun exposure. Stay indoors 10am-4pm. Full sun protection mandatory if outside.",
                icon="🟣"
            )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'value': self.value,
            'level': self.level.value,
            'color': self.color,
            'recommendation': self.recommendation,
            'icon': self.icon
        }


# ============================================================================
# FEATURE 2: AIR QUALITY INDEX (AQI)
# ============================================================================

class AQILevel(Enum):
    """Air Quality Index levels based on US EPA standards."""
    GOOD = "good"
    MODERATE = "moderate"
    UNHEALTHY_SENSITIVE = "unhealthy_for_sensitive_groups"
    UNHEALTHY = "unhealthy"
    VERY_UNHEALTHY = "very_unhealthy"
    HAZARDOUS = "hazardous"
    UNKNOWN = "unknown"


@dataclass
class AirQualityInfo:
    """
    Air Quality Index information with health classifications.
    
    Attributes:
        epa_index: EPA AQI index (1-6)
        level: AQI level classification
        color: Hex color code for display
        health_message: Health implications
        sensitive_groups: Who should be concerned
        pm2_5: PM2.5 concentration (optional)
        pm10: PM10 concentration (optional)
    """
    epa_index: int
    level: AQILevel
    color: str
    health_message: str
    sensitive_groups: str
    icon: str
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    
    @classmethod
    def from_api_data(cls, air_quality_data: dict) -> 'AirQualityInfo':
        """
        Create AirQualityInfo from WeatherAPI air quality data.
        
        Args:
            air_quality_data: Air quality dict from API with 'us-epa-index'
            
        Returns:
            AirQualityInfo with appropriate health classification
        """
        epa_index = air_quality_data.get('us-epa-index', 0)
        pm2_5 = air_quality_data.get('pm2_5')
        pm10 = air_quality_data.get('pm10')
        
        if epa_index == 1:
            return cls(
                epa_index=1,
                level=AQILevel.GOOD,
                color="#00E400",  # Green
                health_message="Air quality is satisfactory, and air pollution poses little or no risk.",
                sensitive_groups="None",
                icon="🟢",
                pm2_5=pm2_5,
                pm10=pm10
            )
        elif epa_index == 2:
            return cls(
                epa_index=2,
                level=AQILevel.MODERATE,
                color="#FFFF00",  # Yellow
                health_message="Air quality is acceptable. However, there may be a risk for some people.",
                sensitive_groups="Unusually sensitive people should consider limiting prolonged outdoor exertion.",
                icon="🟡",
                pm2_5=pm2_5,
                pm10=pm10
            )
        elif epa_index == 3:
            return cls(
                epa_index=3,
                level=AQILevel.UNHEALTHY_SENSITIVE,
                color="#FF7E00",  # Orange
                health_message="Members of sensitive groups may experience health effects.",
                sensitive_groups="Children, elderly, and people with respiratory or heart disease should limit prolonged outdoor exertion.",
                icon="🟠",
                pm2_5=pm2_5,
                pm10=pm10
            )
        elif epa_index == 4:
            return cls(
                epa_index=4,
                level=AQILevel.UNHEALTHY,
                color="#FF0000",  # Red
                health_message="Some members of the general public may experience health effects.",
                sensitive_groups="Everyone should limit outdoor exertion. Sensitive groups should avoid prolonged outdoor activities.",
                icon="🔴",
                pm2_5=pm2_5,
                pm10=pm10
            )
        elif epa_index == 5:
            return cls(
                epa_index=5,
                level=AQILevel.VERY_UNHEALTHY,
                color="#8F3F97",  # Purple
                health_message="Health alert: The risk of health effects is increased for everyone.",
                sensitive_groups="Everyone should avoid outdoor exertion. Sensitive groups should remain indoors.",
                icon="🟣",
                pm2_5=pm2_5,
                pm10=pm10
            )
        elif epa_index == 6:
            return cls(
                epa_index=6,
                level=AQILevel.HAZARDOUS,
                color="#7E0023",  # Maroon
                health_message="Health warning of emergency conditions. Everyone is likely to be affected.",
                sensitive_groups="Everyone should remain indoors with windows closed. Use air purifiers if available.",
                icon="🔴⚠️",
                pm2_5=pm2_5,
                pm10=pm10
            )
        else:
            return cls(
                epa_index=0,
                level=AQILevel.UNKNOWN,
                color="#808080",  # Gray
                health_message="Air quality data not available.",
                sensitive_groups="N/A",
                icon="❓",
                pm2_5=pm2_5,
                pm10=pm10
            )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            'epa_index': self.epa_index,
            'level': self.level.value,
            'color': self.color,
            'health_message': self.health_message,
            'sensitive_groups': self.sensitive_groups,
            'icon': self.icon
        }
        if self.pm2_5 is not None:
            result['pm2_5'] = self.pm2_5
        if self.pm10 is not None:
            result['pm10'] = self.pm10
        return result


# ============================================================================
# FEATURE 3: SEVERE WEATHER ALERTS
# ============================================================================

class AlertSeverity(Enum):
    """Weather alert severity levels."""
    EXTREME = "extreme"
    SEVERE = "severe"
    MODERATE = "moderate"
    MINOR = "minor"
    UNKNOWN = "unknown"


class AlertUrgency(Enum):
    """Weather alert urgency levels."""
    IMMEDIATE = "immediate"
    EXPECTED = "expected"
    FUTURE = "future"
    PAST = "past"
    UNKNOWN = "unknown"


@dataclass
class WeatherAlert:
    """
    Severe weather alert information.
    
    Attributes:
        headline: Brief alert headline
        event: Type of weather event
        severity: Alert severity level
        urgency: Alert urgency level
        areas: Affected areas
        description: Detailed alert description
        instruction: Safety instructions
        effective: When alert takes effect
        expires: When alert expires
        color: Display color based on severity
    """
    headline: str
    event: str
    severity: AlertSeverity
    urgency: AlertUrgency
    areas: str
    description: str
    instruction: str
    effective: datetime
    expires: datetime
    color: str
    icon: str
    
    @classmethod
    def from_api_data(cls, alert_data: dict) -> 'WeatherAlert':
        """
        Create WeatherAlert from WeatherAPI alert data.
        
        Args:
            alert_data: Alert dict from API
            
        Returns:
            WeatherAlert with parsed information
        """
        # Parse severity
        severity_str = alert_data.get('severity', '').lower()
        if 'extreme' in severity_str:
            severity = AlertSeverity.EXTREME
            color = "#FF0000"  # Red
            icon = "🚨"
        elif 'severe' in severity_str:
            severity = AlertSeverity.SEVERE
            color = "#FF4500"  # Orange-Red
            icon = "⚠️"
        elif 'moderate' in severity_str:
            severity = AlertSeverity.MODERATE
            color = "#FFA500"  # Orange
            icon = "⚡"
        elif 'minor' in severity_str:
            severity = AlertSeverity.MINOR
            color = "#FFD700"  # Gold
            icon = "ℹ️"
        else:
            severity = AlertSeverity.UNKNOWN
            color = "#808080"  # Gray
            icon = "📢"
        
        # Parse urgency
        urgency_str = alert_data.get('urgency', '').lower()
        if 'immediate' in urgency_str:
            urgency = AlertUrgency.IMMEDIATE
        elif 'expected' in urgency_str:
            urgency = AlertUrgency.EXPECTED
        elif 'future' in urgency_str:
            urgency = AlertUrgency.FUTURE
        elif 'past' in urgency_str:
            urgency = AlertUrgency.PAST
        else:
            urgency = AlertUrgency.UNKNOWN
        
        # Parse timestamps
        try:
            effective = datetime.fromisoformat(alert_data.get('effective', '').replace('Z', '+00:00'))
        except:
            effective = datetime.now()
            
        try:
            expires = datetime.fromisoformat(alert_data.get('expires', '').replace('Z', '+00:00'))
        except:
            expires = datetime.now()
        
        return cls(
            headline=alert_data.get('headline', 'Weather Alert'),
            event=alert_data.get('event', 'Unknown Event'),
            severity=severity,
            urgency=urgency,
            areas=alert_data.get('areas', ''),
            description=alert_data.get('desc', ''),
            instruction=alert_data.get('instruction', ''),
            effective=effective,
            expires=expires,
            color=color,
            icon=icon
        )
    
    def is_active(self) -> bool:
        """Check if alert is currently active."""
        now = datetime.now(self.effective.tzinfo) if self.effective.tzinfo else datetime.now()
        return self.effective <= now <= self.expires
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'headline': self.headline,
            'event': self.event,
            'severity': self.severity.value,
            'urgency': self.urgency.value,
            'areas': self.areas,
            'description': self.description,
            'instruction': self.instruction,
            'effective': self.effective.isoformat(),
            'expires': self.expires.isoformat(),
            'color': self.color,
            'icon': self.icon,
            'is_active': self.is_active()
        }


# ============================================================================
# INTEGRATED SAFETY DATA CLASS
# ============================================================================

@dataclass
class SafetyWeatherData:
    """
    Complete safety weather information for a location.
    
    Combines UV index, air quality, and weather alerts into a single
    data structure for easy display and API responses.
    """
    uv_index: Optional[UVIndexInfo] = None
    air_quality: Optional[AirQualityInfo] = None
    alerts: List[WeatherAlert] = None
    
    def __post_init__(self):
        if self.alerts is None:
            self.alerts = []
    
    @classmethod
    def from_weather_api_response(cls, weather_data: dict) -> 'SafetyWeatherData':
        """
        Extract safety information from WeatherAPI response.
        
        Args:
            weather_data: Full weather data dict from WeatherAPI
            
        Returns:
            SafetyWeatherData with all available safety information
        """
        # Extract UV Index
        uv_index = None
        current = weather_data.get('current', {})
        if 'uv' in current:
            uv_index = UVIndexInfo.from_uv_value(current['uv'])
        
        # Extract Air Quality
        air_quality = None
        if 'air_quality' in current and current['air_quality']:
            air_quality = AirQualityInfo.from_api_data(current['air_quality'])
        
        # Extract Weather Alerts
        alerts = []
        alerts_data = weather_data.get('alerts', {}).get('alert', [])
        for alert_data in alerts_data:
            alerts.append(WeatherAlert.from_api_data(alert_data))
        
        return cls(
            uv_index=uv_index,
            air_quality=air_quality,
            alerts=alerts
        )
    
    def has_active_alerts(self) -> bool:
        """Check if there are any active weather alerts."""
        return any(alert.is_active() for alert in self.alerts)
    
    def get_active_alerts(self) -> List[WeatherAlert]:
        """Get only currently active alerts."""
        return [alert for alert in self.alerts if alert.is_active()]
    
    def get_safety_summary(self) -> dict:
        """
        Get a summary of all safety concerns.
        
        Returns:
            Dict with safety status and priority level
        """
        concerns = []
        priority = 0  # 0=safe, 1=caution, 2=warning, 3=danger
        
        # Check UV
        if self.uv_index:
            if self.uv_index.level == UVLevel.EXTREME:
                concerns.append("Extreme UV radiation")
                priority = max(priority, 3)
            elif self.uv_index.level == UVLevel.VERY_HIGH:
                concerns.append("Very high UV radiation")
                priority = max(priority, 2)
            elif self.uv_index.level == UVLevel.HIGH:
                concerns.append("High UV radiation")
                priority = max(priority, 1)
        
        # Check Air Quality
        if self.air_quality:
            if self.air_quality.level == AQILevel.HAZARDOUS:
                concerns.append("Hazardous air quality")
                priority = max(priority, 3)
            elif self.air_quality.level == AQILevel.VERY_UNHEALTHY:
                concerns.append("Very unhealthy air quality")
                priority = max(priority, 3)
            elif self.air_quality.level == AQILevel.UNHEALTHY:
                concerns.append("Unhealthy air quality")
                priority = max(priority, 2)
            elif self.air_quality.level == AQILevel.UNHEALTHY_SENSITIVE:
                concerns.append("Air quality concern for sensitive groups")
                priority = max(priority, 1)
        
        # Check Alerts
        active_alerts = self.get_active_alerts()
        for alert in active_alerts:
            concerns.append(f"{alert.event} ({alert.severity.value})")
            if alert.severity == AlertSeverity.EXTREME:
                priority = max(priority, 3)
            elif alert.severity == AlertSeverity.SEVERE:
                priority = max(priority, 3)
            elif alert.severity == AlertSeverity.MODERATE:
                priority = max(priority, 2)
        
        return {
            'priority': priority,
            'priority_label': ['Safe', 'Caution', 'Warning', 'Danger'][priority],
            'concerns': concerns,
            'has_concerns': len(concerns) > 0,
            'active_alerts_count': len(active_alerts)
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'uv_index': self.uv_index.to_dict() if self.uv_index else None,
            'air_quality': self.air_quality.to_dict() if self.air_quality else None,
            'alerts': [alert.to_dict() for alert in self.alerts],
            'active_alerts': [alert.to_dict() for alert in self.get_active_alerts()],
            'safety_summary': self.get_safety_summary()
        }


# ============================================================================
# FLASK ROUTE EXAMPLE
# ============================================================================

def example_flask_route():
    """
    Example Flask route showing how to integrate safety features.
    
    This would be added to forecast.py or a new safety.py blueprint.
    """
    from flask import jsonify, request
    
    # Example route to get safety data
    # @forecast_bp.route('/api/safety-info', methods=['GET'])
    def get_safety_info():
        """Get safety information for a location."""
        location = request.args.get('location')
        if not location:
            return jsonify({'error': 'Location required'}), 400
        
        # Get weather service (existing pattern)
        from forecast import get_weather_service
        service = get_weather_service()
        
        # Get weather data (already fetches AQI and alerts)
        weather_data = service.get_weather_data(location)
        if not weather_data:
            return jsonify({'error': 'Unable to fetch weather data'}), 500
        
        # Extract safety information
        safety_data = SafetyWeatherData.from_weather_api_response(weather_data)
        
        return jsonify(safety_data.to_dict()), 200


# ============================================================================
# TEMPLATE HELPER FUNCTIONS
# ============================================================================

def get_uv_badge_html(uv_value: float) -> str:
    """
    Generate HTML for UV index badge display.
    
    Args:
        uv_value: UV index value
        
    Returns:
        HTML string for badge
    """
    uv_info = UVIndexInfo.from_uv_value(uv_value)
    return f'''
    <div class="uv-badge" style="background-color: {uv_info.color}; color: white; padding: 8px 12px; border-radius: 4px;">
        <span class="uv-icon">{uv_info.icon}</span>
        <span class="uv-value">UV {uv_info.value:.0f}</span>
        <span class="uv-level">{uv_info.level.value.replace('_', ' ').title()}</span>
    </div>
    <p class="uv-recommendation" style="margin-top: 8px; font-size: 0.9em;">
        {uv_info.recommendation}
    </p>
    '''


def get_aqi_badge_html(air_quality_data: dict) -> str:
    """
    Generate HTML for AQI badge display.
    
    Args:
        air_quality_data: Air quality dict from API
        
    Returns:
        HTML string for badge
    """
    if not air_quality_data:
        return '<p class="aqi-unavailable">Air quality data unavailable</p>'
    
    aqi_info = AirQualityInfo.from_api_data(air_quality_data)
    return f'''
    <div class="aqi-badge" style="background-color: {aqi_info.color}; color: {'white' if aqi_info.epa_index >= 4 else 'black'}; padding: 8px 12px; border-radius: 4px;">
        <span class="aqi-icon">{aqi_info.icon}</span>
        <span class="aqi-level">{aqi_info.level.value.replace('_', ' ').title()}</span>
    </div>
    <p class="aqi-health-message" style="margin-top: 8px; font-size: 0.9em;">
        <strong>Health:</strong> {aqi_info.health_message}
    </p>
    <p class="aqi-sensitive-groups" style="margin-top: 4px; font-size: 0.85em; font-style: italic;">
        {aqi_info.sensitive_groups}
    </p>
    '''


def get_alert_html(alert: WeatherAlert) -> str:
    """
    Generate HTML for weather alert display.
    
    Args:
        alert: WeatherAlert object
        
    Returns:
        HTML string for alert
    """
    return f'''
    <div class="weather-alert" style="border-left: 4px solid {alert.color}; padding: 12px; margin: 8px 0; background-color: rgba(255,0,0,0.1);">
        <div class="alert-header">
            <span class="alert-icon">{alert.icon}</span>
            <strong class="alert-headline">{alert.headline}</strong>
        </div>
        <p class="alert-event"><strong>Event:</strong> {alert.event}</p>
        <p class="alert-severity"><strong>Severity:</strong> {alert.severity.value.title()}</p>
        <p class="alert-expires"><strong>Expires:</strong> {alert.expires.strftime('%Y-%m-%d %H:%M')}</p>
        <p class="alert-description">{alert.description}</p>
        {f'<p class="alert-instruction"><strong>Instructions:</strong> {alert.instruction}</p>' if alert.instruction else ''}
    </div>
    '''


if __name__ == '__main__':
    # Demo the functionality
    print("=== UV INDEX DEMO ===")
    for uv in [1.5, 4.0, 6.5, 9.0, 12.0]:
        uv_info = UVIndexInfo.from_uv_value(uv)
        print(f"UV {uv}: {uv_info.level.value} - {uv_info.recommendation}")
    
    print("\n=== AIR QUALITY DEMO ===")
    for epa_idx in range(1, 7):
        aqi_info = AirQualityInfo.from_api_data({'us-epa-index': epa_idx})
        print(f"EPA {epa_idx}: {aqi_info.level.value} - {aqi_info.health_message}")
    
    print("\n=== WEATHER ALERT DEMO ===")
    sample_alert = {
        'headline': 'Excessive Heat Warning',
        'event': 'Excessive Heat',
        'severity': 'Extreme',
        'urgency': 'Expected',
        'areas': 'Phoenix Metro Area',
        'desc': 'Dangerously hot conditions with temperatures up to 115F expected.',
        'instruction': 'Drink plenty of fluids, stay in air-conditioned spaces, check on relatives.',
        'effective': '2024-07-15T12:00:00-07:00',
        'expires': '2024-07-15T20:00:00-07:00'
    }
    alert = WeatherAlert.from_api_data(sample_alert)
    print(f"Alert: {alert.headline} ({alert.severity.value}) - {alert.instruction}")
