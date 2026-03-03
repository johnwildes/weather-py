using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

/// <summary>
/// Enriches a WeatherViewModel with astronomy data from the first forecast day.
/// Logic mirrors the Python astronomy_features.py module.
/// </summary>
public static class AstronomyService
{
    private static readonly Dictionary<string, string> MoonPhaseEmojis = new(StringComparer.OrdinalIgnoreCase)
    {
        ["New Moon"]        = "🌑",
        ["Waxing Crescent"] = "🌒",
        ["First Quarter"]   = "🌓",
        ["Waxing Gibbous"]  = "🌔",
        ["Full Moon"]       = "🌕",
        ["Waning Gibbous"]  = "🌖",
        ["Last Quarter"]    = "🌗",
        ["Waning Crescent"] = "🌘"
    };

    public static void Enrich(WeatherViewModel vm)
    {
        var firstDay = vm.Forecast.ForecastDay.FirstOrDefault();
        if (firstDay is null) return;

        var astro = firstDay.Astro;

        vm.AstronomyInfo = new AstronomyInfo
        {
            Sunrise          = astro.Sunrise,
            Sunset           = astro.Sunset,
            Moonrise         = astro.Moonrise,
            Moonset          = astro.Moonset,
            MoonPhase        = astro.MoonPhase,
            MoonPhaseEmoji   = MoonPhaseEmojis.TryGetValue(astro.MoonPhase, out var emoji) ? emoji : "🌕",
            MoonIllumination = astro.MoonIllumination,
            DaylightDuration = CalculateDaylight(astro.Sunrise, astro.Sunset)
        };
    }

    private static string CalculateDaylight(string sunrise, string sunset)
    {
        try
        {
            if (DateTime.TryParse(sunrise, out var rise) && DateTime.TryParse(sunset, out var set))
            {
                var duration = set - rise;
                return $"{(int)duration.TotalHours}h {duration.Minutes}m";
            }
        }
        catch { /* ignore parse errors */ }
        return "";
    }
}
