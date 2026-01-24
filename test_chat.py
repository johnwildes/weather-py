"""
Tests for chat agent functionality
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from chat import chat_bp, build_system_prompt


@pytest.fixture
def client():
    """Create a test client for the chat blueprint."""
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_get_chat_config(client):
    """Test getting chat configuration."""
    response = client.get('/api/chat/config')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'configured' in data
    assert 'endpoint' in data
    assert 'deployment' in data


def test_chat_completions_missing_message(client):
    """Test chat completions endpoint with missing message."""
    response = client.post(
        '/api/chat/completions',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data


def test_build_system_prompt_no_context():
    """Test building system prompt without context."""
    prompt = build_system_prompt({})
    assert 'weather assistant' in prompt.lower()
    assert 'meteorology' in prompt.lower()


def test_build_system_prompt_with_context():
    """Test building system prompt with weather context."""
    context = {
        'currentWeather': {
            'location': {
                'name': 'New York',
                'region': 'NY',
                'country': 'USA'
            },
            'current': {
                'temp_c': 15,
                'temp_f': 59,
                'feelslike_c': 13,
                'feelslike_f': 55,
                'humidity': 65,
                'wind_kph': 10,
                'wind_mph': 6,
                'vis_km': 10,
                'pressure_mb': 1015,
                'uv': 3,
                'condition': {'text': 'Partly cloudy'}
            }
        },
        'currentLocation': 'New York',
        'locations': []
    }
    
    prompt = build_system_prompt(context)
    assert 'New York' in prompt
    assert '15' in prompt
    assert 'Partly cloudy' in prompt
    assert 'CURRENTLY DISPLAYED WEATHER' in prompt


def test_build_system_prompt_with_full_context():
    """Test building system prompt with all context including UV and AQI."""
    context = {
        'currentWeather': {
            'location': {
                'name': 'Pensacola',
                'region': 'Florida',
                'country': 'USA'
            },
            'current': {
                'temp_c': 28,
                'temp_f': 82,
                'feelslike_c': 30,
                'feelslike_f': 86,
                'humidity': 75,
                'wind_kph': 15,
                'wind_mph': 9,
                'vis_km': 16,
                'pressure_mb': 1010,
                'uv': 8,
                'condition': {'text': 'Sunny'}
            },
            'uv_info': {
                'value': 8,
                'level': 'Very High',
                'recommendation': 'Wear sunscreen'
            },
            'aqi_info': {
                'level': 'Good',
                'pm2_5': 12.5,
                'guidance': 'Air quality is satisfactory'
            },
            'forecast': {
                'forecastday': [
                    {
                        'date': '2026-01-24',
                        'day': {
                            'maxtemp_c': 30,
                            'mintemp_c': 22,
                            'condition': {'text': 'Sunny'},
                            'daily_chance_of_rain': 10
                        }
                    }
                ]
            }
        },
        'currentLocation': 'Pensacola'
    }
    
    prompt = build_system_prompt(context)
    assert 'Pensacola' in prompt
    assert 'Florida' in prompt
    assert 'USA' in prompt
    assert '28' in prompt
    assert 'Sunny' in prompt
    assert 'UV Safety' in prompt
    assert 'Very High' in prompt
    assert 'Air Quality' in prompt
    assert 'Good' in prompt


def test_chat_completions_non_streaming(client):
    """Test that non-streaming mode returns 501."""
    response = client.post(
        '/api/chat/completions',
        data=json.dumps({
            'message': 'What is the weather?',
            'context': {},
            'stream': False
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 501
