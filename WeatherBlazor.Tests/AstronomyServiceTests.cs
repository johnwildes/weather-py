using WeatherBlazor.Models;
using WeatherBlazor.Services;

namespace WeatherBlazor.Tests;

public class AstronomyServiceTests
{
    [Fact]
    public void Enrich_SetsAstronomyInfo_WhenForecastDayPresent()
    {
        var vm = MakeViewModel("07:30 AM", "05:45 PM", "Full Moon", 100);
        AstronomyService.Enrich(vm);

        Assert.NotNull(vm.AstronomyInfo);
        Assert.Equal("Full Moon", vm.AstronomyInfo.MoonPhase);
        Assert.Equal("🌕", vm.AstronomyInfo.MoonPhaseEmoji);
        Assert.Equal("07:30 AM", vm.AstronomyInfo.Sunrise);
        Assert.Equal("05:45 PM", vm.AstronomyInfo.Sunset);
    }

    [Fact]
    public void Enrich_SetsDefaultEmoji_WhenPhaseUnknown()
    {
        var vm = MakeViewModel("06:00 AM", "07:00 PM", "Unknown Phase", 50);
        AstronomyService.Enrich(vm);

        Assert.Equal("🌕", vm.AstronomyInfo?.MoonPhaseEmoji);
    }

    [Theory]
    [InlineData("New Moon",        "🌑")]
    [InlineData("Waxing Crescent", "🌒")]
    [InlineData("First Quarter",   "🌓")]
    [InlineData("Waxing Gibbous",  "🌔")]
    [InlineData("Full Moon",       "🌕")]
    [InlineData("Waning Gibbous",  "🌖")]
    [InlineData("Last Quarter",    "🌗")]
    [InlineData("Waning Crescent", "🌘")]
    public void Enrich_MoonPhaseEmoji_MatchesPhase(string phase, string expectedEmoji)
    {
        var vm = MakeViewModel("06:00 AM", "06:00 PM", phase, 50);
        AstronomyService.Enrich(vm);

        Assert.Equal(expectedEmoji, vm.AstronomyInfo?.MoonPhaseEmoji);
    }

    [Fact]
    public void Enrich_NoForecastDay_LeavesAstronomyNull()
    {
        var vm = new WeatherViewModel();
        AstronomyService.Enrich(vm);
        Assert.Null(vm.AstronomyInfo);
    }

    // ── Helpers ────────────────────────────────────────────────────────────

    private static WeatherViewModel MakeViewModel(
        string sunrise, string sunset, string moonPhase, int moonIllumination)
    {
        return new WeatherViewModel
        {
            Forecast = new Forecast
            {
                ForecastDay =
                [
                    new ForecastDay
                    {
                        Date = DateTime.Today.ToString("yyyy-MM-dd"),
                        Astro = new Astro
                        {
                            Sunrise           = sunrise,
                            Sunset            = sunset,
                            Moonrise          = "08:00 PM",
                            Moonset           = "06:00 AM",
                            MoonPhase         = moonPhase,
                            MoonIllumination  = moonIllumination
                        }
                    }
                ]
            }
        };
    }
}
