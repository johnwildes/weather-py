"""
Tests for chat agent functionality
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from chat import chat_bp, build_system_prompt, get_foundry_config


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
    assert 'apiKey' in data
    assert 'endpoint' in data
    assert isinstance(data['apiKey'], bool)


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
        'locations': [
            {
                'location': '10001',
                'displayName': 'New York, NY',
                'weather': {
                    'current': {
                        'temp_c': 15,
                        'condition': {'text': 'Partly cloudy'}
                    }
                }
            }
        ],
        'currentLocation': 'New York, NY'
    }
    
    prompt = build_system_prompt(context)
    assert 'New York, NY' in prompt
    assert '15' in prompt
    assert 'Partly cloudy' in prompt


def test_get_foundry_config():
    """Test getting Foundry configuration from environment."""
    with patch.dict('os.environ', {
        'FOUNDRY_API_KEY': 'test_key',
        'FOUNDRY_ENDPOINT': 'https://test.endpoint.com'
    }):
        config = get_foundry_config()
        assert config['apiKey'] == 'test_key'
        assert config['endpoint'] == 'https://test.endpoint.com'


def test_get_foundry_config_defaults():
    """Test Foundry config with default values."""
    with patch.dict('os.environ', {}, clear=True):
        config = get_foundry_config()
        assert config['apiKey'] == ''
        assert 'foundry.microsoft.com' in config['endpoint']


@patch('chat.requests.post')
def test_chat_completions_streaming(mock_post, client):
    """Test chat completions with streaming."""
    # Mock the streaming response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
        b'data: {"choices": [{"delta": {"content": " there"}}]}',
        b'data: [DONE]'
    ]
    mock_post.return_value = mock_response
    
    with patch.dict('os.environ', {'FOUNDRY_API_KEY': 'test_key'}):
        response = client.post(
            '/api/chat/completions',
            data=json.dumps({
                'message': 'What is the weather?',
                'context': {},
                'stream': True
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'


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
