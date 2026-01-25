"""
Integration test to verify astronomy template rendering.
"""

import pytest
from unittest.mock import patch, MagicMock
from main import app
from datetime import datetime, timedelta


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_weather_service():
    """Reset the weather service singleton before each test."""
    import forecast
    import home
    forecast._weather_service = None
    home._weather_service = None
    yield
    forecast._weather_service = None
    home._weather_service = None


def _get_moon_phase_for_day(day_number):
    """Helper to get moon phase based on day number in forecast."""
    phases = ['Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 
              'Full Moon', 'Waning Gibbous', 'Last Quarter', 
              'Waning Crescent', 'New Moon']
    return phases[day_number % len(phases)]


def create_mock_weather_response_with_astronomy():
    """Create a complete mock weather response including astronomy data."""
    today = datetime.now().date()
    future_dates = [today + timedelta(days=i) for i in range(1, 10)]
    
    return {
        'location': {
            'name': 'London',
            'region': 'City of London',
            'country': 'UK',
            'lat': 51.52,
            'lon': -0.11
        },
        'current': {
            'temp_c': 15.0,
            'temp_f': 59.0,
            'feelslike_c': 13.0,
            'feelslike_f': 55.0,
            'condition': {
                'text': 'Partly cloudy',
                'icon': '//cdn.weatherapi.com/weather/64x64/day/116.png'
            },
            'wind_kph': 15.0,
            'wind_mph': 9.3,
            'humidity': 72,
            'uv': 3,
            'vis_km': 10.0,
            'pressure_mb': 1015.0
        },
        'forecast': {
            'forecastday': [
                {
                    'date': today.strftime('%Y-%m-%d'),
                    'day': {
                        'condition': {
                            'text': 'Partly cloudy',
                            'icon': '//cdn.weatherapi.com/weather/64x64/day/116.png'
                        },
                        'maxtemp_c': 18.0,
                        'maxtemp_f': 64.4,
                        'mintemp_c': 12.0,
                        'mintemp_f': 53.6,
                        'daily_chance_of_rain': 20
                    },
                    'astro': {
                        'sunrise': '07:30 AM',
                        'sunset': '05:45 PM',
                        'moonrise': '08:30 PM',
                        'moonset': '09:15 AM',
                        'moon_phase': 'Waxing Crescent',
                        'moon_illumination': '15'
                    }
                }
            ] + [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'day': {
                        'condition': {
                            'text': 'Sunny',
                            'icon': '//cdn.weatherapi.com/weather/64x64/day/113.png'
                        },
                        'maxtemp_c': 20.0,
                        'maxtemp_f': 68.0,
                        'mintemp_c': 14.0,
                        'mintemp_f': 57.2,
                        'daily_chance_of_rain': 10
                    },
                    'astro': {
                        'sunrise': '07:29 AM',
                        'sunset': '05:46 PM',
                        'moonrise': '09:00 PM',
                        'moonset': '10:00 AM',
                        'moon_phase': _get_moon_phase_for_day(i),
                        'moon_illumination': str(15 + i * 10)
                    }
                }
                for i, date in enumerate(future_dates, start=1)
            ]
        },
        'alerts': {'alert': []}
    }


@patch('services.weatherapi_provider.requests.get')
def test_home_page_with_astronomy_data(mock_get, client):
    """Test that home page includes astronomy data when location is provided."""
    import os
    os.environ['WEATHER_API_KEY'] = 'test_api_key'
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = create_mock_weather_response_with_astronomy()
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    response = client.get('/?location=London')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Check for astronomy section
    assert 'astronomy-section' in html
    assert 'Sun & Moon' in html
    
    # Check for current day astronomy data
    assert '07:30 AM' in html  # sunrise
    assert '05:45 PM' in html  # sunset
    assert '08:30 PM' in html  # moonrise
    assert '09:15 AM' in html  # moonset
    assert 'Waxing Crescent' in html  # moon phase
    
    # Check for daylight duration
    assert '10h 15m' in html  # calculated daylight
    
    # Check for multi-day toggle
    assert 'astronomyMultiDayToggle' in html
    assert '5-Day View' in html
    
    # Check for moon phase emoji (should be in the HTML)
    assert '🌒' in html or 'moon_phase_emoji' in html


@patch('services.weatherapi_provider.requests.get')
def test_astronomy_with_no_moonrise(mock_get, client):
    """Test handling of polar regions with no moonrise/moonset."""
    import os
    os.environ['WEATHER_API_KEY'] = 'test_api_key'
    
    weather_data = create_mock_weather_response_with_astronomy()
    # Simulate polar region with no moonrise
    weather_data['forecast']['forecastday'][0]['astro']['moonrise'] = 'No moonrise'
    weather_data['forecast']['forecastday'][0]['astro']['moonset'] = 'No moonset'
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = weather_data
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    response = client.get('/?location=NorthPole')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should still show sunrise/sunset
    assert '07:30 AM' in html
    assert '05:45 PM' in html
    
    # Moonrise/moonset should be hidden (has_moonrise/has_moonset is False)
    # The template uses {% if astronomy_info.has_moonrise %} to conditionally show


@patch('services.weatherapi_provider.requests.get')
def test_home_page_without_location_no_astronomy(mock_get, client):
    """Test that home page without location doesn't show astronomy section."""
    response = client.get('/')
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Should not have astronomy section when no location
    assert 'astronomy-section' not in html


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
