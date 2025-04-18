# Import necessary modules for testing
import os
import pytest
from unittest.mock import patch
from flask import Flask
from main import app

@pytest.fixture
def client():
    # Set up a test client for the Flask application
    app.testing = True
    with app.test_client() as client:
        yield client

@patch('main.requests.get')
def test_missing_zip_code(mock_get, client):
    # Test the behavior when no ZIP code is provided in the request
    response = client.get('/forecast')
    assert response.status_code == 400
    assert response.json == {'error': 'ZIP code is required'}

@patch('main.requests.get')
def test_missing_api_key(mock_get, client):
    # Test the behavior when the API key is not configured
    os.environ.pop('WEATHER_API_KEY', None)  # Ensure API key is not set
    response = client.get('/forecast?zip=12345')
    assert response.status_code == 500
    assert response.json == {'error': 'Weather API key is not configured'}

@patch('main.requests.get')
def test_successful_response(mock_get, client):
    # Test a successful response from the weather API
    os.environ['WEATHER_API_KEY'] = 'test_api_key'  # Set a dummy API key
    mock_response = {
        'location': {'name': 'Test City'},
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
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    response = client.get('/forecast?zip=12345')
    assert response.status_code == 200
    assert 'Weather Forecast for Test City' in response.data.decode()
    assert '<td>2023-01-01</td>' in response.data.decode()
    assert '<td>Sunny</td>' in response.data.decode()

@patch('main.requests.get')
def test_api_error_response(mock_get, client):
    # Test the behavior when the weather API raises an exception
    os.environ['WEATHER_API_KEY'] = 'test_api_key'  # Set a dummy API key
    mock_get.side_effect = Exception('API error')

    response = client.get('/forecast?zip=12345')
    assert response.status_code == 500
    assert response.json == {'error': 'API error'}

@patch('main.requests.get')
def test_cli_user_agent(mock_get, client):
    # Test the response for a CLI user agent
    os.environ['WEATHER_API_KEY'] = 'test_api_key'  # Set a dummy API key
    mock_response = {
        'location': {'name': 'Test City'},
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
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    headers = {'User-Agent': 'curl/7.68.0'}
    response = client.get('/forecast?zip=12345', headers=headers)
    assert response.status_code == 200
    assert response.is_json
    assert response.json['location']['name'] == 'Test City'

@patch('main.requests.get')
def test_browser_user_agent(mock_get, client):
    # Test the response for a browser user agent
    os.environ['WEATHER_API_KEY'] = 'test_api_key'  # Set a dummy API key
    mock_response = {
        'location': {'name': 'Test City'},
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
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = client.get('/forecast?zip=12345', headers=headers)
    assert response.status_code == 200
    assert not response.is_json
    assert 'Weather Forecast for Test City' in response.data.decode()
    assert '<td>2023-01-01</td>' in response.data.decode()
    assert '<td>Sunny</td>' in response.data.decode()