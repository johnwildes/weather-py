using WeatherBlazor.Models;

namespace WeatherBlazor.Services;

public interface IAIService
{
    bool IsConfigured { get; }
    IAsyncEnumerable<string> StreamChatAsync(string message, WeatherViewModel? weatherContext, CancellationToken ct = default);
}
