using System.Text.Json;
using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

public class WeatherApiService : IWeatherService
{
    private const string BaseUrl = "https://api.weatherapi.com/v1";

    private readonly HttpClient _http;
    private readonly string _apiKey;
    private readonly ILogger<WeatherApiService> _logger;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public WeatherApiService(HttpClient http, IConfiguration config, ILogger<WeatherApiService> logger)
    {
        _http   = http;
        _logger = logger;
        _apiKey = config["WeatherApiKey"] ?? Environment.GetEnvironmentVariable("WEATHER_API_KEY") ?? "";

        if (string.IsNullOrEmpty(_apiKey))
            _logger.LogWarning("WEATHER_API_KEY is not configured. Weather data will not be available.");
    }

    public async Task<WeatherViewModel?> GetWeatherAsync(string location, int days = 10)
    {
        if (string.IsNullOrEmpty(_apiKey)) return null;

        try
        {
            var url = $"{BaseUrl}/forecast.json?key={_apiKey}&q={Uri.EscapeDataString(location)}&days={days}&aqi=yes&alerts=yes";
            var response = await _http.GetAsync(url);

            if (!response.IsSuccessStatusCode) return null;

            var json = await response.Content.ReadAsStringAsync();
            var apiResponse = JsonSerializer.Deserialize<WeatherApiResponse>(json, JsonOptions);

            if (apiResponse is null) return null;

            var vm = new WeatherViewModel
            {
                Location = apiResponse.Location,
                Current  = apiResponse.Current,
                Forecast = apiResponse.Forecast
            };

            // Enrich with safety features
            SafetyFeaturesService.Enrich(vm);
            SafetyFeaturesService.EnrichAlerts(vm, apiResponse.Alerts);

            // Enrich with astronomy from first forecast day
            AstronomyService.Enrich(vm);

            return vm;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error fetching weather for {Location}", location);
            return null;
        }
    }

    public async Task<List<SearchResult>> SearchLocationsAsync(string query, int limit = 10)
    {
        if (string.IsNullOrEmpty(_apiKey) || string.IsNullOrWhiteSpace(query) || query.Length < 2)
            return [];

        try
        {
            var url = $"{BaseUrl}/search.json?key={_apiKey}&q={Uri.EscapeDataString(query)}";
            var response = await _http.GetAsync(url);

            if (!response.IsSuccessStatusCode) return [];

            var json = await response.Content.ReadAsStringAsync();
            var results = JsonSerializer.Deserialize<List<SearchResult>>(json, JsonOptions);
            return results?.Take(limit).ToList() ?? [];
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching locations for {Query}", query);
            return [];
        }
    }

    public async Task<(bool IsValid, Location? LocationInfo)> ValidateLocationAsync(string location)
    {
        if (string.IsNullOrEmpty(_apiKey)) return (false, null);

        try
        {
            var url = $"{BaseUrl}/current.json?key={_apiKey}&q={Uri.EscapeDataString(location)}";
            var response = await _http.GetAsync(url);

            if (!response.IsSuccessStatusCode) return (false, null);

            var json = await response.Content.ReadAsStringAsync();
            var apiResponse = JsonSerializer.Deserialize<WeatherApiResponse>(json, JsonOptions);

            return apiResponse is not null ? (true, apiResponse.Location) : (false, null);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating location {Location}", location);
            return (false, null);
        }
    }
}
