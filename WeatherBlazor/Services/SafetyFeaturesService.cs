using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

/// <summary>
/// Enriches a WeatherViewModel with UV Index and Air Quality safety information.
/// Logic mirrors the Python safety_features.py module.
/// </summary>
public static class SafetyFeaturesService
{
    public static void Enrich(WeatherViewModel vm)
    {
        var current = vm.Current;

        // UV Index
        vm.UvInfo = GetUvInfo(current.Uv);

        // Air Quality
        if (current.AirQuality is not null)
            vm.AqiInfo = GetAqiInfo(current.AirQuality);

        // Alerts
        // Alerts come from the raw response; the view model holds enriched AlertInfo
        // (called after construction in WeatherApiService – see below)
    }

    public static void EnrichAlerts(WeatherViewModel vm, AlertsWrapper? alertsWrapper)
    {
        if (alertsWrapper is null) return;

        vm.AlertsInfo = alertsWrapper.Alert.Select(a => new AlertInfo
        {
            Headline    = a.Headline,
            Severity    = a.Severity,
            Urgency     = a.Urgency,
            Description = a.Description,
            Instruction = a.Instruction,
            Icon        = GetAlertIcon(a.Severity),
            Color       = GetAlertColor(a.Severity)
        }).ToList();
    }

    private static UvInfo GetUvInfo(double uv)
    {
        return uv switch
        {
            < 3  => new UvInfo { Value = uv, Level = "Low",      Color = "#299501", Recommendation = "No protection required. You can safely stay outside." },
            < 6  => new UvInfo { Value = uv, Level = "Moderate", Color = "#F7E400", Recommendation = "Seek shade during midday. Wear sun-protective clothing." },
            < 8  => new UvInfo { Value = uv, Level = "High",     Color = "#F95900", Recommendation = "Reduce time in sun 10am–4pm. Apply SPF 30+ sunscreen." },
            < 11 => new UvInfo { Value = uv, Level = "Very High",Color = "#D90011", Recommendation = "Take extra precautions. Unprotected skin burns quickly." },
            _    => new UvInfo { Value = uv, Level = "Extreme",  Color = "#6B49C8", Recommendation = "Avoid sun exposure 10am–4pm. Full sun protection required." }
        };
    }

    private static AqiInfo GetAqiInfo(AirQuality aq)
    {
        var epa = aq.EpaIndex ?? 1;
        return epa switch
        {
            1 => new AqiInfo { Level = "Good",                  Color = "#00e400", Guidance = "Air quality is satisfactory, posing little or no risk.",              Pm25 = aq.Pm25, Pm10 = aq.Pm10 },
            2 => new AqiInfo { Level = "Moderate",              Color = "#ffff00", Guidance = "Unusually sensitive individuals should reduce prolonged exertion.",    Pm25 = aq.Pm25, Pm10 = aq.Pm10 },
            3 => new AqiInfo { Level = "Unhealthy for Sensitive",Color = "#ff7e00",Guidance = "Sensitive groups should limit prolonged outdoor exertion.",            Pm25 = aq.Pm25, Pm10 = aq.Pm10 },
            4 => new AqiInfo { Level = "Unhealthy",             Color = "#ff0000", Guidance = "Everyone may begin to experience health effects.",                     Pm25 = aq.Pm25, Pm10 = aq.Pm10 },
            5 => new AqiInfo { Level = "Very Unhealthy",        Color = "#8f3f97", Guidance = "Health warnings. Avoid prolonged outdoor activity.",                  Pm25 = aq.Pm25, Pm10 = aq.Pm10 },
            _ => new AqiInfo { Level = "Hazardous",             Color = "#7e0023", Guidance = "Health emergency. Everyone should avoid all outdoor exertion.",        Pm25 = aq.Pm25, Pm10 = aq.Pm10 }
        };
    }

    private static string GetAlertIcon(string severity) => severity.ToLowerInvariant() switch
    {
        "extreme"  => "🚨",
        "severe"   => "⛔",
        "moderate" => "⚠️",
        _          => "ℹ️"
    };

    private static string GetAlertColor(string severity) => severity.ToLowerInvariant() switch
    {
        "extreme"  => "#d32f2f",
        "severe"   => "#e64a19",
        "moderate" => "#f9a825",
        _          => "#1976d2"
    };
}
