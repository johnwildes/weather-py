"""
Chat blueprint for AI assistant integration.

This module handles chat-related routes, integrating with Azure OpenAI
for GPT-powered weather assistant functionality.
"""

from flask import Blueprint, request, jsonify, Response, stream_with_context
import os
import json
import logging
from typing import Generator
from openai import AzureOpenAI

# Configure logging for chat module
logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

# Configuration constants
MAX_RESPONSE_TOKENS = 500  # Maximum tokens for chat responses
RESPONSE_TEMPERATURE = 0.7  # Temperature for response generation

# Azure OpenAI client singleton
_azure_client = None


def get_azure_client():
    """Get or create Azure OpenAI client singleton."""
    global _azure_client
    if _azure_client is None:
        api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')
        
        if api_key and endpoint:
            _azure_client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
    return _azure_client


def get_deployment_name():
    """Get the Azure OpenAI deployment name from environment."""
    return os.getenv('AZURE_OPENAI_DEPLOYMENT', '')


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

You have access to current weather data and forecasts for the user's currently displayed city. 
When answering questions, be conversational, friendly, and informative. Use the weather data provided 
to give accurate, context-aware responses.

Guidelines:
- Answer weather-related questions using the provided data
- When the user asks "is this typical?" or similar questions, refer to the current conditions shown
- Explain weather patterns and phenomena when relevant
- Provide helpful suggestions (e.g., clothing recommendations, activity planning)
- If asked about locations not in the context, politely indicate you don't have current data for them
- Be concise but thorough in your explanations
- Use a friendly, conversational tone"""

    # Add current weather context (the location the user is viewing)
    if context and context.get('currentWeather'):
        cw = context['currentWeather']
        loc = cw.get('location', {})
        current = cw.get('current', {})
        
        location_name = loc.get('name', 'Unknown')
        region = loc.get('region', '')
        country = loc.get('country', '')
        full_location = ', '.join(filter(None, [location_name, region, country]))
        
        base_prompt += f"\n\n=== CURRENTLY DISPLAYED WEATHER ===\n"
        base_prompt += f"Location: {full_location}\n"
        
        if current:
            condition = current.get('condition', {}).get('text', 'N/A')
            temp_c = current.get('temp_c', 'N/A')
            temp_f = current.get('temp_f', 'N/A')
            feels_c = current.get('feelslike_c', 'N/A')
            feels_f = current.get('feelslike_f', 'N/A')
            humidity = current.get('humidity', 'N/A')
            wind_kph = current.get('wind_kph', 'N/A')
            wind_mph = current.get('wind_mph', 'N/A')
            vis_km = current.get('vis_km', 'N/A')
            pressure = current.get('pressure_mb', 'N/A')
            uv = current.get('uv', 'N/A')
            
            base_prompt += f"Condition: {condition}\n"
            base_prompt += f"Temperature: {temp_c}°C ({temp_f}°F)\n"
            base_prompt += f"Feels like: {feels_c}°C ({feels_f}°F)\n"
            base_prompt += f"Humidity: {humidity}%\n"
            base_prompt += f"Wind: {wind_kph} km/h ({wind_mph} mph)\n"
            base_prompt += f"Visibility: {vis_km} km\n"
            base_prompt += f"Pressure: {pressure} mb\n"
            base_prompt += f"UV Index: {uv}\n"
        
        # Add UV safety info if available
        if cw.get('uv_info'):
            uv_info = cw['uv_info']
            base_prompt += f"\nUV Safety: {uv_info.get('level', 'N/A')} - {uv_info.get('recommendation', '')}\n"
        
        # Add air quality info if available
        if cw.get('aqi_info'):
            aqi = cw['aqi_info']
            base_prompt += f"\nAir Quality: {aqi.get('level', 'N/A')}"
            if aqi.get('pm2_5'):
                base_prompt += f" (PM2.5: {aqi['pm2_5']} µg/m³)"
            base_prompt += f"\nAir Quality Guidance: {aqi.get('guidance', '')}\n"
        
        # Add weather alerts if any
        if cw.get('alerts') and len(cw['alerts']) > 0:
            base_prompt += f"\n⚠️ ACTIVE WEATHER ALERTS:\n"
            for alert in cw['alerts'][:3]:  # Limit to 3 alerts
                base_prompt += f"- {alert.get('headline', 'Weather Alert')}: {alert.get('severity', 'Unknown severity')}\n"
        
        # Add forecast summary
        forecast = cw.get('forecast', {})
        if forecast and forecast.get('forecastday'):
            base_prompt += f"\n10-Day Forecast Summary:\n"
            for day in forecast['forecastday'][:5]:  # First 5 days
                date = day.get('date', 'N/A')
                day_data = day.get('day', {})
                max_c = day_data.get('maxtemp_c', 'N/A')
                min_c = day_data.get('mintemp_c', 'N/A')
                cond = day_data.get('condition', {}).get('text', 'N/A')
                rain_chance = day_data.get('daily_chance_of_rain', 0)
                base_prompt += f"- {date}: {cond}, High {max_c}°C, Low {min_c}°C"
                if rain_chance > 0:
                    base_prompt += f", {rain_chance}% chance of rain"
                base_prompt += "\n"

    # Also add other recent locations for context
    if context and context.get('locations'):
        other_locations = [loc for loc in context['locations'] 
                          if loc.get('location') != context.get('currentLocation')]
        if other_locations:
            base_prompt += "\n\nOther recently searched locations:\n"
            for loc_info in other_locations[:3]:
                location = loc_info.get('displayName', loc_info.get('location', 'Unknown'))
                weather = loc_info.get('weather', {})
                current = weather.get('current', {})
                if current:
                    temp = current.get('temp_c', 'N/A')
                    condition = current.get('condition', {}).get('text', 'N/A')
                    base_prompt += f"- {location}: {temp}°C, {condition}\n"

    return base_prompt


def stream_azure_response(message: str, context: dict) -> Generator[str, None, None]:
    """
    Stream response from Azure OpenAI.
    
    Args:
        message: User's message
        context: Weather context from recent searches
        
    Yields:
        SSE formatted data chunks
    """
    client = get_azure_client()
    deployment = get_deployment_name()
    
    logger.info(f"Chat request - Message: {message[:50]}...")
    logger.info(f"Config - Client configured: {client is not None}, Deployment: {deployment}")
    
    if not client:
        logger.error("Azure OpenAI client not configured")
        yield 'data: {"error": "Azure OpenAI not configured. Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your .env file."}\n\n'
        yield 'data: [DONE]\n\n'
        return

    if not deployment:
        logger.error("Azure OpenAI deployment not configured")
        yield 'data: {"error": "Azure OpenAI deployment not configured. Please set AZURE_OPENAI_DEPLOYMENT in your .env file."}\n\n'
        yield 'data: [DONE]\n\n'
        return

    try:
        logger.info(f"Sending streaming request to deployment: {deployment}")
        
        # Use Azure OpenAI SDK for streaming
        # Note: Some models only support default temperature (1) and max_completion_tokens
        stream = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": build_system_prompt(context)
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            stream=True,
            max_completion_tokens=MAX_RESPONSE_TOKENS
        )
        
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield f'data: {{"content": {json.dumps(delta.content)}}}\n\n'

        yield 'data: [DONE]\n\n'
        logger.info("Stream completed successfully")
        
    except Exception as e:
        error_msg = f"Azure OpenAI error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        yield f'data: {{"error": {json.dumps(error_msg)}}}\n\n'
        yield 'data: [DONE]\n\n'


@chat_bp.route('/config', methods=['GET'])
def get_chat_config():
    """
    Get chat configuration (API key check only, not the actual key).
    
    Returns:
        JSON with config status
    """
    client = get_azure_client()
    deployment = get_deployment_name()
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    
    return jsonify({
        'configured': client is not None and bool(deployment),
        'endpoint': endpoint,
        'deployment': deployment
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
            stream_with_context(stream_azure_response(message, context)),
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
