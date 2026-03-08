using WeatherBlazor.Models;
using WeatherBlazor.Services;

namespace WeatherBlazor.Tests;

public class AzureOpenAIServiceTests
{
    [Fact]
    public void BuildSystemPrompt_Null_ReturnsBasePrompt()
    {
        var prompt = AzureOpenAIService.BuildSystemPrompt(null);

        Assert.Contains("weather assistant", prompt, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("CURRENTLY DISPLAYED WEATHER", prompt);
    }

    [Fact]
    public void BuildSystemPrompt_WithWeatherContext_ContainsLocationAndConditions()
    {
        var vm = MakeViewModel("London", 15.0, 59.0, "Partly cloudy");

        var prompt = AzureOpenAIService.BuildSystemPrompt(vm);

        Assert.Contains("London",         prompt);
        Assert.Contains("Partly cloudy",  prompt);
        Assert.Contains("15",             prompt);   // TempC
        Assert.Contains("59",             prompt);   // TempF
        Assert.Contains("CURRENTLY DISPLAYED WEATHER", prompt);
    }

    [Fact]
    public void BuildSystemPrompt_WithForecast_ContainsForecastSummary()
    {
        var vm = MakeViewModel("Seattle", 10.0, 50.0, "Rain");
        vm.Forecast.ForecastDay.Add(new ForecastDay
        {
            Date = "2026-03-10",
            Day  = new DaySummary { MaxTempC = 12, MinTempC = 7, Condition = new Condition { Text = "Showers" }, ChanceOfRain = 80 }
        });

        var prompt = AzureOpenAIService.BuildSystemPrompt(vm);

        Assert.Contains("5-Day Forecast Summary", prompt);
        Assert.Contains("2026-03-10",              prompt);
        Assert.Contains("Showers",                 prompt);
        Assert.Contains("80%",                     prompt);
    }

    [Fact]
    public void BuildSystemPrompt_WithAlerts_ContainsAlertInfo()
    {
        var vm = MakeViewModel("Miami", 30.0, 86.0, "Sunny");
        vm.AlertsInfo.Add(new AlertInfo { Headline = "Tornado Watch", Severity = "Moderate" });

        var prompt = AzureOpenAIService.BuildSystemPrompt(vm);

        Assert.Contains("ACTIVE WEATHER ALERTS", prompt);
        Assert.Contains("Tornado Watch",          prompt);
        Assert.Contains("Moderate",               prompt);
    }

    [Fact]
    public void BuildSystemPrompt_WithUvAndAqi_ContainsSafetyInfo()
    {
        var vm = MakeViewModel("Phoenix", 38.0, 100.4, "Sunny");
        vm.UvInfo  = new UvInfo  { Level = "Extreme",  Recommendation = "Avoid sun exposure" };
        vm.AqiInfo = new AqiInfo { Level = "Moderate", Guidance = "Sensitive groups should limit outdoor activity", Pm25 = 12.5 };

        var prompt = AzureOpenAIService.BuildSystemPrompt(vm);

        Assert.Contains("Extreme",                 prompt);
        Assert.Contains("Avoid sun exposure",      prompt);
        Assert.Contains("Moderate",                prompt);
        Assert.Contains("12.5",                    prompt);
    }

    // ── Helpers ──────────────────────────────────────────────────────────────

    private static WeatherViewModel MakeViewModel(string city, double tempC, double tempF, string condition)
        => new()
        {
            Location = new Location { Name = city },
            Current  = new CurrentWeather
            {
                TempC     = tempC,
                TempF     = tempF,
                Condition = new Condition { Text = condition }
            },
            Forecast  = new Forecast()
        };
}
