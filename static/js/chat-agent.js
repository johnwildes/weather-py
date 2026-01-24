// Chat Agent - Microsoft Foundry GPT-5.2 Integration
// Desktop-only chat popup with streaming responses

class ChatAgent {
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.isOpen = false;
        this.messages = [];
        this.isStreaming = false;
        this.apiKey = null;
        this.foundryEndpoint = null;
        this.MAX_CHAT_HISTORY = 50; // Maximum messages to keep in history
        this.init();
    }

    init() {
        // Only initialize on desktop devices
        if (!this.isDesktop()) {
            console.log('Chat agent disabled on mobile devices');
            return;
        }

        this.loadConfig();
        this.createChatUI();
        this.setupEventListeners();
        this.loadChatHistory();
    }

    isDesktop() {
        // Check if device is desktop based on screen size and user agent
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const isSmallScreen = window.innerWidth < 768;
        return !isMobile && !isSmallScreen;
    }

    async loadConfig() {
        // Load configuration from backend
        try {
            const response = await fetch('/api/chat/config');
            if (response.ok) {
                const config = await response.json();
                this.apiKey = config.apiKey;
                this.foundryEndpoint = config.endpoint;
            }
        } catch (error) {
            console.error('Failed to load chat config:', error);
        }
    }

    createChatUI() {
        // Create chat button
        const chatButton = document.createElement('fluent-button');
        chatButton.id = 'chatAgentButton';
        chatButton.className = 'chat-agent-button';
        chatButton.appearance = 'accent';
        chatButton.innerHTML = `
            <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6.5 10a4.5 4.5 0 1 1 9 0h.5a3.5 3.5 0 1 1 0 7H6a4 4 0 0 1-.5-7.97 4.5 4.5 0 0 1 1-0.03z"/>
                <path d="M12 14l-2.5 5h2l-.5 2 3-4h-2l.5-3z" fill="white"/>
            </svg>
        `;
        chatButton.title = 'Weather Assistant';

        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'chatAgentWindow';
        chatWindow.className = 'chat-agent-window';
        chatWindow.style.display = 'none';
        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-title">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M6.5 10a4.5 4.5 0 1 1 9 0h.5a3.5 3.5 0 1 1 0 7H6a4 4 0 0 1-.5-7.97 4.5 4.5 0 0 1 1-0.03z"/>
                        <path d="M12 14l-2.5 5h2l-.5 2 3-4h-2l.5-3z" fill="#FFD700"/>
                    </svg>
                    <span>Weather Assistant</span>
                </div>
                <fluent-button id="chatCloseButton" appearance="stealth" class="chat-close-btn">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M2.146 2.146a.5.5 0 0 1 .708 0L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854a.5.5 0 0 1 0-.708z"/>
                    </svg>
                </fluent-button>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="chat-welcome">
                    <p>👋 Hi! I'm your weather assistant powered by GPT-5.2.</p>
                    <p>Ask me anything about the weather in your searched cities!</p>
                </div>
            </div>
            <div class="chat-input-area">
                <input 
                    type="text"
                    id="chatInput" 
                    class="chat-input" 
                    placeholder="Ask about the weather..."
                />
                <button id="chatSendButton" class="chat-send-btn">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M1.724 1.053a.5.5 0 0 0-.714.545l1.403 4.85a.5.5 0 0 0 .397.354l5.69.953c.268.045.268.434 0 .478l-5.69.953a.5.5 0 0 0-.397.354l-1.403 4.85a.5.5 0 0 0 .714.545l13-6.5a.5.5 0 0 0 0-.894l-13-6.5z"/>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(chatButton);
        document.body.appendChild(chatWindow);

        this.elements = {
            button: chatButton,
            window: chatWindow,
            messages: chatWindow.querySelector('#chatMessages'),
            input: chatWindow.querySelector('#chatInput'),
            sendButton: chatWindow.querySelector('#chatSendButton'),
            closeButton: chatWindow.querySelector('#chatCloseButton')
        };
    }

    setupEventListeners() {
        // Toggle chat window
        this.elements.button.addEventListener('click', () => this.toggleChat());
        this.elements.closeButton.addEventListener('click', () => this.closeChat());

        // Send message
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        this.elements.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Listen for state changes to update context
        this.stateManager.on('recentLocationsChanged', () => {
            // Context updated, no UI change needed
        });
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        this.isOpen = true;
        this.elements.window.style.display = 'flex';
        this.elements.button.style.display = 'none';
        this.elements.input.focus();
        
        // Animate in
        requestAnimationFrame(() => {
            this.elements.window.classList.add('open');
        });
    }

    closeChat() {
        this.isOpen = false;
        this.elements.window.classList.remove('open');
        
        setTimeout(() => {
            this.elements.window.style.display = 'none';
            this.elements.button.style.display = 'flex';
        }, 200);
    }

    async sendMessage() {
        const input = this.elements.input;
        const message = input.value.trim();
        
        if (!message || this.isStreaming) {
            return;
        }

        // Add user message to chat
        this.addMessage('user', message);
        input.value = '';

        // Show typing indicator
        const typingId = this.showTypingIndicator();

        try {
            // Get context from last 5 searched cities
            const context = this.getWeatherContext();

            // Send to backend with streaming
            await this.streamChatResponse(message, context, typingId);
        } catch (error) {
            this.removeMessage(typingId);
            const errorMsg = `Sorry, I encountered an error: ${error.message}`;
            this.addMessage('assistant', errorMsg);
            console.error('Chat error:', error);
            
            // Log to help with debugging
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                apiKey: this.apiKey ? 'configured' : 'not configured',
                endpoint: this.foundryEndpoint
            });
        }
    }

    getWeatherContext() {
        // Get the currently displayed weather data first
        const currentLocation = this.stateManager.getUIState().selectedLocation;
        const context = {
            locations: [],
            currentLocation: currentLocation,
            currentWeather: null
        };

        // Get the current location's weather data (most important for context)
        if (currentLocation) {
            const currentData = this.stateManager.getWeatherData(currentLocation);
            if (currentData) {
                context.currentWeather = {
                    location: currentData.location,
                    current: currentData.current,
                    forecast: currentData.forecast,
                    uv_info: currentData.uv_info,
                    aqi_info: currentData.aqi_info,
                    alerts: currentData.alerts
                };
            }
        }

        // Also get recent locations for additional context
        const recentLocations = this.stateManager.getRecentLocations().slice(0, 5);
        for (const recent of recentLocations) {
            const weatherData = this.stateManager.getWeatherData(recent.location);
            if (weatherData) {
                context.locations.push({
                    location: recent.location,
                    displayName: recent.displayName,
                    weather: {
                        current: weatherData.current,
                        forecast: weatherData.forecast
                    }
                });
            }
        }

        return context;
    }

    async streamChatResponse(message, context, typingId) {
        this.isStreaming = true;
        
        try {
            const response = await fetch('/api/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: context,
                    stream: true
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Remove typing indicator
            this.removeMessage(typingId);

            // Create message element for streaming response
            const messageId = this.addMessage('assistant', '');
            const messageElement = document.getElementById(messageId);
            const contentElement = messageElement.querySelector('.message-content');

            // Read the stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = '';

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    break;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data === '[DONE]') {
                            break;
                        }

                        try {
                            const parsed = JSON.parse(data);
                            
                            // Handle error messages from backend
                            if (parsed.error) {
                                console.error('Chat API error:', parsed.error);
                                fullText = `Error: ${parsed.error}`;
                                contentElement.textContent = fullText;
                                contentElement.style.color = '#d13438'; // Red color for errors
                                this.scrollToBottom();
                                break;
                            }
                            
                            if (parsed.content) {
                                fullText += parsed.content;
                                contentElement.innerHTML = this.parseMarkdown(fullText);
                                this.scrollToBottom();
                            }
                        } catch (e) {
                            console.warn('Failed to parse SSE data:', data, e);
                        }
                    }
                }
            }

            // Save complete message
            this.messages.push({
                role: 'assistant',
                content: fullText,
                timestamp: Date.now()
            });
            this.saveChatHistory();

        } finally {
            this.isStreaming = false;
        }
    }

    addMessage(role, content) {
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = `chat-message ${role}-message`;
        
        // Render markdown for assistant messages, escape HTML for user messages
        const renderedContent = role === 'assistant' && content 
            ? this.parseMarkdown(content) 
            : this.escapeHtml(content);
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
            <div class="message-content">${renderedContent}</div>
        `;

        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();

        // Save to history (except typing indicators)
        if (content) {
            this.messages.push({
                role: role,
                content: content,
                timestamp: Date.now()
            });
            this.saveChatHistory();
        }

        return messageId;
    }

    showTypingIndicator() {
        const messageId = `typing-${Date.now()}`;
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = 'chat-message assistant-message typing';
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();

        return messageId;
    }

    removeMessage(messageId) {
        const element = document.getElementById(messageId);
        if (element) {
            element.remove();
        }
    }

    scrollToBottom() {
        requestAnimationFrame(() => {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        });
    }

    parseMarkdown(text) {
        if (!text) return '';
        
        // Escape HTML first to prevent XSS
        let html = this.escapeHtml(text);
        
        // Code blocks (```code```)
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Inline code (`code`)
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Headers (### Header)
        html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
        html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>');
        
        // Bold (**text** or __text__)
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
        
        // Italic (*text* or _text_)
        html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
        
        // Unordered lists (- item)
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
        
        // Ordered lists (1. item)
        html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
        
        // Line breaks (double newline = paragraph)
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        // Wrap in paragraph if not already wrapped
        if (!html.startsWith('<')) {
            html = '<p>' + html + '</p>';
        }
        
        // Clean up empty paragraphs
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p>(<h[234]>)/g, '$1');
        html = html.replace(/(<\/h[234]>)<\/p>/g, '$1');
        html = html.replace(/<p>(<ul>)/g, '$1');
        html = html.replace(/(<\/ul>)<\/p>/g, '$1');
        html = html.replace(/<p>(<pre>)/g, '$1');
        html = html.replace(/(<\/pre>)<\/p>/g, '$1');
        
        return html;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    saveChatHistory() {
        try {
            localStorage.setItem('chat_history', JSON.stringify(this.messages.slice(-this.MAX_CHAT_HISTORY)));
        } catch (error) {
            console.error('Failed to save chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const saved = localStorage.getItem('chat_history');
            if (saved) {
                this.messages = JSON.parse(saved);
                // Optionally restore messages to UI
                // this.restoreMessagesToUI();
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }
}

// Export for global use
window.ChatAgent = ChatAgent;
