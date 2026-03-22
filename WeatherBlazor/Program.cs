using WeatherBlazor.Components;
using WeatherBlazor.Services;
using Microsoft.FluentUI.AspNetCore.Components;
using Microsoft.AspNetCore.HttpOverrides;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// FluentUI Blazor
builder.Services.AddFluentUIComponents();

// Weather service (typed HttpClient)
builder.Services.AddHttpClient<IWeatherService, WeatherApiService>();

// AI chat service (typed HttpClient) + shared weather context for ChatWidget
builder.Services.AddHttpClient<IAIService, AzureOpenAIService>();
builder.Services.AddScoped<ChatStateService>();

// Trust the Azure Container Apps ingress proxy so the app sees the real
// scheme (https) and client IP rather than the internal HTTP connection.
// Without this, Blazor Server's antiforgery check rejects the SignalR
// circuit negotiate request (Origin: https vs server-perceived http),
// preventing the interactive circuit from connecting.
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    // Azure Container Apps' proxy IPs are not fixed, so clear the default
    // trusted-networks allowlist to accept forwarded headers from any proxy.
    options.KnownIPNetworks.Clear();
    options.KnownProxies.Clear();
});

var app = builder.Build();

// Must be first — populates Request.Scheme / RemoteIpAddress from
// X-Forwarded-Proto / X-Forwarded-For before any other middleware runs.
app.UseForwardedHeaders();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}
app.UseHttpsRedirection();

app.UseAntiforgery();

// MapStaticAssets serves all static files (wwwroot, _framework, _content)
// using a fingerprinted manifest.  Do NOT add UseStaticFiles() — in .NET 10
// it conflicts with MapStaticAssets for _framework/ paths, causing
// blazor.web.js to 404 (see dotnet/aspnetcore#64381).
app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
