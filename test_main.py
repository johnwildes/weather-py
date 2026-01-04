# Import necessary modules for testing
import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from main import app

@pytest.fixture
def client():
    # Set up a test client for the Flask application
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


@patch('services.weatherapi_provider.requests.get')
def test_missing_zip_code(mock_get, client):
    # Test the behavior when no ZIP code is provided in the request
    # With browser User-Agent, returns HTML page (no error)
    # With CLI User-Agent and no default ZIP, returns error
    os.environ.pop('DEFAULT_ZIP_CODE', None)
    headers = {'User-Agent': 'curl/7.68.0'}
    response = client.get('/forecast', headers=headers)
    assert response.status_code == 400
    assert response.json == {'error': 'ZIP code is required and no default is configured'}


@patch('services.weatherapi_provider.requests.get')
def test_missing_api_key(mock_get, client):
    # Test the behavior when the API key is not configured
    os.environ.pop('WEATHER_API_KEY', None)
    headers = {'User-Agent': 'curl/7.68.0'}
    response = client.get('/forecast?zip=12345', headers=headers)
    assert response.status_code == 500
    assert response.json == {'error': 'Unable to fetch weather data'}


@patch('services.weatherapi_provider.requests.get')
def test_successful_response(mock_get, client):
    # Test a successful response from the weather API
    os.environ['WEATHER_API_KEY'] = 'test_api_key'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'location': {'name': 'Test City', 'region': 'Test Region', 'country': 'Test Country'},
        'current': {
            'temp_c': 20.0,
            'temp_f': 68.0,
            'feelslike_c': 19.0,
            'feelslike_f': 66.0,
            'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/icon.png'},
            'wind_kph': 10.0,
            'wind_mph': 6.2,
            'humidity': 50,
            'uv': 5,
            'vis_km': 10.0,
            'pressure_mb': 1015.0,
            'precip_mm': 0.0,
            'cloud': 20,
            'air_quality': {}
        },
        'forecast': {
            'forecastday': [
                {
                    'date': '2023-01-01',
                    'day': {
                        'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/icon.png'},
                        'maxtemp_c': 25.0,
                        'maxtemp_f': 77.0,
                        'mintemp_c': 15.0,
                        'mintemp_f': 59.0,
                        'daily_chance_of_rain': 0,
                        'daily_chance_of_snow': 0,
                    },
                }
            ]
        },
        'alerts': {'alert': []}
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    headers = {'User-Agent': 'Mozilla/5.0 Chrome/91.0'}
    response = client.get('/forecast?zip=12345', headers=headers)
    # Browser requests now redirect to home page
    assert response.status_code == 302
    assert '/?location=12345' in response.location


@patch('services.weatherapi_provider.requests.get')
def test_api_error_response(mock_get, client):
    # Test the behavior when the weather API raises an exception
    os.environ['WEATHER_API_KEY'] = 'test_api_key'
    mock_get.side_effect = Exception('API error')

    headers = {'User-Agent': 'curl/7.68.0'}
    response = client.get('/forecast?zip=12345', headers=headers)
    assert response.status_code == 500
    assert response.json == {'error': 'Unable to fetch weather data'}


@patch('services.weatherapi_provider.requests.get')
def test_cli_user_agent(mock_get, client):
    # Test the response for a CLI user agent (returns JSON)
    os.environ['WEATHER_API_KEY'] = 'test_api_key'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'location': {'name': 'Test City'},
        'current': {'temp_c': 20.0},
        'forecast': {
            'forecastday': [
                {
                    'date': '2023-01-01',
                    'day': {
                        'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/icon.png'},
                        'maxtemp_c': 25.0,
                        'maxtemp_f': 77.0,
                        'mintemp_c': 15.0,
                        'mintemp_f': 59.0,
                    },
                }
            ]
        },
        'alerts': {}
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    headers = {'User-Agent': 'curl/7.68.0'}
    response = client.get('/forecast?zip=12345', headers=headers)
    assert response.status_code == 200
    assert response.is_json
    assert 'forecast' in response.json


