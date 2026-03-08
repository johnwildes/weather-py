using System.Text.Json.Serialization;

namespace WeatherBlazor.Models;

// ── Location ──────────────────────────────────────────────────────────────────
public class Location
{
    [JsonPropertyName("name")]      public string Name      { get; set; } = "";
    [JsonPropertyName("region")]    public string Region    { get; set; } = "";
    [JsonPropertyName("country")]   public string Country   { get; set; } = "";
    [JsonPropertyName("lat")]       public double Lat       { get; set; }
    [JsonPropertyName("lon")]       public double Lon       { get; set; }
    [JsonPropertyName("tz_id")]     public string TzId      { get; set; } = "";
    [JsonPropertyName("localtime")] public string Localtime { get; set; } = "";
}

// ── Condition ─────────────────────────────────────────────────────────────────
public class Condition
{
    [JsonPropertyName("text")] public string Text { get; set; } = "";
    [JsonPropertyName("icon")] public string Icon { get; set; } = "";
    [JsonPropertyName("code")] public int    Code { get; set; }

    public string IconUrl => Icon.StartsWith("//") ? "https:" + Icon : Icon;
}

// ── Air Quality ───────────────────────────────────────────────────────────────
public class AirQuality
{
    [JsonPropertyName("pm2_5")]        public double? Pm25      { get; set; }
    [JsonPropertyName("pm10")]         public double? Pm10      { get; set; }
    [JsonPropertyName("us-epa-index")] public int?    EpaIndex  { get; set; }
    [JsonPropertyName("gb-defra-index")] public int?  DefraIndex { get; set; }
}

// ── Current Weather ───────────────────────────────────────────────────────────
public class CurrentWeather
{
    [JsonPropertyName("temp_c")]       public double    TempC       { get; set; }
    [JsonPropertyName("temp_f")]       public double    TempF       { get; set; }
    [JsonPropertyName("feelslike_c")]  public double    FeelsLikeC  { get; set; }
    [JsonPropertyName("feelslike_f")]  public double    FeelsLikeF  { get; set; }
    [JsonPropertyName("humidity")]     public int       Humidity    { get; set; }
    [JsonPropertyName("wind_kph")]     public double    WindKph     { get; set; }
    [JsonPropertyName("wind_mph")]     public double    WindMph     { get; set; }
    [JsonPropertyName("wind_dir")]     public string    WindDir     { get; set; } = "";
    [JsonPropertyName("vis_km")]       public double    VisKm       { get; set; }
    [JsonPropertyName("vis_miles")]    public double    VisMiles    { get; set; }
    [JsonPropertyName("uv")]           public double    Uv          { get; set; }
    [JsonPropertyName("pressure_mb")]  public double    PressureMb  { get; set; }
    [JsonPropertyName("condition")]    public Condition Condition   { get; set; } = new();
    [JsonPropertyName("air_quality")]  public AirQuality? AirQuality { get; set; }
}

// ── Day Summary ───────────────────────────────────────────────────────────────
public class DaySummary
{
    [JsonPropertyName("maxtemp_c")]             public double    MaxTempC         { get; set; }
    [JsonPropertyName("maxtemp_f")]             public double    MaxTempF         { get; set; }
    [JsonPropertyName("mintemp_c")]             public double    MinTempC         { get; set; }
    [JsonPropertyName("mintemp_f")]             public double    MinTempF         { get; set; }
    [JsonPropertyName("avgtemp_c")]             public double    AvgTempC         { get; set; }
    [JsonPropertyName("avgtemp_f")]             public double    AvgTempF         { get; set; }
    [JsonPropertyName("daily_chance_of_rain")]  public int       ChanceOfRain     { get; set; }
    [JsonPropertyName("daily_chance_of_snow")]  public int       ChanceOfSnow     { get; set; }
    [JsonPropertyName("totalprecip_mm")]        public double    TotalPrecipMm    { get; set; }
    [JsonPropertyName("maxwind_kph")]           public double    MaxWindKph       { get; set; }
    [JsonPropertyName("uv")]                    public double    Uv               { get; set; }
    [JsonPropertyName("condition")]             public Condition Condition        { get; set; } = new();
    [JsonPropertyName("air_quality")]           public AirQuality? AirQuality     { get; set; }
}

// ── Astronomy ─────────────────────────────────────────────────────────────────
public class Astro
{
    [JsonPropertyName("sunrise")]            public string Sunrise           { get; set; } = "";
    [JsonPropertyName("sunset")]             public string Sunset            { get; set; } = "";
    [JsonPropertyName("moonrise")]           public string Moonrise          { get; set; } = "";
    [JsonPropertyName("moonset")]            public string Moonset           { get; set; } = "";
    [JsonPropertyName("moon_phase")]         public string MoonPhase         { get; set; } = "";
    [JsonPropertyName("moon_illumination")]  public int    MoonIllumination  { get; set; } = 0;
}

