#!/bin/bash
# Quick start script for the Weather App with Fluent UI

echo "🌤️  Weather App - Fluent UI Development Setup"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please create a .env file with the following variables:"
    echo ""
    echo "WEATHER_API_KEY=your_weather_api_key_here"
    echo "DEFAULT_ZIP_CODE=10001"
    echo "FLASK_DEBUG=true"
    echo ""
    echo "You can get a free API key from: https://www.weatherapi.com/"
    echo ""
    read -p "Press Enter to continue once you've created the .env file..."
fi

# Check if API key is set
if [ -f ".env" ]; then
    if grep -q "WEATHER_API_KEY=your_weather_api_key" .env; then
        echo "⚠️  Please update your WEATHER_API_KEY in the .env file"
        read -p "Press Enter to continue once you've updated the API key..."
    fi
fi

echo ""
echo "🚀 Starting the application..."
echo "The app will be available at: http://localhost:5000"
echo ""
echo "Features to test:"
echo "• Home page with weather map"
echo "• Multi-location forecast page"
echo "• Location search and management"
echo "• Fluent UI components and interactions"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python main.py
