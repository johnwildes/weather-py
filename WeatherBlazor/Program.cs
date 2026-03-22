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
    options.KnownNetworks.Clear();
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
app.UseStatusCodePagesWithReExecute("/not-found", createScopeForStatusCodePages: true);
app.UseHttpsRedirection();

// Serve wwwroot files (including _framework/blazor.web.js) as middleware so
// they are delivered before endpoint routing runs.  MapStaticAssets() is
// endpoint-based and, in some production Docker configurations, fails to match
// the non-fingerprinted _framework/ routes — resulting in a 404 for
// blazor.web.js that prevents the Blazor circuit from ever starting.
app.UseStaticFiles();

app.UseAntiforgery();

// MapStaticAssets handles fingerprinted asset URLs (long-lived cache headers).
// UseStaticFiles above handles the remaining wwwroot files as a middleware fallback.
app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