// ── Hourly ────────────────────────────────────────────────────────────────────
public class HourData
{
    [JsonPropertyName("time")]         public string    Time        { get; set; } = "";
    [JsonPropertyName("temp_c")]       public double    TempC       { get; set; }
    [JsonPropertyName("temp_f")]       public double    TempF       { get; set; }
    [JsonPropertyName("feelslike_c")]  public double    FeelsLikeC  { get; set; }
    [JsonPropertyName("feelslike_f")]  public double    FeelsLikeF  { get; set; }
    [JsonPropertyName("humidity")]     public int       Humidity    { get; set; }
    [JsonPropertyName("wind_kph")]     public double    WindKph     { get; set; }
    [JsonPropertyName("chance_of_rain")] public int     ChanceOfRain { get; set; }
    [JsonPropertyName("condition")]    public Condition Condition   { get; set; } = new();
}

// ── Forecast Day ──────────────────────────────────────────────────────────────
public class ForecastDay
{
    [JsonPropertyName("date")]  public string      Date   { get; set; } = "";
    [JsonPropertyName("day")]   public DaySummary  Day    { get; set; } = new();
    [JsonPropertyName("astro")] public Astro       Astro  { get; set; } = new();
    [JsonPropertyName("hour")]  public List<HourData> Hour { get; set; } = [];
}

// ── Forecast ──────────────────────────────────────────────────────────────────
public class Forecast
{
    [JsonPropertyName("forecastday")] public List<ForecastDay> ForecastDay { get; set; } = [];
}

// ── Alert ─────────────────────────────────────────────────────────────────────
public class WeatherAlert
{
    [JsonPropertyName("headline")]    public string Headline    { get; set; } = "";
    [JsonPropertyName("msgtype")]     public string MsgType     { get; set; } = "";
    [JsonPropertyName("severity")]    public string Severity    { get; set; } = "";
    [JsonPropertyName("urgency")]     public string Urgency     { get; set; } = "";
    [JsonPropertyName("areas")]       public string Areas       { get; set; } = "";
    [JsonPropertyName("category")]    public string Category    { get; set; } = "";
    [JsonPropertyName("event")]       public string Event       { get; set; } = "";
    [JsonPropertyName("note")]        public string Note        { get; set; } = "";
    [JsonPropertyName("desc")]        public string Description { get; set; } = "";
    [JsonPropertyName("instruction")] public string Instruction { get; set; } = "";
}

// ── Alerts Wrapper ────────────────────────────────────────────────────────────
public class AlertsWrapper
{
    [JsonPropertyName("alert")] public List<WeatherAlert> Alert { get; set; } = [];
}

// ── Full API Response ─────────────────────────────────────────────────────────
public class WeatherApiResponse
{
    [JsonPropertyName("location")] public Location        Location { get; set; } = new();
    [JsonPropertyName("current")]  public CurrentWeather  Current  { get; set; } = new();
    [JsonPropertyName("forecast")] public Forecast        Forecast { get; set; } = new();
    [JsonPropertyName("alerts")]   public AlertsWrapper?  Alerts   { get; set; }
}

// ── Search Result ─────────────────────────────────────────────────────────────
public class SearchResult
{
    [JsonPropertyName("name")]    public string Name    { get; set; } = "";
    [JsonPropertyName("region")]  public string Region  { get; set; } = "";
    [JsonPropertyName("country")] public string Country { get; set; } = "";

    public string Display => $"{Name}, {Region}, {Country}";
    public string Value   => Name;
}

// ── Enriched Safety Info ──────────────────────────────────────────────────────
public class UvInfo
{
    public double Value          { get; set; }
    public string Level          { get; set; } = "";
    public string Recommendation { get; set; } = "";
    public string Color          { get; set; } = "#999";
}

public class AqiInfo
{
    public string Level    { get; set; } = "";
    public string Guidance { get; set; } = "";
    public string Color    { get; set; } = "#999";
    public double? Pm25    { get; set; }
    public double? Pm10    { get; set; }
}

public class AlertInfo
{
    public string Icon        { get; set; } = "⚠️";
    public string Headline    { get; set; } = "";
    public string Severity    { get; set; } = "";
    public string Urgency     { get; set; } = "";
    public string Description { get; set; } = "";
    public string Instruction { get; set; } = "";
    public string Color       { get; set; } = "#e74c3c";
}

// ── Enriched Astronomy Info ───────────────────────────────────────────────────
public class AstronomyInfo
{
    public string Sunrise          { get; set; } = "";
    public string Sunset           { get; set; } = "";
    public string Moonrise         { get; set; } = "";
    public string Moonset          { get; set; } = "";
    public string MoonPhase        { get; set; } = "";
    public string MoonPhaseEmoji   { get; set; } = "🌕";
    public string MoonIllumination { get; set; } = "";
    public string DaylightDuration { get; set; } = "";
}

// ── Full Weather View Model ───────────────────────────────────────────────────
public class WeatherViewModel
{
    public Location        Location      { get; set; } = new();
    public CurrentWeather  Current       { get; set; } = new();
    public Forecast        Forecast      { get; set; } = new();
    public UvInfo?         UvInfo        { get; set; }
    public AqiInfo?        AqiInfo       { get; set; }
    public List<AlertInfo> AlertsInfo    { get; set; } = [];
    public AstronomyInfo?  AstronomyInfo { get; set; }
}
