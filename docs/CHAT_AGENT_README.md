# Chat Agent Feature

## Overview

The Weather Forecast application now includes an AI-powered chat assistant powered by Microsoft Foundry's GPT-5.2 model. This feature provides users with an interactive way to ask questions about weather conditions in their searched cities.

## Features

### Desktop-Only Display
- The chat agent is **only available on desktop devices** (screen width ≥ 768px)
- Automatically hidden on mobile and tablet devices to maintain a clean mobile experience
- Responsive design adapts to different desktop screen sizes

### Context-Aware Conversations
- The chat agent has access to the **last 5 searched cities** and their current weather data
- Provides context-aware responses based on the user's recent searches
- Automatically updates context as users search for new locations

### Streaming Responses
- Real-time streaming of AI responses for a better user experience
- Typing indicators show when the assistant is generating a response
- Smooth message animations

### System Prompt Design
The chat agent uses a blended system prompt that combines:
- Weather-specific expertise and meteorology knowledge
- General conversational capabilities
- Access to current weather data from recently searched cities
- Friendly, helpful tone with practical suggestions

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# Microsoft Foundry AI Chat Agent Configuration
FOUNDRY_API_KEY=your_foundry_api_key_here
FOUNDRY_ENDPOINT=https://api.foundry.microsoft.com/v1/chat/completions
```

### API Key Setup

1. Obtain a Microsoft Foundry API key from your Foundry account
2. Add the `FOUNDRY_API_KEY` to your `.env` file
3. (Optional) Customize the `FOUNDRY_ENDPOINT` if using a different endpoint

## Usage

### For Users

1. **Open the chat**: Click the blue chat button in the bottom-right corner of the page (desktop only)
2. **Ask questions**: Type your weather-related questions in the input field
3. **Get answers**: The AI assistant will provide context-aware responses based on your searched cities
4. **Close the chat**: Click the X button in the chat header to close the window

### Example Questions

- "What's the weather like in my recently searched cities?"
- "Should I bring an umbrella tomorrow?"
- "Which city has the best weather right now?"
- "Explain the weather pattern I'm seeing"

## Technical Details

### Architecture

- **Frontend**: JavaScript module (`chat-agent.js`) with Fluent UI components
- **Backend**: Flask blueprint (`chat.py`) handling API requests
- **API Integration**: Streaming SSE (Server-Sent Events) from Microsoft Foundry
- **State Management**: Integration with existing `StateManager` for weather context
- **Styling**: Fluent Design System matching the application's design language

### Files Added

- `/static/js/chat-agent.js` - Chat agent frontend implementation
- `/static/css/chat-agent.css` - Chat UI styling
- `/chat.py` - Flask blueprint for chat API endpoints
- `/test_chat.py` - Test suite for chat functionality
- `/.env.example` - Environment variable template

### API Endpoints

#### `GET /api/chat/config`
Returns chat configuration status (whether API key is configured)

**Response:**
```json
{
  "apiKey": true,
  "endpoint": "https://api.foundry.microsoft.com/v1/chat/completions"
}
```

#### `POST /api/chat/completions`
Handles chat completion requests with streaming support

**Request:**
```json
{
  "message": "What's the weather like?",
  "context": {
    "locations": [...],
    "currentLocation": "New York, NY"
  },
  "stream": true
}
```

**Response:** Server-Sent Events (SSE) stream with JSON chunks

## Limitations

- **No Rate Limiting**: Currently, there is no rate limiting on chat requests (as per requirements)
- **Desktop Only**: Not available on mobile devices (screen width < 768px)
- **API Key Required**: Requires a valid Microsoft Foundry API key to function
- **Context Limit**: Only includes the last 5 searched cities in the context

## Testing

Run the chat agent tests:

```bash
pytest test_chat.py -v
```

Run all tests including chat:

```bash
pytest test_chat.py test_main.py -v
```

## Future Enhancements

Potential improvements for future versions:

- Add conversation history persistence across sessions
- Implement user authentication for personalized experiences
- Add support for voice input/output
- Include more detailed forecast data in context
- Add multi-language support
- Implement rate limiting and usage tracking
- Add analytics to track common questions

## Security Considerations

- API keys are stored in environment variables and never exposed to the frontend
- The configuration endpoint only returns boolean status, not the actual API key
- All API requests are server-side to protect credentials
- Input is properly escaped to prevent XSS attacks
- Chat history is stored locally in the browser (localStorage)

## Troubleshooting

### Chat button doesn't appear
- Check that you're on a desktop device (screen width ≥ 768px)
- Verify JavaScript is enabled in your browser
- Check browser console for errors

### Chat responses don't work
- Verify `FOUNDRY_API_KEY` is set in `.env`
- Check that the Foundry endpoint is accessible
- Review server logs for API errors
- Ensure you have a valid API key with sufficient credits

### Context not updating
- Verify you've searched for locations before asking questions
- Check that StateManager is properly initialized
- Review browser console for state management errors
