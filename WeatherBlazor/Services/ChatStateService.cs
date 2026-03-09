using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

/// <summary>
/// Scoped service that shares the current weather context between Home.razor and ChatWidget.
/// Injecting the same scoped instance allows ChatWidget to access whatever weather is
/// currently displayed without requiring component parameters or cascading values.
/// </summary>
public class ChatStateService
{
    public WeatherViewModel? CurrentWeather { get; set; }
}
