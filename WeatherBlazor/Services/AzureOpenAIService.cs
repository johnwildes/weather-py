using System.Net;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

public class AzureOpenAIService : IAIService
{
    private const int MaxResponseTokens = 500;

    private readonly HttpClient _http;
    private readonly string _apiKey;
    private readonly string _endpoint;
    private readonly string _deployment;
    private readonly string _apiVersion;
    private readonly ILogger<AzureOpenAIService> _logger;

    public bool IsConfigured =>
        !string.IsNullOrEmpty(_apiKey) &&
        !string.IsNullOrEmpty(_endpoint) &&
        !string.IsNullOrEmpty(_deployment);

    public AzureOpenAIService(HttpClient http, IConfiguration config, ILogger<AzureOpenAIService> logger)
    {
        _http   = http;
        _logger = logger;

        _apiKey     = config["AzureOpenAI:ApiKey"]     ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY")     ?? "";
        _endpoint   = config["AzureOpenAI:Endpoint"]   ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")   ?? "";
        _deployment = config["AzureOpenAI:Deployment"] ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "";
        _apiVersion = config["AzureOpenAI:ApiVersion"] ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_API_VERSION") ?? "2024-10-21";

        if (!IsConfigured)
            _logger.LogWarning("Azure OpenAI is not configured. Chat assistant will not be available.");
    }

    public async IAsyncEnumerable<string> StreamChatAsync(
        string message,
        WeatherViewModel? weatherContext,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        if (!IsConfigured)
        {
            yield return "⚠️ The weather assistant is not configured. Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT environment variables.";
            yield break;
        }

        var url = $"{_endpoint.TrimEnd('/')}/openai/deployments/{WebUtility.UrlEncode(_deployment)}/chat/completions?api-version={_apiVersion}";
        var body = JsonSerializer.Serialize(new
        {
            messages = new[]
            {
                new { role = "system", content = BuildSystemPrompt(weatherContext) },
                new { role = "user",   content = message }
            },
            stream = true,
            max_completion_tokens = MaxResponseTokens
        });

        using var request = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = new StringContent(body, Encoding.UTF8, "application/json")
        };
        request.Headers.Add("api-key", _apiKey);

        HttpResponseMessage? response   = null;
        string?             connectErr = null;
        try
        {
            response = await _http.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, ct);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to reach Azure OpenAI endpoint");
            connectErr = $"⚠️ Connection error: {ex.Message}";
        }

        if (connectErr is not null)
        {
            yield return connectErr;
            yield break;
        }

        if (!response!.IsSuccessStatusCode)
        {
            var err = await response.Content.ReadAsStringAsync(ct);
            _logger.LogError("Azure OpenAI returned {Status}: {Body}", response.StatusCode, err);
            yield return $"⚠️ Azure OpenAI returned an error ({(int)response.StatusCode}). Please try again later.";
            yield break;
        }

        await using var stream = await response.Content.ReadAsStreamAsync(ct);
        using var reader       = new StreamReader(stream);

        while (true)
        {
            var line = await reader.ReadLineAsync(ct);
            if (line is null || ct.IsCancellationRequested) break;
            if (!line.StartsWith("data: ")) continue;

            var data = line[6..];
            if (data == "[DONE]") break;

            string? token;
            try
            {
                using var doc = JsonDocument.Parse(data);
                token = doc.RootElement
                    .GetProperty("choices")[0]
                    .GetProperty("delta")
                    .TryGetProperty("content", out var el)
                        ? el.GetString()
                        : null;
            }
            catch { continue; }

            if (!string.IsNullOrEmpty(token))
                yield return token;
        }
    }

    public static string BuildSystemPrompt(WeatherViewModel? vm)
    {
        var sb = new StringBuilder(
            """
            You are a helpful weather assistant with expertise in meteorology and weather patterns.
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
            - Use a friendly, conversational tone
            """);

        if (vm is null) return sb.ToString();

        var loc          = vm.Location;
        var cur          = vm.Current;
        var fullLocation = string.Join(", ", new[] { loc.Name, loc.Region, loc.Country }
                              .Where(s => !string.IsNullOrEmpty(s)));

        sb.AppendLine();
        sb.AppendLine("=== CURRENTLY DISPLAYED WEATHER ===");
        sb.AppendLine($"Location: {fullLocation}");
        sb.AppendLine($"Condition: {cur.Condition.Text}");
        sb.AppendLine($"Temperature: {cur.TempC}°C ({cur.TempF}°F)");
        sb.AppendLine($"Feels like: {cur.FeelsLikeC}°C ({cur.FeelsLikeF}°F)");
        sb.AppendLine($"Humidity: {cur.Humidity}%");
        sb.AppendLine($"Wind: {cur.WindKph} km/h ({cur.WindMph} mph)");
        sb.AppendLine($"Visibility: {cur.VisKm} km");
        sb.AppendLine($"Pressure: {cur.PressureMb} mb");
        sb.AppendLine($"UV Index: {cur.Uv}");

        if (vm.UvInfo is not null)
            sb.AppendLine($"\nUV Safety: {vm.UvInfo.Level} - {vm.UvInfo.Recommendation}");

        if (vm.AqiInfo is not null)
        {
            sb.Append($"\nAir Quality: {vm.AqiInfo.Level}");
            if (vm.AqiInfo.Pm25.HasValue)
                sb.Append($" (PM2.5: {vm.AqiInfo.Pm25:F1} µg/m³)");
            sb.AppendLine();
            sb.AppendLine($"Air Quality Guidance: {vm.AqiInfo.Guidance}");
        }

        if (vm.AlertsInfo.Count > 0)
        {
            sb.AppendLine("\n⚠️ ACTIVE WEATHER ALERTS:");
            foreach (var alert in vm.AlertsInfo.Take(3))
                sb.AppendLine($"- {alert.Headline}: {alert.Severity}");
        }

        if (vm.Forecast.ForecastDay.Count > 0)
        {
            sb.AppendLine("\n5-Day Forecast Summary:");
            foreach (var day in vm.Forecast.ForecastDay.Take(5))
            {
                sb.Append($"- {day.Date}: {day.Day.Condition.Text}, High {day.Day.MaxTempC}°C, Low {day.Day.MinTempC}°C");
                if (day.Day.ChanceOfRain > 0)
                    sb.Append($", {day.Day.ChanceOfRain}% chance of rain");
                sb.AppendLine();
            }
        }

        return sb.ToString();
    }
}
