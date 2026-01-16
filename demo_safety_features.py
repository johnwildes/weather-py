#!/usr/bin/env python3
"""
Weather Safety Features - Interactive Demo

This script demonstrates the safety features with real-world examples
and shows how the code works with actual weather data.

Run: python demo_safety_features.py
"""

from safety_features_implementation import (
    UVIndexInfo, 
    AirQualityInfo, 
    WeatherAlert,
    SafetyWeatherData
)
from datetime import datetime, timedelta
import json


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_uv_index():
    """Demonstrate UV Index classification and recommendations."""
    print_section("FEATURE 1: UV INDEX")
    
    print("UV Index provides sun safety guidance based on WHO standards.\n")
    
    # Test different UV values
    test_cases = [
        (1.5, "Early morning", "Boston in April"),
        (4.0, "Mid-morning", "Chicago in June"),
        (6.5, "Noon", "Los Angeles in July"),
        (9.0, "Midday", "Phoenix in August"),
        (12.0, "Peak hours", "Australia in summer")
    ]
    
    for uv_value, time_of_day, location in test_cases:
        uv_info = UVIndexInfo.from_uv_value(uv_value)
        
        print(f"📍 {location} ({time_of_day})")
        print(f"   UV Index: {uv_info.value} {uv_info.icon}")
        print(f"   Level: {uv_info.level.value.replace('_', ' ').upper()}")
        print(f"   Color: {uv_info.color}")
        print(f"   ⚠️  Recommendation: {uv_info.recommendation}")
        print()
    
    print("💡 Key Points:")
    print("   • UV varies by time of day, season, latitude, and altitude")
    print("   • Protection needed at UV 3+ (moderate and above)")
    print("   • Skin damage can occur in 15-20 minutes at high UV")
    print("   • Children and fair-skinned people need extra protection")


def demo_air_quality():
    """Demonstrate Air Quality Index classification and health guidance."""
    print_section("FEATURE 2: AIR QUALITY INDEX (AQI)")
    
    print("AQI provides respiratory health guidance based on EPA standards.\n")
    
    # Test different AQI levels with realistic scenarios
    test_cases = [
        (1, "Clear day", "Rural Montana", {"pm2_5": 8.5, "pm10": 15.2}),
        (2, "Typical urban day", "Seattle", {"pm2_5": 25.3, "pm10": 35.8}),
        (3, "Smoggy day", "Los Angeles", {"pm2_5": 55.7, "pm10": 82.1}),
        (4, "Wildfire smoke", "Portland during fires", {"pm2_5": 125.4, "pm10": 180.3}),
        (5, "Heavy pollution", "Delhi in winter", {"pm2_5": 225.8, "pm10": 350.2}),
        (6, "Hazardous event", "California wildfire zone", {"pm2_5": 425.5, "pm10": 580.7})
    ]
    
    for epa_index, scenario, location, pollutants in test_cases:
        air_data = {
            'us-epa-index': epa_index,
            'pm2_5': pollutants['pm2_5'],
            'pm10': pollutants['pm10']
        }
        aqi_info = AirQualityInfo.from_api_data(air_data)
        
        print(f"📍 {location} - {scenario}")
        print(f"   EPA Index: {aqi_info.epa_index} {aqi_info.icon}")
        print(f"   Level: {aqi_info.level.value.replace('_', ' ').upper()}")
        print(f"   Color: {aqi_info.color}")
        print(f"   PM2.5: {aqi_info.pm2_5:.1f} μg/m³ | PM10: {aqi_info.pm10:.1f} μg/m³")
        print(f"   🏥 Health: {aqi_info.health_message}")
        print(f"   👥 Sensitive Groups: {aqi_info.sensitive_groups}")
        print()
    
    print("💡 Key Points:")
    print("   • PM2.5 is most dangerous (penetrates deep into lungs)")
    print("   • 25+ million Americans have asthma")
    print("   • Children, elderly, and people with respiratory/heart disease most at risk")
    print("   • Wildfire smoke can travel hundreds of miles")