@patch('services.weatherapi_provider.requests.get')
def test_browser_user_agent(mock_get, client):
    # Test the response for a browser user agent (returns HTML)
    os.environ['WEATHER_API_KEY'] = 'test_api_key'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'location': {'name': 'Test City', 'region': 'Test Region', 'country': 'Test Country'},
        'current': {
            'temp_c': 20.0,
            'temp_f': 68.0,
            'feelslike_c': 19.0,
            'feelslike_f': 66.0,
            'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/icon.png'},
            'wind_kph': 10.0,
            'wind_mph': 6.2,
            'humidity': 50,
            'uv': 5,
            'vis_km': 10.0,
            'pressure_mb': 1015.0,
            'precip_mm': 0.0,
            'cloud': 20,
            'air_quality': {}
        },
        'forecast': {
            'forecastday': [
                {
                    'date': '2023-01-01',
                    'day': {
                        'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/icon.png'},
                        'maxtemp_c': 25.0,
                        'maxtemp_f': 77.0,
                        'mintemp_c': 15.0,
                        'mintemp_f': 59.0,
                        'daily_chance_of_rain': 0,
                        'daily_chance_of_snow': 0,
                    },
                }
            ]
        },
        'alerts': {'alert': []}
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = client.get('/forecast?zip=12345', headers=headers)
    # Browser requests now redirect to home page
    assert response.status_code == 302
    assert '/?location=12345' in response.location


@patch('services.weatherapi_provider.requests.get')
def test_home_route_with_error(mock_get, client):
    # Test error handling in home route
    os.environ['WEATHER_API_KEY'] = 'test_api_key'
    mock_get.side_effect = Exception('API connection error')
    
    response = client.get('/?location=12345')
    assert response.status_code == 200
    # Check that error message is in the response
    assert b'Error Loading Weather Data' in response.data
    assert b'Unable to fetch weather data for' in response.data


@patch('services.weatherapi_provider.requests.get')
def test_home_route_without_location(mock_get, client):
    # Test home route without location parameter (shows empty state)
    response = client.get('/')
    assert response.status_code == 200
    # Check for empty state content
    assert b'Search for a location' in response.data


# PWA Functionality Tests
def test_manifest_json_accessible(client):
    """Test that manifest.json is accessible and has correct content-type"""
    response = client.get('/static/manifest.json')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    # Verify manifest content
    manifest_data = response.json
    assert manifest_data['name'] == 'Weather App'
    assert manifest_data['short_name'] == 'Weather'
    assert manifest_data['display'] == 'standalone'
    assert manifest_data['theme_color'] == '#0078d4'
    assert 'icons' in manifest_data
    assert len(manifest_data['icons']) > 0


def test_service_worker_accessible(client):
    """Test that service worker file (sw.js) is accessible"""
    response = client.get('/static/js/sw.js')
    assert response.status_code == 200
    # Content-type should be JavaScript (may include charset)
    assert 'javascript' in response.content_type.lower()
    
    # Verify service worker contains key functionality
    sw_content = response.data.decode('utf-8')
    assert 'serviceWorker' in sw_content or 'Service Worker' in sw_content
    assert 'install' in sw_content
    assert 'fetch' in sw_content
    assert 'activate' in sw_content


def test_base_html_pwa_meta_tags(client):
    """Test that base.html includes required PWA meta tags and manifest link"""
    # Get a page that extends base.html
    response = client.get('/')
    assert response.status_code == 200
    
    html_content = response.data.decode('utf-8')
    
    # Check for PWA meta tags
    assert 'name="theme-color"' in html_content
    assert 'content="#0078d4"' in html_content
    assert 'name="description"' in html_content
    assert 'name="apple-mobile-web-app-capable"' in html_content
    assert 'content="yes"' in html_content
    assert 'name="apple-mobile-web-app-status-bar-style"' in html_content
    assert 'name="apple-mobile-web-app-title"' in html_content
    assert 'content="Weather"' in html_content
    
    # Check for manifest link
    assert 'rel="manifest"' in html_content
    assert 'manifest.json' in html_content
    
    # Check for apple touch icon
    assert 'rel="apple-touch-icon"' in html_content


def test_service_worker_registration_script(client):
    """Test that service worker registration script is present in base.html"""
    # Get a page that extends base.html
    response = client.get('/')
    assert response.status_code == 200
    
    html_content = response.data.decode('utf-8')
    
    # Check for service worker registration script
    assert "'serviceWorker' in navigator" in html_content or '"serviceWorker" in navigator' in html_content
    assert 'navigator.serviceWorker.register' in html_content
    assert '/static/js/sw.js' in html_content
    assert 'SW registered' in html_content or 'registration.scope' in html_content
    assert 'SW registration failed' in html_content or 'error' in html_content

