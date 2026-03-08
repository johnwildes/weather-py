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
    [InlineData("Third Quarter",   "🌗")]
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

    // ── Extended Outlook Tests ────────────────────────────────────────────

    [Fact]
    public void Enrich_PopulatesExtendedForecast_ForFutureDays()
    {
        var today    = DateTime.Today;
        var tomorrow = today.AddDays(1).ToString("yyyy-MM-dd");
        var dayAfter = today.AddDays(2).ToString("yyyy-MM-dd");

        var vm = new WeatherViewModel
        {
            Forecast = new Forecast
            {
                ForecastDay =
                [
                    MakeForecastDay(today.ToString("yyyy-MM-dd"), "06:00 AM", "07:00 PM", "Full Moon", 100),
                    MakeForecastDay(tomorrow,                      "06:05 AM", "07:05 PM", "Waning Gibbous", 85),
                    MakeForecastDay(dayAfter,                      "06:10 AM", "07:10 PM", "Waning Gibbous", 70)
                ]
            }
        };

        AstronomyService.Enrich(vm);

        Assert.Equal(2, vm.ExtendedAstronomyForecast.Count);
        Assert.Equal(tomorrow, vm.ExtendedAstronomyForecast[0].Date);
        Assert.Equal(dayAfter, vm.ExtendedAstronomyForecast[1].Date);
    }

    [Fact]
    public void Enrich_ExtendedForecast_ExcludesToday()
    {
        var today = DateTime.Today;

        var vm = new WeatherViewModel
        {
            Forecast = new Forecast
            {
                ForecastDay =
                [
                    MakeForecastDay(today.ToString("yyyy-MM-dd"), "06:00 AM", "07:00 PM", "Full Moon", 100)
                ]
            }
        };

        AstronomyService.Enrich(vm);

        Assert.Empty(vm.ExtendedAstronomyForecast);
    }

    [Fact]
    public void Enrich_ExtendedForecast_LimitedToFiveDays()
    {
        var today = DateTime.Today;
        var days = Enumerable.Range(1, 7)
            .Select(i => MakeForecastDay(today.AddDays(i).ToString("yyyy-MM-dd"), "06:00 AM", "07:00 PM", "Full Moon", 100))
            .ToList();

        var vm = new WeatherViewModel { Forecast = new Forecast { ForecastDay = days } };

        AstronomyService.Enrich(vm);

        Assert.Equal(5, vm.ExtendedAstronomyForecast.Count);
    }

    [Fact]
    public void BuildExtendedInfo_Tomorrow_HasTomorrowLabel()
    {
        var today    = DateTime.Today;
        var tomorrow = today.AddDays(1);
        var day      = MakeForecastDay(tomorrow.ToString("yyyy-MM-dd"), "07:00 AM", "06:00 PM", "Waning Gibbous", 80);

        var result = AstronomyService.BuildExtendedInfo(day, today);

        Assert.Equal("Tomorrow", result.DayLabel);
        Assert.Equal(tomorrow.ToString("yyyy-MM-dd"), result.Date);
    }

    [Fact]
    public void BuildExtendedInfo_FutureDay_HasFormattedLabel()
    {
        var today  = DateTime.Today;
        var future = today.AddDays(2);
        var day    = MakeForecastDay(future.ToString("yyyy-MM-dd"), "07:00 AM", "06:00 PM", "Waning Gibbous", 80);

        var result = AstronomyService.BuildExtendedInfo(day, today);

        Assert.Equal(future.ToString("ddd, MMM d"), result.DayLabel);
    }

    [Fact]
    public void BuildExtendedInfo_HasMoonrise_TrueForValidTime()
    {
        var today = DateTime.Today;
        var day   = MakeForecastDay(today.AddDays(1).ToString("yyyy-MM-dd"), "06:00 AM", "07:00 PM", "Full Moon", 100,
                                    moonrise: "08:00 PM", moonset: "No Moonset");

        var result = AstronomyService.BuildExtendedInfo(day, today);

        Assert.True(result.HasMoonrise);
        Assert.False(result.HasMoonset);
    }

    [Fact]
    public void BuildExtendedInfo_DaylightDuration_Calculated()
    {
        var today = DateTime.Today;
        var day   = MakeForecastDay(today.AddDays(1).ToString("yyyy-MM-dd"), "06:00 AM", "06:00 PM", "Full Moon", 100);

        var result = AstronomyService.BuildExtendedInfo(day, today);

        Assert.Equal("12h 0m", result.DaylightDuration);
    }

    [Fact]
    public void FormatDayLabel_Tomorrow_ReturnsTomorrow()
    {
        var today    = DateTime.Today;
        var tomorrow = today.AddDays(1);

        Assert.Equal("Tomorrow", AstronomyService.FormatDayLabel(tomorrow, today));
    }

    [Fact]
    public void FormatDayLabel_OtherDay_ReturnsFormattedDate()
    {
        var today  = DateTime.Today;
        var future = today.AddDays(3);

        Assert.Equal(future.ToString("ddd, MMM d"), AstronomyService.FormatDayLabel(future, today));
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

    private static ForecastDay MakeForecastDay(
        string date, string sunrise, string sunset, string moonPhase, int moonIllumination,
        string moonrise = "08:00 PM", string moonset = "06:00 AM")
    {
        return new ForecastDay
        {
            Date = date,
            Astro = new Astro
            {
                Sunrise          = sunrise,
                Sunset           = sunset,
                Moonrise         = moonrise,
                Moonset          = moonset,
                MoonPhase        = moonPhase,
                MoonIllumination = moonIllumination
            }
        };
    }
}
