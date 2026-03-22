# WeatherBlazor Security Review

Reviewed target: `WeatherBlazor/`

Review date: `2026-03-19`

Baseline: `dotnet build WeatherBlazor/WeatherBlazor.csproj` succeeded.

## Executive summary

I did not find a clear **critical** data-loss issue in the current Blazor implementation.

The most important risk is that the app exposes a **public, unauthenticated, unthrottled server-side AI chat capability** backed by Azure OpenAI credentials. That creates a meaningful abuse and cost-exhaustion path and gives attackers a place to run prompt-injection/jailbreak attempts against a backend-managed model.

The next tier of issues are mostly **secret-handling and defense-in-depth** problems: one outbound provider key is placed in URL query strings, Azure OpenAI errors can leak internal details to logs and users, and the app is missing common hardening headers such as CSP and clickjacking protections.

## Severity categories

### Critical

No confirmed critical findings were identified during this review.

## High

### H1. Public server-side AI chat is exposed without authentication or rate limiting

**Evidence**

- `WeatherBlazor/Components/Layout/MainLayout.razor:33` renders `<ChatWidget />` for all users.
- `WeatherBlazor/Program.cs:17-19` registers `IAIService`/`AzureOpenAIService` with no auth or rate-limiting controls.
- `WeatherBlazor/Services/AzureOpenAIService.cs:39-72` forwards arbitrary user input to Azure OpenAI using server-side credentials.

**Why it matters**

Any visitor can consume the server-backed chat feature. Because the Azure OpenAI call is made from the server, the application owner absorbs the cost and abuse risk. An attacker can automate requests, exhaust quota, drive cost spikes, or use repeated jailbreak/prompt-injection attempts against a privileged backend integration.

**Impact / data-loss view**

- High impact to availability and cost.
- Data-loss risk is moderate rather than catastrophic in the current code, because the model only receives the user message plus weather context, not broader application secrets.
- Still, this is the clearest externally exploitable risk in the implementation.

**Recommended mitigation**

- Require authentication before enabling chat, or gate it behind a feature flag.
- Add server-side rate limiting per IP/user/circuit.
- Add message length caps and request quotas.
- Add telemetry/alerting for abnormal Azure OpenAI usage.

## Medium

### M1. Weather API key is sent in URL query strings

**Evidence**

- `WeatherBlazor/Services/WeatherApiService.cs:38`
- `WeatherBlazor/Services/WeatherApiService.cs:78`
- `WeatherBlazor/Services/WeatherApiService.cs:100`

Example:

```csharp
var url = $"{BaseUrl}/forecast.json?key={_apiKey}&q={Uri.EscapeDataString(location)}&days={days}&aqi=yes&alerts=yes";
```

**Why it matters**

Although this is a server-to-server call, secrets placed in URLs are more likely to end up in reverse-proxy logs, APM traces, diagnostics, and other intermediary systems.

**Impact / data-loss view**

- Moderate impact if infrastructure logs are accessible or retained broadly.
- Primary risk is unauthorized reuse of the third-party weather API key, not direct end-user data loss.

**Recommended mitigation**

- Prefer header-based credential transport if the provider supports it.
- If the provider requires query parameters, tightly control logging at proxies and application telemetry layers.
- Rotate the key if there is any doubt about historical exposure.

### M2. Azure OpenAI error handling can leak internal details to logs and users

**Evidence**

- `WeatherBlazor/Services/AzureOpenAIService.cs:77`
- `WeatherBlazor/Services/AzureOpenAIService.cs:89-90`

Examples:

```csharp
connectErr = $"⚠️ Connection error: {ex.Message}";
_logger.LogError("Azure OpenAI returned {Status}: {Body}", response.StatusCode, err);
```

**Why it matters**

Returning raw exception text to the browser can expose internal DNS names, endpoint details, or network behavior. Logging the full provider error body can also store sensitive diagnostics or user-supplied content in centralized logs.

**Impact / data-loss view**

- Moderate information-disclosure risk.
- Limited direct data-loss impact, but it increases the blast radius of operational failures and support log access.

