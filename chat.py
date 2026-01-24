"""
Chat blueprint for AI assistant integration.

This module handles chat-related routes, integrating with Microsoft Foundry
for GPT-5.2 powered weather assistant functionality.
"""

from flask import Blueprint, request, jsonify, Response, stream_with_context
import os
import json
import requests
from typing import Generator

chat_bp = Blueprint('chat', __name__)


def get_foundry_config():
    """Get Microsoft Foundry configuration from environment."""
    return {
        'apiKey': os.getenv('FOUNDRY_API_KEY', ''),
        'endpoint': os.getenv('FOUNDRY_ENDPOINT', 'https://api.foundry.microsoft.com/v1/chat/completions')
    }


def build_system_prompt(context: dict) -> str:
    """
    Build a blended system prompt for the weather assistant.
    
    Combines weather-specific knowledge with general chat capabilities.
    
    Args:
        context: Dictionary containing current weather data and recent locations
        
    Returns:
        System prompt string
    """
    base_prompt = """You are a helpful weather assistant with expertise in meteorology and weather patterns. 
Your role is to help users understand weather conditions, forecasts, and provide insights about the weather 
in their searched locations.

You have access to current weather data and forecasts for the user's recently searched cities. 
When answering questions, be conversational, friendly, and informative. Use the weather data provided 
to give accurate, context-aware responses.

Guidelines:
- Answer weather-related questions using the provided data
- Explain weather patterns and phenomena when relevant
- Provide helpful suggestions (e.g., clothing recommendations, activity planning)
- If asked about locations not in the context, politely indicate you don't have current data for them
- Be concise but thorough in your explanations
- Use a friendly, conversational tone"""

    # Add current context
    if context and context.get('locations'):
        location_data = "\n\nCurrent Weather Context:\n"
        
        for loc_info in context['locations'][:5]:  # Last 5 searched cities
            location = loc_info.get('displayName', loc_info.get('location', 'Unknown'))
            weather = loc_info.get('weather', {})
            current = weather.get('current', {})
            
            if current:
                temp = current.get('temp_c', 'N/A')
                condition = current.get('condition', {}).get('text', 'N/A')
                location_data += f"\n- {location}: {temp}°C, {condition}"
        
        if context.get('currentLocation'):
            location_data += f"\n\nCurrently viewing: {context['currentLocation']}"
        
        base_prompt += location_data

    return base_prompt


def stream_foundry_response(message: str, context: dict) -> Generator[str, None, None]:
    """
    Stream response from Microsoft Foundry GPT-5.2.
    
    Args:
        message: User's message
        context: Weather context from recent searches
        
    Yields:
        SSE formatted data chunks
    """
    config = get_foundry_config()
    
    if not config['apiKey']:
        yield 'data: {"error": "Foundry API key not configured"}\n\n'
        yield 'data: [DONE]\n\n'
        return

    # Build the request payload
    payload = {
        "model": "gpt-5.2",
        "messages": [
            {
                "role": "system",
                "content": build_system_prompt(context)
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 500
    }

    headers = {
        'Authorization': f'Bearer {config["apiKey"]}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            config['endpoint'],
            headers=headers,
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            yield f'data: {{"error": "Foundry API error: {response.status_code}"}}\n\n'
            yield 'data: [DONE]\n\n'
            return

        # Stream the response
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = line_str[6:]  # Remove 'data: ' prefix
                    
                    if data == '[DONE]':
                        yield 'data: [DONE]\n\n'
                        break
                    
                    try:
                        parsed = json.loads(data)
                        if 'choices' in parsed and len(parsed['choices']) > 0:
                            delta = parsed['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            
                            if content:
                                yield f'data: {{"content": {json.dumps(content)}}}\n\n'
                    except json.JSONDecodeError:
                        continue

        yield 'data: [DONE]\n\n'
        
    except requests.exceptions.RequestException as e:
        yield f'data: {{"error": "Network error: {str(e)}"}}\n\n'
        yield 'data: [DONE]\n\n'
    except Exception as e:
        yield f'data: {{"error": "Unexpected error: {str(e)}"}}\n\n'
        yield 'data: [DONE]\n\n'


@chat_bp.route('/config', methods=['GET'])
def get_chat_config():
    """
    Get chat configuration (API key check only, not the actual key).
    
    Returns:
        JSON with config status
    """
    config = get_foundry_config()
    
    return jsonify({
        'apiKey': bool(config['apiKey']),  # Just indicate if it's configured
        'endpoint': config['endpoint']
    })


@chat_bp.route('/completions', methods=['POST'])
def chat_completions():
    """
    Handle chat completion requests with streaming support.
    
    Request body:
        {
            "message": "user message",
            "context": {"locations": [...], "currentLocation": "..."},
            "stream": true/false
        }
    
    Returns:
        Streaming response with SSE format or JSON response
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message']
    context = data.get('context', {})
    should_stream = data.get('stream', True)
    
    if should_stream:
        # Return streaming response
        return Response(
            stream_with_context(stream_foundry_response(message, context)),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        # Non-streaming response (fallback)
        # Note: This would need to be implemented to collect full response
        return jsonify({'error': 'Non-streaming mode not implemented'}), 501