def demo_weather_alerts():
    """Demonstrate Weather Alert classification and safety instructions."""
    print_section("FEATURE 3: SEVERE WEATHER ALERTS")
    
    print("Weather Alerts provide life-safety warnings from NOAA/NWS.\n")
    
    # Create realistic alert scenarios
    alerts_scenarios = [
        {
            'headline': 'Tornado Warning issued for Travis County',
            'event': 'Tornado Warning',
            'severity': 'Extreme',
            'urgency': 'Immediate',
            'areas': 'Travis County, Texas',
            'desc': 'A confirmed tornado is on the ground moving northeast at 40 mph. This is a life-threatening situation.',
            'instruction': 'Take shelter immediately in a basement or interior room on lowest floor. Put as many walls as possible between you and the outside.',
            'effective': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(hours=1)).isoformat()
        },
        {
            'headline': 'Excessive Heat Warning',
            'event': 'Excessive Heat',
            'severity': 'Extreme',
            'urgency': 'Expected',
            'areas': 'Maricopa County, Arizona',
            'desc': 'Dangerously hot conditions with temperatures up to 118 degrees expected. Heat index values up to 120.',
            'instruction': 'Drink plenty of fluids, stay in an air-conditioned room, stay out of the sun, and check up on relatives and neighbors.',
            'effective': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(hours=12)).isoformat()
        },
        {
            'headline': 'Flash Flood Warning',
            'event': 'Flash Flooding',
            'severity': 'Severe',
            'urgency': 'Immediate',
            'areas': 'Harris County, Texas',
            'desc': 'Flash flooding caused by thunderstorms is imminent or occurring. Up to 6 inches of rain has fallen.',
            'instruction': 'Move to higher ground immediately. Do not attempt to drive through flooded roads. Turn around, don\'t drown.',
            'effective': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'expires': (datetime.now() + timedelta(hours=3)).isoformat()
        },
        {
            'headline': 'Winter Storm Warning',
            'event': 'Winter Storm',
            'severity': 'Moderate',
            'urgency': 'Expected',
            'areas': 'Denver Metro Area',
            'desc': 'Heavy snow expected. Total snow accumulations of 8 to 14 inches. Winds gusting as high as 45 mph.',
            'instruction': 'Avoid travel if possible. If you must travel, keep an extra flashlight, food, and water in your vehicle.',
            'effective': (datetime.now() + timedelta(hours=6)).isoformat(),
            'expires': (datetime.now() + timedelta(hours=24)).isoformat()
        }
    ]
    
    for alert_data in alerts_scenarios:
        alert = WeatherAlert.from_api_data(alert_data)
        
        print(f"{alert.icon} {alert.headline}")
        print(f"   Event: {alert.event}")
        print(f"   Severity: {alert.severity.value.upper()} | Urgency: {alert.urgency.value.upper()}")
        print(f"   Areas: {alert.areas}")
        print(f"   Active: {'YES ✓' if alert.is_active() else 'NO (future or past)'}")
        print(f"   📝 Description: {alert.description}")
        print(f"   🚨 Action Required: {alert.instruction}")
        print(f"   ⏰ Expires: {alert.expires.strftime('%Y-%m-%d %H:%M')}")
        print()
    
    print("💡 Key Points:")
    print("   • Alerts are issued by National Weather Service (official government warnings)")
    print("   • IMMEDIATE urgency means act now (tornado, flash flood)")
    print("   • EXPECTED urgency means prepare (heat wave, winter storm)")
    print("   • Always follow safety instructions")
    print("   • Multiple alerts can be active simultaneously")


def demo_integrated_safety_data():
    """Demonstrate integrated safety data for a complete weather response."""
    print_section("INTEGRATED SAFETY DATA")
    
    print("Example: Complete weather data with all safety features\n")
    
    # Simulate a complete weather API response
    weather_response = {
        'location': {
            'name': 'Phoenix',
            'region': 'Arizona',
            'country': 'USA',
            'lat': 33.45,
            'lon': -112.07
        },
        'current': {
            'temp_c': 43.0,
            'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
            'humidity': 15,
            'wind_kph': 12.0,
            'uv': 11.0,  # Extreme UV
            'air_quality': {
                'us-epa-index': 3,  # Unhealthy for sensitive groups
                'pm2_5': 55.2,
                'pm10': 82.3
            }
        },
        'alerts': {
            'alert': [
                {
                    'headline': 'Excessive Heat Warning',
                    'event': 'Excessive Heat',
                    'severity': 'Extreme',
                    'urgency': 'Expected',
                    'areas': 'Phoenix Metro Area',
                    'desc': 'Dangerously hot conditions with temperatures up to 118°F expected.',
                    'instruction': 'Drink fluids, stay indoors in AC, check on relatives.',
                    'effective': datetime.now().isoformat(),
                    'expires': (datetime.now() + timedelta(hours=8)).isoformat()
                }
            ]
        }
    }
    
    # Extract safety data
    safety_data = SafetyWeatherData.from_weather_api_response(weather_response)
    
    print("📍 Location: Phoenix, Arizona")
    print(f"🌡️  Temperature: {weather_response['current']['temp_c']}°C")
    print()
    
    # UV Index
    if safety_data.uv_index:
        print(f"☀️  UV Index: {safety_data.uv_index.value} {safety_data.uv_index.icon}")
        print(f"    Level: {safety_data.uv_index.level.value.upper()}")
        print(f"    {safety_data.uv_index.recommendation}")
        print()
    
    # Air Quality
    if safety_data.air_quality:
        print(f"🌫️  Air Quality: {safety_data.air_quality.level.value.replace('_', ' ').title()} {safety_data.air_quality.icon}")
        print(f"    {safety_data.air_quality.health_message}")
        print(f"    {safety_data.air_quality.sensitive_groups}")
        print()
    
    # Alerts
    if safety_data.alerts:
        print(f"🚨 Active Alerts: {len(safety_data.get_active_alerts())}")
        for alert in safety_data.get_active_alerts():
            print(f"    {alert.icon} {alert.headline}")
            print(f"    Action: {alert.instruction}")
        print()
    
    # Safety Summary
    summary = safety_data.get_safety_summary()
    print(f"⚠️  Safety Summary:")
    print(f"    Priority Level: {summary['priority_label'].upper()} ({summary['priority']}/3)")
    print(f"    Concerns: {', '.join(summary['concerns']) if summary['concerns'] else 'None'}")
    print(f"    Has Safety Concerns: {'YES' if summary['has_concerns'] else 'NO'}")
    print()
    
    # JSON output example
    print("📄 JSON API Response:")
    print(json.dumps(safety_data.to_dict(), indent=2, default=str))


