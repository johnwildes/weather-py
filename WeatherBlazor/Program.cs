using WeatherBlazor.Components;
using WeatherBlazor.Services;
using Microsoft.FluentUI.AspNetCore.Components;

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

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}
app.UseStatusCodePagesWithReExecute("/not-found", createScopeForStatusCodePages: true);
app.UseHttpsRedirection();

app.UseAntiforgery();

app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
