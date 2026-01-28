"""
Flask Integration Example for Safety Features

This file demonstrates how to integrate the safety features into the existing
Flask weather application. It includes:
1. New API routes
2. Template filters
3. Integration with existing weather service
4. Frontend display recommendations

Add this to your Flask app to enable safety features display.
"""

from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from safety_features_implementation import (
    SafetyWeatherData,
    UVIndexInfo,
    AirQualityInfo,
    WeatherAlert
)

# Create a new blueprint for safety features
safety_bp = Blueprint('safety', __name__)


# ============================================================================
# API ROUTES
# ============================================================================

@safety_bp.route('/api/safety-info', methods=['GET'])
def get_safety_info():
    """
    Get comprehensive safety information for a location.
    
    Query Parameters:
        location: Location query (city, ZIP, coordinates)
        
    Returns:
        JSON with UV index, air quality, and weather alerts
    """
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter required'}), 400
    
    # Import weather service (using existing pattern from forecast.py)
    from forecast import get_weather_service
    service = get_weather_service()
    
    try:
        # Get weather data (already includes AQI and alerts from API)
        weather_data = service.get_weather_data(location)
        
        if not weather_data:
            return jsonify({'error': 'Unable to fetch weather data for location'}), 404
        
        # Extract safety information
        safety_data = SafetyWeatherData.from_weather_api_response(weather_data)
        
        return jsonify({
            'location': weather_data.get('location', {}),
            'safety': safety_data.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@safety_bp.route('/api/uv-index', methods=['GET'])
def get_uv_index():
    """
    Get UV index information for a location.
    
    Query Parameters:
        location: Location query
        
    Returns:
        JSON with UV index and safety recommendations
    """
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter required'}), 400
    
    from forecast import get_weather_service
    service = get_weather_service()
    
    try:
        weather_data = service.get_current_weather(location)
        
        if not weather_data or 'current' not in weather_data:
            return jsonify({'error': 'Unable to fetch UV data'}), 404
        
        uv_value = weather_data['current'].get('uv', 0)
        uv_info = UVIndexInfo.from_uv_value(uv_value)
        
        return jsonify({
            'location': weather_data.get('location', {}),
            'uv_index': uv_info.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@safety_bp.route('/api/air-quality', methods=['GET'])
def get_air_quality():
    """
    Get air quality information for a location.
    
    Query Parameters:
        location: Location query
        
    Returns:
        JSON with AQI and health recommendations
    """
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter required'}), 400
    
    from forecast import get_weather_service
    service = get_weather_service()
    
    try:
        weather_data = service.get_current_weather(location)
        
        if not weather_data or 'current' not in weather_data:
            return jsonify({'error': 'Unable to fetch air quality data'}), 404
        
        air_quality_data = weather_data['current'].get('air_quality', {})
        
        if not air_quality_data:
            return jsonify({
                'location': weather_data.get('location', {}),
                'air_quality': None,
                'message': 'Air quality data not available for this location'
            }), 200
        
        aqi_info = AirQualityInfo.from_api_data(air_quality_data)
        
        return jsonify({
            'location': weather_data.get('location', {}),
            'air_quality': aqi_info.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@safety_bp.route('/api/weather-alerts', methods=['GET'])
def get_weather_alerts():
    """
    Get active weather alerts for a location.
    
    Query Parameters:
        location: Location query
        
    Returns:
        JSON with list of active weather alerts
    """
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter required'}), 400
    
    from forecast import get_weather_service
    service = get_weather_service()
    
    try:
        weather_data = service.get_weather_data(location)
        
        if not weather_data:
            return jsonify({'error': 'Unable to fetch weather alerts'}), 404
        
        alerts_data = weather_data.get('alerts', {}).get('alert', [])
        alerts = [WeatherAlert.from_api_data(alert) for alert in alerts_data]
        active_alerts = [alert for alert in alerts if alert.is_active()]
        
        return jsonify({
            'location': weather_data.get('location', {}),
            'alerts': [alert.to_dict() for alert in alerts],
            'active_alerts': [alert.to_dict() for alert in active_alerts],
            'alert_count': len(alerts),
            'active_alert_count': len(active_alerts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# TEMPLATE FILTERS
# ============================================================================

def register_safety_filters(app):
    """
    Register Jinja2 template filters for safety features.
    
    Call this function in main.py after creating the Flask app:
        register_safety_filters(app)
    """
    
    @app.template_filter('uv_level')
    def uv_level_filter(uv_value):
        """Get UV level classification from value."""
        if uv_value is None:
            return 'unknown'
        uv_info = UVIndexInfo.from_uv_value(uv_value)
        return uv_info.level.value.replace('_', ' ').title()
    
    @app.template_filter('uv_color')
    def uv_color_filter(uv_value):
        """Get UV color code from value."""
        if uv_value is None:
            return '#808080'
        uv_info = UVIndexInfo.from_uv_value(uv_value)
        return uv_info.color
    
    @app.template_filter('uv_recommendation')
    def uv_recommendation_filter(uv_value):
        """Get UV safety recommendation from value."""
        if uv_value is None:
            return 'UV data not available'
        uv_info = UVIndexInfo.from_uv_value(uv_value)
        return uv_info.recommendation
    
    @app.template_filter('aqi_level')
    def aqi_level_filter(epa_index):
        """Get AQI level from EPA index."""
        if epa_index is None:
            return 'unknown'
        aqi_info = AirQualityInfo.from_api_data({'us-epa-index': epa_index})
        return aqi_info.level.value.replace('_', ' ').title()
    
    @app.template_filter('aqi_color')
    def aqi_color_filter(epa_index):
        """Get AQI color from EPA index."""
        if epa_index is None:
            return '#808080'
        aqi_info = AirQualityInfo.from_api_data({'us-epa-index': epa_index})
        return aqi_info.color
    
    @app.template_filter('aqi_health_message')
    def aqi_health_message_filter(epa_index):
        """Get AQI health message from EPA index."""
        if epa_index is None:
            return 'Air quality data not available'
        aqi_info = AirQualityInfo.from_api_data({'us-epa-index': epa_index})
        return aqi_info.health_message


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

"""
TO INTEGRATE INTO YOUR EXISTING FLASK APP:

1. In main.py, add the blueprint registration:
   
   from flask_safety_integration import safety_bp, register_safety_filters
   
   app.register_blueprint(safety_bp, url_prefix='/safety')
   register_safety_filters(app)

2. Modify home.py to include safety data:

   @home_bp.route('', methods=['GET'])
   def home():
       service = get_weather_service()
       location = request.args.get('location')
       
       weather_data = None
       safety_data = None
       error_message = None
       
       if location:
           try:
               weather_data = service.get_detailed_forecast(location, days=10)
               
               # ADD THIS: Extract safety information
               if weather_data:
                   from safety_features_implementation import SafetyWeatherData
                   safety_data = SafetyWeatherData.from_weather_api_response(weather_data)
                   
           except Exception as e:
               logger.error(f"Error: {e}", exc_info=True)
               error_message = f"Unable to fetch weather data"
       
       return render_template(
           'home.html',
           weather_data=weather_data,
           safety_data=safety_data,  # ADD THIS
           error_message=error_message
       )

3. Update templates/home.html to display safety features.
   Add this section after the current weather card:

   {% if safety_data %}
   <!-- Safety Information Section -->
   <div class="safety-section">
       <fluent-card class="safety-card">
           <h3 class="safety-title">Safety Information</h3>
           
           <!-- UV Index -->
           {% if safety_data.uv_index %}
           <div class="safety-item uv-info">
               <div class="safety-header">
                   <span class="safety-icon">☀️</span>
                   <h4>UV Index</h4>
               </div>
               <div class="safety-badge" style="background-color: {{ safety_data.uv_index.color }}; color: white;">
                   <span class="badge-value">{{ safety_data.uv_index.value|round(0)|int }}</span>
                   <span class="badge-level">{{ safety_data.uv_index.level.value|replace('_', ' ')|title }}</span>
               </div>
               <p class="safety-recommendation">{{ safety_data.uv_index.recommendation }}</p>
           </div>
           {% endif %}
           
           <!-- Air Quality -->
           {% if safety_data.air_quality %}
           <div class="safety-item aqi-info">
               <div class="safety-header">
                   <span class="safety-icon">🌫️</span>
                   <h4>Air Quality</h4>
               </div>
               <div class="safety-badge" style="background-color: {{ safety_data.air_quality.color }}; 
                    color: {% if safety_data.air_quality.epa_index >= 4 %}white{% else %}black{% endif %};">
                   <span class="badge-level">{{ safety_data.air_quality.level.value|replace('_', ' ')|title }}</span>
               </div>
               <p class="safety-health-message">{{ safety_data.air_quality.health_message }}</p>
               <p class="safety-sensitive-groups"><em>{{ safety_data.air_quality.sensitive_groups }}</em></p>
           </div>
           {% endif %}
           
           <!-- Weather Alerts -->
           {% if safety_data.alerts %}
           <div class="safety-item alerts-info">
               <div class="safety-header">
                   <span class="safety-icon">⚠️</span>
                   <h4>Weather Alerts ({{ safety_data.get_active_alerts()|length }})</h4>
               </div>
               {% for alert in safety_data.get_active_alerts() %}
               <div class="alert-card" style="border-left: 4px solid {{ alert.color }};">
                   <div class="alert-headline">
                       <span>{{ alert.icon }}</span>
                       <strong>{{ alert.headline }}</strong>
                   </div>
                   <p class="alert-event">{{ alert.event }}</p>
                   <p class="alert-description">{{ alert.description }}</p>
                   {% if alert.instruction %}
                   <p class="alert-instruction"><strong>What to do:</strong> {{ alert.instruction }}</p>
                   {% endif %}
                   <p class="alert-expires"><small>Expires: {{ alert.expires.strftime('%b %d, %I:%M %p') }}</small></p>
               </div>
               {% endfor %}
           </div>
           {% endif %}
       </fluent-card>
   </div>
   {% endif %}

4. Add CSS styling to static/style.css (or create it):

   /* Safety Section Styling */
   .safety-section {
       margin-top: 20px;
   }
   
   .safety-card {
       padding: 20px;
   }
   
   .safety-title {
       font-size: 1.5rem;
       margin-bottom: 20px;
       color: #323130;
   }
   
   .safety-item {
       margin-bottom: 24px;
       padding-bottom: 24px;
       border-bottom: 1px solid #edebe9;
   }
   
   .safety-item:last-child {
       border-bottom: none;
   }
   
   .safety-header {
       display: flex;
       align-items: center;
       gap: 8px;
       margin-bottom: 12px;
   }
   
   .safety-icon {
       font-size: 1.5rem;
   }
   
   .safety-badge {
       display: inline-flex;
       align-items: center;
       gap: 8px;
       padding: 8px 16px;
       border-radius: 4px;
       font-weight: 600;
       margin-bottom: 12px;
   }
   
   .badge-value {
       font-size: 1.2rem;
   }
   
   .safety-recommendation,
   .safety-health-message {
       font-size: 0.95rem;
       line-height: 1.5;
       margin: 8px 0;
   }
   
   .safety-sensitive-groups {
       font-size: 0.9rem;
       color: #605e5c;
       font-style: italic;
       margin-top: 4px;
   }
   
   .alert-card {
       background-color: #fff4ce;
       padding: 12px;
       margin: 8px 0;
       border-radius: 4px;
   }
   
   .alert-headline {
       display: flex;
       align-items: center;
       gap: 8px;
       font-size: 1.1rem;
       margin-bottom: 8px;
   }
   
   .alert-event {
       font-weight: 600;
       color: #d13438;
       margin: 4px 0;
   }
   
   .alert-description,
   .alert-instruction {
       font-size: 0.9rem;
       line-height: 1.4;
       margin: 8px 0;
   }
   
   .alert-expires {
       font-size: 0.85rem;
       color: #605e5c;
       margin-top: 8px;
   }

5. Test the integration:
   
   # Start your Flask app
   python main.py
   
   # Test API endpoints
   curl "http://localhost:5000/safety/api/safety-info?location=London"
   curl "http://localhost:5000/safety/api/uv-index?location=London"
   curl "http://localhost:5000/safety/api/air-quality?location=London"
   curl "http://localhost:5000/safety/api/weather-alerts?location=London"
   
   # Visit in browser
   http://localhost:5000/?location=London

6. Optional: Add daily forecast safety info
   
   Modify the forecast loop in home.html to show UV for each day:
   
   {% for day in weather_data.forecast.forecastday %}
   <div class="forecast-day-row">
       <!-- existing content -->
       <div class="day-uv">
           {% if day.day.uv %}
           <span class="uv-indicator" style="background-color: {{ day.day.uv|uv_color }};">
               UV {{ day.day.uv|round(0)|int }}
           </span>
           {% endif %}
       </div>
   </div>
   {% endfor %}
"""


# ============================================================================
# EXAMPLE: Enhanced Weather Data Response
# ============================================================================

def example_enhanced_response():
    """
    Example of what the enhanced API response looks like with safety data.
    """
    return {
        "location": {
            "name": "London",
            "region": "City of London, Greater London",
            "country": "United Kingdom"
        },
        "current": {
            "temp_c": 22.0,
            "condition": {"text": "Partly cloudy"},
            "humidity": 65,
            "wind_kph": 15.0,
            "vis_km": 10.0,
            # Existing data...
        },
        "safety": {
            "uv_index": {
                "value": 6.0,
                "level": "high",
                "color": "#F85900",
                "recommendation": "Protection essential. Seek shade during midday.",
                "icon": "🟠"
            },
            "air_quality": {
                "epa_index": 2,
                "level": "moderate",
                "color": "#FFFF00",
                "health_message": "Air quality is acceptable.",
                "sensitive_groups": "Unusually sensitive people should limit prolonged outdoor exertion.",
                "icon": "🟡",
                "pm2_5": 12.5,
                "pm10": 20.3
            },
            "alerts": [],
            "active_alerts": [],
            "safety_summary": {
                "priority": 1,
                "priority_label": "Caution",
                "concerns": ["High UV radiation"],
                "has_concerns": True,
                "active_alerts_count": 0
            }
        }
    }


if __name__ == '__main__':
    print("Flask Safety Integration Module")
    print("=" * 50)
    print("\nThis module provides:")
    print("1. API routes for safety data (/safety/api/...)")
    print("2. Template filters for Jinja2")
    print("3. Integration examples")
    print("\nSee docstrings for integration instructions.")
    print("\nExample enhanced response structure:")
    import json
    print(json.dumps(example_enhanced_response(), indent=2))
