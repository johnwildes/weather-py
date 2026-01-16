"""
Tests for safety features module.

Author: John Wildes
License: Apache License 2.0
"""

import pytest
from services.safety_features import get_uv_info, get_aqi_info, get_alerts_info, enrich_weather_data


def test_uv_info_low():
    """Test UV index classification for low levels."""
    current_data = {'uv': 1.5}
    uv_info = get_uv_info(current_data)
    
    assert uv_info['value'] == 1.5
    assert uv_info['level'] == 'Low'
    assert uv_info['color'] == '#289500'
    assert 'Minimal protection' in uv_info['recommendation']
    assert uv_info['icon'] == '🟢'


def test_uv_info_moderate():
    """Test UV index classification for moderate levels."""
    current_data = {'uv': 4}
    uv_info = get_uv_info(current_data)
    
    assert uv_info['value'] == 4
    assert uv_info['level'] == 'Moderate'
    assert uv_info['color'] == '#F7E400'
    assert 'SPF 30+' in uv_info['recommendation']


def test_uv_info_high():
    """Test UV index classification for high levels."""
    current_data = {'uv': 6}
    uv_info = get_uv_info(current_data)
    
    assert uv_info['value'] == 6
    assert uv_info['level'] == 'High'
    assert uv_info['color'] == '#F85900'


def test_uv_info_very_high():
    """Test UV index classification for very high levels."""
    current_data = {'uv': 9}
    uv_info = get_uv_info(current_data)
    
    assert uv_info['value'] == 9
    assert uv_info['level'] == 'Very High'
    assert uv_info['color'] == '#D8001D'


def test_uv_info_extreme():
    """Test UV index classification for extreme levels."""
    current_data = {'uv': 12}
    uv_info = get_uv_info(current_data)
    
    assert uv_info['value'] == 12
    assert uv_info['level'] == 'Extreme'
    assert uv_info['color'] == '#6B49C8'


def test_aqi_info_good():
    """Test AQI classification for good air quality."""
    current_data = {
        'air_quality': {
            'us-epa-index': 1,
            'pm2_5': 10.5,
            'pm10': 20.3
        }
    }
    aqi_info = get_aqi_info(current_data)
    
    assert aqi_info['value'] == 1
    assert aqi_info['level'] == 'Good'
    assert aqi_info['color'] == '#00E400'
    assert aqi_info['pm2_5'] == 10.5
    assert aqi_info['pm10'] == 20.3


def test_aqi_info_moderate():
    """Test AQI classification for moderate air quality."""
    current_data = {
        'air_quality': {
            'us-epa-index': 2,
            'pm2_5': 25.0,
            'pm10': 50.0
        }
    }
    aqi_info = get_aqi_info(current_data)
    
    assert aqi_info['value'] == 2
    assert aqi_info['level'] == 'Moderate'
    assert 'sensitive people' in aqi_info['guidance']


def test_aqi_info_unhealthy_sensitive():
    """Test AQI classification for unhealthy for sensitive groups."""
    current_data = {
        'air_quality': {
            'us-epa-index': 3,
            'pm2_5': 55.0,
            'pm10': 100.0
        }
    }
    aqi_info = get_aqi_info(current_data)
    
    assert aqi_info['value'] == 3
    assert aqi_info['level'] == 'Unhealthy for Sensitive Groups'
    assert aqi_info['color'] == '#FF7E00'


def test_aqi_info_no_data():
    """Test AQI when no air quality data is available."""
    current_data = {
        'air_quality': {
            'us-epa-index': 0
        }
    }
    aqi_info = get_aqi_info(current_data)
    
    assert aqi_info is None


def test_alerts_info_with_alerts():
    """Test alert parsing with active alerts."""
    alerts_data = {
        'alert': [
            {
                'headline': 'Severe Thunderstorm Warning',
                'event': 'Thunderstorm',
                'severity': 'severe',
                'urgency': 'immediate',
                'areas': 'County A, County B',
                'desc': 'Severe thunderstorms expected.',
                'instruction': 'Take shelter immediately.',
                'effective': '2024-01-01T10:00:00',
                'expires': '2024-01-01T18:00:00'
            }
        ]
    }
    alerts = get_alerts_info(alerts_data)
    
    assert len(alerts) == 1
    assert alerts[0]['headline'] == 'Severe Thunderstorm Warning'
    assert alerts[0]['severity'] == 'Severe'
    assert alerts[0]['color'] == '#F85900'


def test_alerts_info_extreme():
    """Test alert parsing for extreme severity."""
    alerts_data = {
        'alert': [
            {
                'headline': 'Tornado Warning',
                'event': 'Tornado',
                'severity': 'extreme',
                'urgency': 'immediate',
                'areas': 'County C',
                'desc': 'Tornado on the ground.',
                'instruction': 'Take cover now!',
                'effective': '2024-01-01T10:00:00',
                'expires': '2024-01-01T11:00:00'
            }
        ]
    }
    alerts = get_alerts_info(alerts_data)
    
    assert len(alerts) == 1
    assert alerts[0]['color'] == '#D8001D'  # Red for extreme
    assert alerts[0]['icon'] == '🔴'


def test_alerts_info_no_alerts():
    """Test alert parsing with no active alerts."""
    alerts_data = {'alert': []}
    alerts = get_alerts_info(alerts_data)
    
    assert len(alerts) == 0


def test_enrich_weather_data():
    """Test enrichment of weather data with safety features."""
    weather_data = {
        'current': {
            'uv': 6,
            'air_quality': {
                'us-epa-index': 2,
                'pm2_5': 25.0,
                'pm10': 50.0
            }
        },
        'alerts': {
            'alert': [
                {
                    'headline': 'Heat Advisory',
                    'event': 'Heat',
                    'severity': 'moderate',
                    'urgency': 'expected',
                    'areas': 'County D',
                    'desc': 'High temperatures expected.',
                    'instruction': 'Stay hydrated.',
                    'effective': '2024-01-01T10:00:00',
                    'expires': '2024-01-01T20:00:00'
                }
            ]
        }
    }
    
    enriched = enrich_weather_data(weather_data)
    
    assert 'uv_info' in enriched
    assert 'aqi_info' in enriched
    assert 'alerts_info' in enriched
    
    assert enriched['uv_info']['level'] == 'High'
    assert enriched['aqi_info']['level'] == 'Moderate'
    assert len(enriched['alerts_info']) == 1


def test_enrich_weather_data_none():
    """Test enrichment handles None input gracefully."""
    enriched = enrich_weather_data(None)
    assert enriched is None


def test_enrich_weather_data_empty():
    """Test enrichment with minimal data."""
    weather_data = {
        'current': {},
        'alerts': {}
    }
    
    enriched = enrich_weather_data(weather_data)
    
    assert 'uv_info' in enriched
    # AQI should be None when no data
    assert enriched['aqi_info'] is None
    # Alerts should be empty list
    assert len(enriched['alerts_info']) == 0
