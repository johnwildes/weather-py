using WeatherBlazor.Models;
using WeatherBlazor.Services;

namespace WeatherBlazor.Tests;

public class SafetyFeaturesServiceTests
{
    [Fact]
    public void Enrich_SetsUvInfo_ForLowUv()
    {
        var vm = MakeViewModel(uv: 1.0);
        SafetyFeaturesService.Enrich(vm);

        Assert.NotNull(vm.UvInfo);
        Assert.Equal("Low", vm.UvInfo.Level);
    }

    [Theory]
    [InlineData(0.5, "Low")]
    [InlineData(3.0, "Moderate")]
    [InlineData(6.0, "High")]
    [InlineData(8.0, "Very High")]
    [InlineData(11.0, "Extreme")]
    public void Enrich_UvLevel_MatchesExpected(double uv, string expectedLevel)
    {
        var vm = MakeViewModel(uv: uv);
        SafetyFeaturesService.Enrich(vm);

        Assert.Equal(expectedLevel, vm.UvInfo?.Level);
    }

    [Fact]
    public void Enrich_SetsAqiInfo_WhenAirQualityPresent()
    {
        var vm = MakeViewModel(epaIndex: 1);
        SafetyFeaturesService.Enrich(vm);

        Assert.NotNull(vm.AqiInfo);
        Assert.Equal("Good", vm.AqiInfo.Level);
    }

    [Theory]
    [InlineData(1, "Good")]
    [InlineData(2, "Moderate")]
    [InlineData(3, "Unhealthy for Sensitive")]
    [InlineData(4, "Unhealthy")]
    [InlineData(5, "Very Unhealthy")]
    [InlineData(6, "Hazardous")]
    public void Enrich_AqiLevel_MatchesEpaIndex(int epa, string expected)
    {
        var vm = MakeViewModel(epaIndex: epa);
        SafetyFeaturesService.Enrich(vm);

        Assert.Equal(expected, vm.AqiInfo?.Level);
    }

    [Fact]
    public void EnrichAlerts_PopulatesAlertInfo()
    {
        var vm = new WeatherViewModel();
        var alerts = new AlertsWrapper
        {
            Alert =
            [
                new WeatherAlert { Headline = "Tornado Warning", Severity = "Extreme", Urgency = "Immediate" }
            ]
        };

        SafetyFeaturesService.EnrichAlerts(vm, alerts);

        Assert.Single(vm.AlertsInfo);
        Assert.Equal("Tornado Warning", vm.AlertsInfo[0].Headline);
        Assert.Equal("🚨", vm.AlertsInfo[0].Icon);
    }

    [Fact]
    public void EnrichAlerts_WithNull_LeavesAlertsEmpty()
    {
        var vm = new WeatherViewModel();
        SafetyFeaturesService.EnrichAlerts(vm, null);
        Assert.Empty(vm.AlertsInfo);
    }

    // ── Helpers ────────────────────────────────────────────────────────────

    private static WeatherViewModel MakeViewModel(double uv = 1.0, int? epaIndex = null)
    {
        AirQuality? aq = epaIndex.HasValue ? new AirQuality { EpaIndex = epaIndex, Pm25 = 5.0, Pm10 = 10.0 } : null;
        return new WeatherViewModel
        {
            Current = new CurrentWeather { Uv = uv, AirQuality = aq }
        };
    }
}
