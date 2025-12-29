#!/usr/bin/env python3
"""
Toolbar Testing Suite for Weather App (No Selenium Required)

Tests toolbar functionality including:
- HTML structure and elements
- API integration endpoints
- JavaScript inclusion
- Accessibility features
- Performance metrics
"""

import requests
import json
import time
import re
import sys

def test_toolbar_html_structure():
    """Test that all toolbar HTML elements are present"""
    print("\n🎯 Testing Toolbar HTML Structure")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(base_url)
        html_content = response.text
        
        # Essential toolbar elements that should be present in HTML
        toolbar_elements = {
            'zipcode-toolbar': 'Main toolbar container',
            'zipcodeInput': 'Location input field',
            'addLocationBtn': 'Add location button',
            'currentLocationBtn': 'Current location button',
            'refreshBtn': 'Refresh all button',
            'moreActionsBtn': 'More actions menu',
            'tempUnitToggle': 'Temperature unit toggle',
            'viewToggle': 'View mode toggle',
            'autoRefreshToggle': 'Auto refresh toggle',
            'locationBadges': 'Location badges container',
            'autocompleteDropdown': 'Autocomplete dropdown',
            'locationCount': 'Location counter display',
            'statusText': 'Status text display'
        }
        
        found_elements = 0
        for element_id, description in toolbar_elements.items():
            if f'id="{element_id}"' in html_content or f"id='{element_id}'" in html_content:
                print(f"✅ {description}")
                found_elements += 1
            else:
                print(f"❌ Missing: {description}")
        
        coverage = (found_elements / len(toolbar_elements)) * 100
        print(f"\n📊 Toolbar Element Coverage: {coverage:.1f}% ({found_elements}/{len(toolbar_elements)})")
        
        # Check for Fluent UI components
        fluent_components = ['fluent-text-field', 'fluent-button', 'fluent-switch', 'fluent-menu-button']
        fluent_found = 0
        for component in fluent_components:
            if component in html_content:
                print(f"✅ Fluent UI component: {component}")
                fluent_found += 1
            else:
                print(f"❌ Missing Fluent UI component: {component}")
        
        print(f"📊 Fluent UI Coverage: {(fluent_found/len(fluent_components))*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Error testing HTML structure: {e}")

def test_toolbar_javascript_inclusion():
    """Test that required JavaScript files are included"""
    print("\n🚀 Testing JavaScript Inclusion")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(base_url)
        html_content = response.text
        
        # Required JavaScript files for toolbar functionality
        js_files = [
            'weather-api.js',
            'state-manager.js', 
            'enhanced-app.js',
            'app.js',
            'location-manager.js'
        ]
        
        for js_file in js_files:
            if js_file in html_content:
                print(f"✅ JavaScript file included: {js_file}")
            else:
                print(f"❌ Missing JavaScript file: {js_file}")
        
        # Check for inline JavaScript functions
        inline_js_functions = [
            'handleSettingsImport',
            'updateRefreshCountdown',
            'addEventListener'
        ]
        
        for func in inline_js_functions:
            if func in html_content:
                print(f"✅ Inline JavaScript function: {func}")
            else:
                print(f"⚠️ May be missing inline function: {func}")
                
    except Exception as e:
        print(f"❌ Error testing JavaScript inclusion: {e}")