def demo_real_world_scenarios():
    """Show safety data for different real-world weather scenarios."""
    print_section("REAL-WORLD SCENARIOS")
    
    scenarios = [
        {
            'name': 'Perfect Day',
            'location': 'San Francisco, CA',
            'uv': 3.0,
            'aqi': 1,
            'alerts': []
        },
        {
            'name': 'High UV Day',
            'location': 'Miami, FL',
            'uv': 10.0,
            'aqi': 2,
            'alerts': []
        },
        {
            'name': 'Wildfire Smoke',
            'location': 'Portland, OR',
            'uv': 2.0,
            'aqi': 5,
            'alerts': []
        },
        {
            'name': 'Severe Weather',
            'location': 'Oklahoma City, OK',
            'uv': 5.0,
            'aqi': 2,
            'alerts': ['Tornado Watch']
        },
        {
            'name': 'Extreme Heat',
            'location': 'Phoenix, AZ',
            'uv': 11.0,
            'aqi': 3,
            'alerts': ['Excessive Heat Warning']
        }
    ]
    
    for scenario in scenarios:
        uv_info = UVIndexInfo.from_uv_value(scenario['uv'])
        aqi_info = AirQualityInfo.from_api_data({'us-epa-index': scenario['aqi']})
        
        print(f"📍 {scenario['name']} - {scenario['location']}")
        print(f"   UV: {uv_info.icon} {scenario['uv']} ({uv_info.level.value})")
        print(f"   AQI: {aqi_info.icon} {aqi_info.level.value.replace('_', ' ')}")
        print(f"   Alerts: {', '.join(scenario['alerts']) if scenario['alerts'] else 'None'}")
        
        # Determine overall safety
        if scenario['uv'] >= 8 or scenario['aqi'] >= 4 or scenario['alerts']:
            print(f"   ⚠️  Overall: USE CAUTION")
        else:
            print(f"   ✅ Overall: CONDITIONS OK")
        print()


def main():
    """Run all demonstrations."""
    print("\n" + "🌤️  " * 15)
    print("      WEATHER SAFETY FEATURES - INTERACTIVE DEMONSTRATION")
    print("🌤️  " * 15)
    
    print("\nThis demo shows how the safety features work with real-world data.")
    print("All values are based on official WHO, EPA, and NWS standards.")
    
    # Run each demo
    demo_uv_index()
    demo_air_quality()
    demo_weather_alerts()
    demo_integrated_safety_data()
    demo_real_world_scenarios()
    
    # Summary
    print_section("SUMMARY")
    print("✅ UV Index - Implemented with WHO 5-level scale")
    print("✅ Air Quality - Implemented with EPA 6-level AQI")
    print("✅ Weather Alerts - Implemented with NWS CAP protocol")
    print()
    print("📊 All features:")
    print("   • Use data already fetched from WeatherAPI")
    print("   • Follow official safety standards")
    print("   • Provide actionable recommendations")
    print("   • Support JSON serialization for APIs")
    print("   • Include visual indicators (colors, icons)")
    print()
    print("🚀 Ready for production integration!")
    print("   See README_IMPLEMENTATION.md for integration guide")
    print()


if __name__ == '__main__':
    main()
