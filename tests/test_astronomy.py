"""
Tests for astronomy features module.
"""

import pytest
from datetime import datetime, timedelta
from services.astronomy_features import (
    get_moon_phase_emoji,
    calculate_daylight_duration,
    process_astronomy_day,
    get_astronomy_data,
    enrich_with_astronomy
)


class TestMoonPhaseEmoji:
    """Test moon phase emoji mapping."""
    
    def test_new_moon(self):
        assert get_moon_phase_emoji("New Moon") == "🌑"
    
    def test_full_moon(self):
        assert get_moon_phase_emoji("Full Moon") == "🌕"
    
    def test_first_quarter(self):
        assert get_moon_phase_emoji("First Quarter") == "🌓"
    
    def test_waxing_crescent(self):
        assert get_moon_phase_emoji("Waxing Crescent") == "🌒"
    
    def test_waning_gibbous(self):
        assert get_moon_phase_emoji("Waning Gibbous") == "🌖"
    
    def test_case_insensitive(self):
        assert get_moon_phase_emoji("FULL MOON") == "🌕"
        assert get_moon_phase_emoji("new moon") == "🌑"
    
    def test_unknown_phase(self):
        assert get_moon_phase_emoji("Unknown Phase") == "🌙"
    
    def test_empty_phase(self):
        assert get_moon_phase_emoji("") == "🌙"
    
    def test_none_phase(self):
        assert get_moon_phase_emoji(None) == "🌙"


class TestDaylightDuration:
    """Test daylight duration calculation."""
    
    def test_normal_calculation(self):
        result = calculate_daylight_duration("06:30 AM", "05:45 PM")
        assert result == "11h 15m"
    
    def test_long_day(self):
        result = calculate_daylight_duration("05:00 AM", "09:00 PM")
        assert result == "16h 0m"
    
    def test_short_day(self):
        result = calculate_daylight_duration("08:00 AM", "04:30 PM")
        assert result == "8h 30m"
    
    def test_noon_times(self):
        result = calculate_daylight_duration("12:00 PM", "11:59 PM")
        assert result == "11h 59m"
    
    def test_midnight_crossing(self):
        # This shouldn't happen in real data, but test edge case
        result = calculate_daylight_duration("11:00 PM", "01:00 AM")
        assert result == "2h 0m"
    
    def test_empty_sunrise(self):
        result = calculate_daylight_duration("", "05:45 PM")
        assert result is None
    
    def test_empty_sunset(self):
        result = calculate_daylight_duration("06:30 AM", "")
        assert result is None
    
    def test_none_inputs(self):
        result = calculate_daylight_duration(None, None)
        assert result is None
    
    def test_invalid_format(self):
        result = calculate_daylight_duration("6:30", "17:45")
        assert result is None


class TestProcessAstronomyDay:
    """Test processing astronomy data for a single day."""
    
    def test_complete_data(self):
        day_data = {
            'date': '2024-01-15',
            'astro': {
                'sunrise': '07:30 AM',
                'sunset': '05:15 PM',
                'moonrise': '08:45 PM',
                'moonset': '09:30 AM',
                'moon_phase': 'First Quarter',
                'moon_illumination': '50'
            }
        }
        
        result = process_astronomy_day(day_data, is_current_day=True)
        
        assert result['date'] == '2024-01-15'
        assert result['is_current_day'] is True
        assert result['sunrise'] == '07:30 AM'
        assert result['sunset'] == '05:15 PM'
        assert result['moonrise'] == '08:45 PM'
        assert result['moonset'] == '09:30 AM'
        assert result['has_moonrise'] is True
        assert result['has_moonset'] is True
        assert result['moon_phase'] == 'First Quarter'
        assert result['moon_phase_emoji'] == '🌓'
        assert result['moon_illumination'] == '50'
        assert result['daylight_duration'] == '9h 45m'
    
    def test_no_moonrise(self):
        day_data = {
            'date': '2024-06-15',
            'astro': {
                'sunrise': '04:30 AM',
                'sunset': '09:45 PM',
                'moonrise': 'No moonrise',
                'moonset': '02:30 PM',
                'moon_phase': 'Full Moon',
                'moon_illumination': '100'
            }
        }
        
        result = process_astronomy_day(day_data)
        
        assert result['has_moonrise'] is False
        assert result['has_moonset'] is True
    
    def test_no_moonset(self):
        day_data = {
            'date': '2024-12-20',
            'astro': {
                'sunrise': '08:00 AM',
                'sunset': '03:30 PM',
                'moonrise': '10:00 AM',
                'moonset': 'No moonset',
                'moon_phase': 'Waning Crescent',
                'moon_illumination': '25'
            }
        }
        
        result = process_astronomy_day(day_data)
        
        assert result['has_moonrise'] is True
        assert result['has_moonset'] is False
    
    def test_missing_astro_data(self):
        day_data = {
            'date': '2024-01-15'
        }
        
        result = process_astronomy_day(day_data)
        
        assert result['date'] == '2024-01-15'
        assert result['sunrise'] == ''
        assert result['sunset'] == ''
        assert result['daylight_duration'] is None