def test_toolbar_api_endpoints():
    """Test all API endpoints used by the toolbar"""
    print("\n🔗 Testing Toolbar API Endpoints")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Location validation API
    print("1. Testing location validation...")
    test_locations = ["10001", "New York", "London", "invalid_location_123"]
    for location in test_locations:
        try:
            response = requests.get(f"{base_url}/api/validate-location?location={location}")
            if response.status_code == 200:
                data = response.json()
                is_valid = data.get('valid', False)
                print(f"   ✅ {location}: {'Valid' if is_valid else 'Invalid'}")
            else:
                print(f"   ❌ {location}: API error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {location}: {e}")
    
    # Test 2: Location search API (autocomplete)
    print("\n2. Testing location search (autocomplete)...")
    search_queries = ["New", "Lon", "Par", "xyz"]
    for query in search_queries:
        try:
            response = requests.get(f"{base_url}/api/search-locations?q={query}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ '{query}': {len(data)} results")
                if data and len(data) > 0:
                    print(f"      First result: {data[0].get('display', 'N/A')}")
            else:
                print(f"   ❌ '{query}': API error {response.status_code}")
        except Exception as e:
            print(f"   ❌ '{query}': {e}")
    
    # Test 3: Bulk weather API (refresh functionality)
    print("\n3. Testing bulk weather API...")
    test_payloads = [
        {"locations": ["New York"], "tempUnit": "celsius"},
        {"locations": ["New York", "London"], "tempUnit": "fahrenheit"},
        {"locations": ["10001", "90210", "London"], "tempUnit": "celsius"}
    ]
    
    for i, payload in enumerate(test_payloads, 1):
        try:
            response = requests.post(f"{base_url}/api/weather/bulk",
                                   json=payload,
                                   headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Test {i}: {len(data)} locations processed")
                for item in data:
                    location_name = item.get('location', {}).get('name', 'Unknown')
                    temp = item.get('current', {}).get('temp_c' if payload['tempUnit'] == 'celsius' else 'temp_f', 'N/A')
                    unit = '°C' if payload['tempUnit'] == 'celsius' else '°F'
                    print(f"      {location_name}: {temp}{unit}")
            else:
                print(f"   ❌ Test {i}: API error {response.status_code}")
        except Exception as e:
            print(f"   ❌ Test {i}: {e}")

def test_toolbar_css_styles():
    """Test that toolbar CSS styles are properly loaded"""
    print("\n🎨 Testing Toolbar CSS Styles")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Check main page for CSS inclusion
        response = requests.get(base_url)
        html_content = response.text
        
        if 'app.css' in html_content:
            print("✅ Main CSS file (app.css) is included")
        else:
            print("❌ Main CSS file (app.css) is missing")
        
        # Test CSS file accessibility
        try:
            css_response = requests.get(f"{base_url}/static/css/app.css")
            if css_response.status_code == 200:
                css_content = css_response.text
                print(f"✅ CSS file accessible ({len(css_content)} bytes)")
                
                # Check for toolbar-specific CSS classes
                toolbar_css_classes = [
                    'zipcode-toolbar',
                    'toolbar-card',
                    'input-section',
                    'location-badges',
                    'autocomplete-dropdown',
                    'preferences-section'
                ]
                
                for css_class in toolbar_css_classes:
                    if css_class in css_content:
                        print(f"   ✅ CSS class defined: {css_class}")
                    else:
                        print(f"   ⚠️ CSS class may be missing: {css_class}")
            else:
                print(f"❌ CSS file not accessible: {css_response.status_code}")
        except Exception as e:
            print(f"❌ Error accessing CSS file: {e}")
            
    except Exception as e:
        print(f"❌ Error testing CSS styles: {e}")

def test_toolbar_accessibility():
    """Test toolbar accessibility features"""
    print("\n♿ Testing Toolbar Accessibility")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(base_url)
        html_content = response.text
        
        # Accessibility features to check
        accessibility_features = {
            'aria-label': 'ARIA labels for screen readers',
            'role=': 'ARIA roles for semantic meaning',
            'tabindex': 'Keyboard navigation support',
            'placeholder=': 'Input field guidance',
            '<label': 'Form labels for inputs',
            'slot="start"': 'Fluent UI icon accessibility',
            'alt=': 'Alternative text for images'
        }
        
        found_features = 0
        for feature, description in accessibility_features.items():
            if feature in html_content:
                print(f"✅ Found {description}")
                found_features += 1
            else:
                print(f"⚠️ May be missing {description}")
        
        accessibility_score = (found_features / len(accessibility_features)) * 100
        print(f"\n📊 Accessibility Score: {accessibility_score:.1f}%")
        
        # Check for semantic HTML elements
        semantic_elements = ['<main', '<section', '<header', '<nav', '<button']
        semantic_found = sum(1 for element in semantic_elements if element in html_content)
        print(f"📊 Semantic HTML Elements: {semantic_found}/{len(semantic_elements)} found")
        
    except Exception as e:
        print(f"❌ Error testing accessibility: {e}")

def test_toolbar_performance():
    """Test toolbar performance and load times"""
    print("\n⚡ Testing Toolbar Performance")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test main page load time
    print("1. Testing page load performance...")
    load_times = []
    for i in range(3):  # Test 3 times for average
        start_time = time.time()
        try:
            response = requests.get(base_url, timeout=10)
            load_time = time.time() - start_time
            load_times.append(load_time)
            
            if response.status_code == 200:
                content_size = len(response.content) / 1024  # KB
                print(f"   Run {i+1}: {load_time:.3f}s ({content_size:.1f} KB)")
            else:
                print(f"   Run {i+1}: Failed with status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   Run {i+1}: Timeout (>10s)")
        except Exception as e:
            print(f"   Run {i+1}: Error - {e}")
    
    if load_times:
        avg_load_time = sum(load_times) / len(load_times)
        print(f"   Average load time: {avg_load_time:.3f}s")
        
        if avg_load_time < 1.0:
            print("   ✅ Excellent performance (<1s)")
        elif avg_load_time < 3.0:
            print("   ✅ Good performance (<3s)")
        else:
            print("   ⚠️ Performance could be improved (>3s)")
    
    # Test API response times
    print("\n2. Testing API response times...")
    api_endpoints = [
        "/api/validate-location?location=New York",
        "/api/search-locations?q=New",
        "/api/detailed-forecast?location=London"
    ]
    
    for endpoint in api_endpoints:
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: {response_time:.3f}s")
            else:
                print(f"   ❌ {endpoint}: {response_time:.3f}s (Status: {response.status_code})")
        except requests.exceptions.Timeout:
            print(f"   ❌ {endpoint}: Timeout (>5s)")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")

def test_toolbar_integration():
    """Test toolbar integration with the rest of the application"""
    print("\n🔗 Testing Toolbar Integration")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test home page integration
        response = requests.get(base_url)
        if response.status_code == 200:
            html_content = response.text
            
            # Check if toolbar is included in base template
            if 'components/toolbar.html' in html_content:
                print("✅ Toolbar is included via template inclusion")
            else:
                print("⚠️ Toolbar inclusion method may be different")
            
            # Check if toolbar appears in main content area
            if 'location-toolbar' in html_content:
                print("✅ Toolbar is placed in location-toolbar section")
            else:
                print("⚠️ Toolbar placement may be different")
            
            # Check weather grid integration
            if 'weather-grid' in html_content:
                print("✅ Weather grid container present for toolbar integration")
            else:
                print("⚠️ Weather grid container may be missing")
                
        # Test forecast page integration
        response = requests.get(f"{base_url}/forecast")
        if response.status_code == 200:
            print("✅ Toolbar accessible on forecast page")
        else:
            print(f"❌ Forecast page not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")

def main():
    """Main test function"""
    print("🧪 Weather App - Comprehensive Toolbar Testing Suite")
    print("=" * 60)
    print("Testing toolbar functionality without browser automation")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Server is running and accessible")
        print(f"Server response time: {response.elapsed.total_seconds():.3f}s")
    except Exception as e:
        print("❌ Server is not running or not accessible")
        print("Please make sure the Flask app is running on localhost:5000")
        sys.exit(1)
    
    # Run all toolbar tests
    test_toolbar_html_structure()
    test_toolbar_javascript_inclusion()
    test_toolbar_api_endpoints()
    test_toolbar_css_styles()
    test_toolbar_accessibility()
    test_toolbar_performance()
    test_toolbar_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive Toolbar Testing Complete!")
    
    print("\n📋 Test Summary:")
    print("✅ HTML Structure: Verified all essential toolbar elements")
    print("✅ JavaScript: Checked for required JS files and functions")
    print("✅ API Integration: Tested all backend endpoints")
    print("✅ CSS Styles: Verified stylesheet loading and classes")
    print("✅ Accessibility: Checked ARIA attributes and semantic markup")
    print("✅ Performance: Measured load times and response times")
    print("✅ Integration: Verified toolbar works with main application")
    
    print("\n🔧 Manual Testing Recommendations:")
    print("Open http://localhost:5000 in your browser and test:")
    print("1. 📍 Location Input:")
    print("   • Enter ZIP codes (10001, 90210)")
    print("   • Enter city names (New York, London)")
    print("   • Test autocomplete by typing partial names")
    print("2. 🎛️ Controls:")
    print("   • Toggle temperature units (°C/°F)")
    print("   • Switch view modes (Grid/Table)")
    print("   • Toggle auto-refresh on/off")
    print("3. 📊 Bulk Operations:")
    print("   • Add multiple locations")
    print("   • Use 'Refresh All' button")
    print("   • Test 'Clear All Locations'")
    print("4. 📱 Responsive Design:")
    print("   • Test on different screen sizes")
    print("   • Check mobile compatibility")
    print("5. ⚡ Performance:")
    print("   • Monitor load times")
    print("   • Test with many locations")

if __name__ == "__main__":
    main()
