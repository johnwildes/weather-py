#!/usr/bin/env python3
"""
Test script for the new Fluent UI Weather App
"""
import requests
import json
import sys

def test_api_endpoints():
    """Test the new API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Weather App API Endpoints")
    print("=" * 50)
    
    # Test 1: Location validation
    print("\n1. Testing location validation...")
    try:
        response = requests.get(f"{base_url}/api/validate-location?location=New York")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Location validation: {data.get('valid', False)}")
        else:
            print(f"❌ Location validation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Location validation error: {e}")
    
    # Test 2: Location search with enhanced results
    print("\n2. Testing location search...")
    try:
        response = requests.get(f"{base_url}/api/search-locations?q=London")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Location search found {len(data)} results")
            if data:
                print(f"   First result: {data[0].get('display', 'N/A')}")
                print(f"   Search includes: {', '.join([item.get('name', 'N/A') for item in data[:3]])}")
        else:
            print(f"❌ Location search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Location search error: {e}")
    
    # Test 3: Bulk weather data with enhanced info
    print("\n3. Testing bulk weather data...")
    try:
        payload = {
            "locations": ["New York", "London", "Tokyo"],
            "tempUnit": "celsius"
        }
        response = requests.post(f"{base_url}/api/weather/bulk", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bulk weather data: {len(data)} locations")
            for item in data:
                location_name = item.get('location', {}).get('name', 'Unknown')
                temp = item.get('current', {}).get('temp_c', 'N/A')
                condition = item.get('current', {}).get('condition', {}).get('text', 'N/A')
                alerts = len(item.get('alerts', {}).get('alert', []))
                print(f"   {location_name}: {temp}°C, {condition}, {alerts} alerts")
        else:
            print(f"❌ Bulk weather data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Bulk weather data error: {e}")
    
    # Test 4: Enhanced detailed forecast
    print("\n4. Testing detailed forecast...")
    try:
        response = requests.get(f"{base_url}/api/detailed-forecast?location=Paris")
        if response.status_code == 200:
            data = response.json()
            forecast_days = len(data.get('forecast', {}).get('forecastday', []))
            alerts = len(data.get('alerts', {}).get('alert', []))
            aqi = data.get('current', {}).get('air_quality', {}).get('us_epa_index', 'N/A')
            print(f"✅ Detailed forecast: {forecast_days} days, {alerts} alerts, AQI: {aqi}")
        else:
            print(f"❌ Detailed forecast failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Detailed forecast error: {e}")
    
    # Test 5: Hourly forecast (new feature)
    print("\n5. Testing hourly forecast...")
    try:
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = requests.get(f"{base_url}/api/hourly-forecast?location=Miami&date={tomorrow}")
        if response.status_code == 200:
            data = response.json()
            hourly_count = len(data.get('hourly', []))
            location_name = data.get('location', {}).get('name', 'Unknown')
            print(f"✅ Hourly forecast: {hourly_count} hours for {location_name} on {tomorrow}")
            if hourly_count > 0:
                first_hour = data['hourly'][0]
                temp = first_hour.get('temp_c', 'N/A')
                condition = first_hour.get('condition', {}).get('text', 'N/A')
                print(f"   First hour: {temp}°C, {condition}")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': 'Unknown error'}
            print(f"❌ Hourly forecast failed: {response.status_code} - {error_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Hourly forecast error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")

def test_web_pages():
    """Test the web pages"""
    base_url = "http://localhost:5000"
    
    print("\n🌐 Testing Web Pages")
    print("=" * 50)
    
    # Test home page
    print("\n1. Testing home page...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Home page loads successfully")
            if "Weather Forecast" in response.text:
                print("✅ Page contains expected content")
            else:
                print("⚠️ Page content may be incomplete")
        else:
            print(f"❌ Home page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Home page error: {e}")
    
    # Test forecast page
    print("\n2. Testing forecast page...")
    try:
        response = requests.get(f"{base_url}/forecast")
        if response.status_code == 200:
            print("✅ Forecast page loads successfully")
            if "weather-grid" in response.text or "empty-state" in response.text:
                print("✅ Page contains expected UI elements")
            else:
                print("⚠️ Page content may be incomplete")
        else:
            print(f"❌ Forecast page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Forecast page error: {e}")
    
    # Test forecast with ZIP code
    print("\n3. Testing forecast with ZIP code...")
    try:
        response = requests.get(f"{base_url}/forecast?zip=10001")
        if response.status_code == 200:
            print("✅ Forecast with ZIP code loads successfully")
        else:
            print(f"❌ Forecast with ZIP code failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Forecast with ZIP code error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Web Page Testing Complete!")

def main():
    """Main test function"""
    print("🚀 Weather App - Fluent UI Testing Suite")
    print("========================================")
    print("Make sure the Flask app is running on localhost:5000")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Server is running")
    except Exception as e:
        print("❌ Server is not running or not accessible")
        print("Please start the Flask app with: python main.py")
        sys.exit(1)
    
    # Run tests
    test_web_pages()
    test_api_endpoints()
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Try adding multiple locations using the toolbar")
    print("3. Test the different view modes and settings")

if __name__ == "__main__":
    main()