class TestGetAstronomyData:
    """Test extracting astronomy data from weather forecast."""
    
    def test_valid_forecast_data(self):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        weather_data = {
            'forecast': {
                'forecastday': [
                    {
                        'date': today.strftime('%Y-%m-%d'),
                        'astro': {
                            'sunrise': '07:00 AM',
                            'sunset': '05:30 PM',
                            'moonrise': '09:00 PM',
                            'moonset': '10:00 AM',
                            'moon_phase': 'New Moon',
                            'moon_illumination': '5'
                        }
                    },
                    {
                        'date': tomorrow.strftime('%Y-%m-%d'),
                        'astro': {
                            'sunrise': '07:01 AM',
                            'sunset': '05:31 PM',
                            'moonrise': '09:30 PM',
                            'moonset': '10:30 AM',
                            'moon_phase': 'Waxing Crescent',
                            'moon_illumination': '10'
                        }
                    }
                ]
            }
        }
        
        result = get_astronomy_data(weather_data, include_current_day=True)
        
        assert len(result) == 2
        assert result[0]['is_current_day'] is True
        assert result[1]['is_current_day'] is False
    
    def test_exclude_current_day(self):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        weather_data = {
            'forecast': {
                'forecastday': [
                    {
                        'date': today.strftime('%Y-%m-%d'),
                        'astro': {'sunrise': '07:00 AM', 'sunset': '05:30 PM'}
                    },
                    {
                        'date': tomorrow.strftime('%Y-%m-%d'),
                        'astro': {'sunrise': '07:01 AM', 'sunset': '05:31 PM'}
                    }
                ]
            }
        }
        
        result = get_astronomy_data(weather_data, include_current_day=False)
        
        assert len(result) == 1
        assert result[0]['is_current_day'] is False
    
    def test_empty_weather_data(self):
        result = get_astronomy_data(None)
        assert result == []
    
    def test_no_forecast(self):
        weather_data = {'location': {'name': 'Test'}}
        result = get_astronomy_data(weather_data)
        assert result == []


class TestEnrichWithAstronomy:
    """Test enriching weather data with astronomy information."""
    
    def test_enrich_complete_data(self):
        today = datetime.now().date()
        future_dates = [today + timedelta(days=i) for i in range(1, 6)]
        
        weather_data = {
            'location': {'name': 'Test City'},
            'forecast': {
                'forecastday': [
                    {
                        'date': today.strftime('%Y-%m-%d'),
                        'astro': {
                            'sunrise': '07:00 AM',
                            'sunset': '05:30 PM',
                            'moonrise': '09:00 PM',
                            'moonset': '10:00 AM',
                            'moon_phase': 'Full Moon',
                            'moon_illumination': '98'
                        }
                    }
                ] + [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'astro': {
                            'sunrise': '07:00 AM',
                            'sunset': '05:30 PM',
                            'moonrise': '09:00 PM',
                            'moonset': '10:00 AM',
                            'moon_phase': 'Waning Gibbous',
                            'moon_illumination': '90'
                        }
                    }
                    for date in future_dates
                ]
            }
        }
        
        result = enrich_with_astronomy(weather_data)
        
        assert 'astronomy_info' in result
        assert result['astronomy_info']['is_current_day'] is True
        assert result['astronomy_info']['moon_phase'] == 'Full Moon'
        
        assert 'astronomy_forecast' in result
        assert len(result['astronomy_forecast']) == 5
        assert all(not day['is_current_day'] for day in result['astronomy_forecast'])
    
    def test_enrich_none_data(self):
        result = enrich_with_astronomy(None)
        assert result is None
    
    def test_enrich_preserves_other_data(self):
        weather_data = {
            'location': {'name': 'Test'},
            'current': {'temp_c': 20},
            'forecast': {'forecastday': []}
        }
        
        result = enrich_with_astronomy(weather_data)
        
        assert result['location'] == {'name': 'Test'}
        assert result['current'] == {'temp_c': 20}
