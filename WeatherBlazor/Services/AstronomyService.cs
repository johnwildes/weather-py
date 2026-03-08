using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

/// <summary>
/// Enriches a WeatherViewModel with astronomy data from the first forecast day
/// and an extended multi-day outlook for future days.
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
        ["Waning Crescent"] = "🌘",
        ["Third Quarter"]   = "🌗"  // Alias for "Last Quarter" used by some API responses
    };

    public static void Enrich(WeatherViewModel vm)
    {
        var today = DateTime.Today;

        // Current day astronomy (first forecast day)
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
            MoonIllumination = astro.MoonIllumination.ToString(),
            DaylightDuration = CalculateDaylight(astro.Sunrise, astro.Sunset)
        };

        // Extended multi-day astronomy forecast (future days only, up to 5)
        vm.ExtendedAstronomyForecast = vm.Forecast.ForecastDay
            .Where(d => DateTime.TryParse(d.Date, out var dt) && dt.Date > today)
            .Take(5)
            .Select(d => BuildExtendedInfo(d, today))
            .ToList();
    }

    public static ExtendedAstronomyInfo BuildExtendedInfo(ForecastDay day, DateTime today)
    {
        var astro = day.Astro;
        DateTime.TryParse(day.Date, out var date);

        return new ExtendedAstronomyInfo
        {
            Date             = day.Date,
            DayLabel         = FormatDayLabel(date, today),
            Sunrise          = astro.Sunrise,
            Sunset           = astro.Sunset,
            DaylightDuration = CalculateDaylight(astro.Sunrise, astro.Sunset),
            Moonrise         = astro.Moonrise,
            Moonset          = astro.Moonset,
            HasMoonrise      = !string.IsNullOrWhiteSpace(astro.Moonrise) &&
                               !astro.Moonrise.StartsWith("No ", StringComparison.OrdinalIgnoreCase),
            HasMoonset       = !string.IsNullOrWhiteSpace(astro.Moonset) &&
                               !astro.Moonset.StartsWith("No ", StringComparison.OrdinalIgnoreCase),
            MoonPhase        = astro.MoonPhase,
            MoonPhaseEmoji   = MoonPhaseEmojis.TryGetValue(astro.MoonPhase, out var emoji) ? emoji : "🌕"
        };
    }

    public static string FormatDayLabel(DateTime date, DateTime today)
    {
        if (date.Date == today.AddDays(1)) return "Tomorrow";
        return date.ToString("ddd, MMM d");
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
