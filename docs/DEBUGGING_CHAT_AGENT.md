# Chat Agent Debugging Guide

## How to Check Logs

The chat agent now includes comprehensive logging to help debug issues. Here's where to find the information you need:

## 1. Server-Side Logs (Flask Console)

When you run the Flask application, detailed logs are printed to the console/terminal:

```bash
# Start the Flask app
python main.py

# You'll see logs like:
INFO - Chat request - Message: What's the weather like?...
INFO - Config - API Key present: True, Endpoint: https://api.foundry.microsoft.com/v1/chat/completions
INFO - Sending request to https://api.foundry.microsoft.com/v1/chat/completions
INFO - Response status: 200
INFO - Stream completed successfully
```

### Common Error Messages in Server Logs:

**API Key Not Configured:**
```
ERROR - Foundry API key not configured
```
**Solution:** Set `FOUNDRY_API_KEY` in your `.env` file

**API Authentication Error:**
```
INFO - Response status: 401
ERROR - API error response: {"error": "Invalid API key"}
```
**Solution:** Check that your API key is correct and active

**Wrong Endpoint:**
```
INFO - Response status: 404
ERROR - API error response: {"error": "Not found"}
```
**Solution:** Verify `FOUNDRY_ENDPOINT` is correct in `.env`

**Network Error:**
```
ERROR - Network error: HTTPSConnectionPool(host='api.foundry.microsoft.com', port=443): Max retries exceeded
```
**Solution:** Check network connectivity or firewall settings

## 2. Browser Console Logs (Client-Side)

Open your browser's Developer Tools (F12) and check the Console tab:

```javascript
// Configuration loaded
Chat request initiated

// Error details (if any)
Chat API error: Foundry API error (HTTP 401): {"error": "Invalid authentication"}

// Detailed debugging info
Error details: {
  message: "HTTP 401: Unauthorized",
  stack: "...",
  apiKey: "configured",  // or "not configured"
  endpoint: "https://api.foundry.microsoft.com/v1/chat/completions"
}
```

### How to Access Browser Console:

1. **Chrome/Edge:** Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
2. **Firefox:** Press `F12` or `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)
3. **Safari:** Enable Developer menu in Preferences, then press `Cmd+Option+C`

## 3. Chat UI Error Display

Errors are now displayed directly in the chat window in red text:

- **Configuration errors:** "Error: Foundry API key not configured. Please set FOUNDRY_API_KEY in your .env file."
- **API errors:** "Error: Foundry API error (HTTP 401): Invalid API key"
- **Network errors:** "Error: Network error: Connection timeout"

## 4. Network Tab (Advanced Debugging)

In Developer Tools, check the Network tab:

1. Open DevTools (F12)
2. Click the "Network" tab
3. Send a chat message
4. Look for request to `/api/chat/completions`
5. Click on it to see:
   - Request headers
   - Request payload
   - Response headers
   - Response body

## Configuration Checklist

Before troubleshooting, verify your configuration:

### 1. Check .env file exists:
```bash
cat .env
```

Should contain:
```env
FOUNDRY_API_KEY=your_actual_api_key_here
FOUNDRY_ENDPOINT=https://api.foundry.microsoft.com/v1/chat/completions
```

### 2. Verify API key is loaded:
Check server logs when you start the app. When you click the chat button, you should see:
```
INFO - Config - API Key present: True
```

If it says `False`, the environment variable is not loaded.

### 3. Test the configuration endpoint:
```bash
curl http://localhost:5000/api/chat/config
```

Response should be:
```json
{
  "apiKey": true,
  "endpoint": "https://api.foundry.microsoft.com/v1/chat/completions"
}
```

If `apiKey` is `false`, the environment variable is not set correctly.

## Step-by-Step Debugging Process

### Step 1: Check Server Logs
1. Open the terminal where Flask is running
2. Look for lines starting with `INFO - Chat request`
3. Check the API key status and endpoint

### Step 2: Check Browser Console
1. Press F12 to open DevTools
2. Go to Console tab
3. Send a test message in the chat
4. Look for any red error messages

### Step 3: Check Error Message in Chat
1. Look at the actual chat message
2. If it starts with "Error:", read the full message
3. This will tell you exactly what went wrong

## Common Issues and Solutions

### Issue: "API key not configured"
**Check:**
- Does `.env` file exist?
- Is `FOUNDRY_API_KEY` set in `.env`?
- Did you restart Flask after adding the key?

**Solution:**
```bash
echo "FOUNDRY_API_KEY=your_key_here" >> .env
# Restart Flask
```

### Issue: HTTP 401 or 403 errors
**Check:**
- Is your API key correct?
- Is your API key still active/valid?
- Does your account have access to GPT-5.2?

**Solution:**
- Regenerate API key from Foundry dashboard
- Update `.env` with new key
- Restart Flask

### Issue: HTTP 404 error
**Check:**
- Is the endpoint URL correct?
- Is it the right version (v1)?

**Solution:**
```bash
# Update .env with correct endpoint
FOUNDRY_ENDPOINT=https://api.foundry.microsoft.com/v1/chat/completions
```

### Issue: Network timeout
**Check:**
- Can you reach the endpoint from your server?
- Firewall blocking outbound HTTPS?

**Solution:**
```bash
# Test connectivity
curl -I https://api.foundry.microsoft.com
```

## Example Debug Session

Here's what a successful chat interaction looks like in the logs:

**Server logs:**
```
INFO - Chat request - Message: What's the weather like?...
INFO - Config - API Key present: True, Endpoint: https://api.foundry.microsoft.com/v1/chat/completions
INFO - Sending request to https://api.foundry.microsoft.com/v1/chat/completions
INFO - Response status: 200
INFO - Stream completed successfully
```

**Browser console:**
```
Chat request initiated
SSE chunk received: {"content": "Based"}
SSE chunk received: {"content": " on"}
SSE chunk received: {"content": " the"}
...
```

**Chat UI:**
Shows the AI response streaming in character by character.

## Need More Help?

If you're still experiencing issues:

1. Include server logs from the terminal
2. Include browser console logs (F12 → Console)
3. Include the exact error message shown in the chat UI
4. Include your `.env` configuration (without the actual API key)

Example:
```
Server log:
INFO - Response status: 401
ERROR - API error response: {"error": "Invalid API key"}

Browser console:
Error: HTTP 401: Unauthorized

Chat UI message:
Error: Foundry API error (HTTP 401): Invalid API key

.env config:
FOUNDRY_API_KEY=sk-... (masked)
FOUNDRY_ENDPOINT=https://api.foundry.microsoft.com/v1/chat/completions
```