**Recommended mitigation**

- Return generic user-facing errors.
- Log status codes and sanitized error categories instead of full response bodies.
- Treat chat prompts and provider responses as potentially sensitive operational data.

### M3. Missing common hardening headers and CSP

**Evidence**

- `WeatherBlazor/Program.cs:23-39` enables HTTPS, HSTS, and antiforgery.
- No corresponding middleware adds `Content-Security-Policy`, `X-Frame-Options`/`frame-ancestors`, `X-Content-Type-Options`, `Referrer-Policy`, or `Permissions-Policy`.

**Why it matters**

The app relies on interactive server-side Blazor and JavaScript interop. Without a CSP and related headers, a future XSS issue would be easier to exploit, and clickjacking defenses are absent.

**Impact / data-loss view**

- Moderate defense-in-depth gap.
- By itself this is not a direct data-loss bug, but it weakens containment if another bug appears.

**Recommended mitigation**

- Add a CSP suitable for Blazor Server.
- Add clickjacking protection (`frame-ancestors 'none'` or equivalent).
- Add `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and `Permissions-Policy`.

### M4. User-controlled inputs lack strong server-side bounds

**Evidence**

- `WeatherBlazor/Components/Pages/Home.razor:72-98` accepts `location` directly from the query string and sends it to the weather service.
- `WeatherBlazor/Components/Weather/SearchBar.razor:41-56` only checks a minimum length before searching.
- `WeatherBlazor/Components/Chat/ChatWidget.razor:141-179` accepts any non-empty chat input and streams it upstream.

**Why it matters**

There are basic checks, but no clear maximum lengths, normalization rules, or quota controls. That makes it easier to drive oversized requests, churn outbound provider usage, or degrade service behavior.

**Impact / data-loss view**

- Moderate availability/cost risk.
- Low direct data-loss risk in the current code.

**Recommended mitigation**

- Enforce server-side maximum lengths for location and chat inputs.
- Normalize/validate expected location formats.
- Pair input bounds with rate limiting.

## Low

### L1. Development config uses wildcard `AllowedHosts`

**Evidence**

- `WeatherBlazor/appsettings.Development.json:8`

```json
"AllowedHosts": "*"
```

**Why it matters**

This is in the development settings rather than the production config, so the immediate production risk is low. Still, wildcard host allowances are easy to promote accidentally into deployed environments.

**Impact / data-loss view**

- Low current impact.
- Low direct data-loss risk.

**Recommended mitigation**

- Keep development-only settings isolated.
- Set explicit production host allow-lists in deployment configuration.

### L2. Console logging is used in a UI component

**Evidence**

- `WeatherBlazor/Components/Layout/MainLayout.razor:68-70`

```csharp
Console.WriteLine($"[Theme] Could not read localStorage: {ex.Message}");
```

**Why it matters**

This is mainly an operational hygiene issue. It is less controllable and less scrub-friendly than structured application logging.

**Impact / data-loss view**

- Low impact.
- No meaningful direct data-loss risk by itself.

**Recommended mitigation**

- Use `ILogger` with sanitized messages instead of `Console.WriteLine`.

## Notable positive findings

- `WeatherBlazor/Program.cs:24-31` enables exception handling outside development, HSTS, and HTTPS redirection.
- `WeatherBlazor/Program.cs:33` enables antiforgery middleware.
- `WeatherBlazor/Components/Chat/ChatWidget.razor:203-205` HTML-encodes model output before applying the custom markdown formatting, so I did **not** find a confirmed XSS issue in the current markdown renderer.
- No real secrets were committed in the reviewed source files; the config placeholders were empty.

## Recommended remediation order

1. Lock down the Azure OpenAI chat surface with authentication, quotas, and server-side rate limiting.
2. Sanitize Azure OpenAI error handling for both logs and user-facing responses.
3. Reduce secret exposure from outbound weather API usage and review infrastructure logging.
4. Add CSP and the rest of the missing hardening headers.
5. Add input length limits and request throttling for weather search, weather lookup, and chat.
