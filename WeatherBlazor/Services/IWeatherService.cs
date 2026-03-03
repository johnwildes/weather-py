using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

public interface IWeatherService
{
    Task<WeatherViewModel?> GetWeatherAsync(string location, int days = 10);
    Task<List<SearchResult>> SearchLocationsAsync(string query, int limit = 10);
    Task<(bool IsValid, Location? LocationInfo)> ValidateLocationAsync(string location);
}
