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
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 2a6 6 0 0 1 6 6v4a6 6 0 0 1-6 6H6a2 2 0 0 1-2-2v-2a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1a1 1 0 0 1-2 0v-1H6v2h4a4 4 0 0 0 4-4V8a4 4 0 0 0-8 0v.5a1 1 0 0 1-2 0V8a6 6 0 0 1 6-6z"/>
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
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 2a6 6 0 0 1 6 6v4a6 6 0 0 1-6 6H6a2 2 0 0 1-2-2v-2a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1a1 1 0 0 1-2 0v-1H6v2h4a4 4 0 0 0 4-4V8a4 4 0 0 0-8 0v.5a1 1 0 0 1-2 0V8a6 6 0 0 1 6-6z"/>
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
                <fluent-text-field 
                    id="chatInput" 
                    class="chat-input" 
                    placeholder="Ask about the weather..."
                    type="text">
                </fluent-text-field>
                <fluent-button id="chatSendButton" appearance="accent" class="chat-send-btn">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M1.724 1.053a.5.5 0 0 0-.714.545l1.403 4.85a.5.5 0 0 0 .397.354l5.69.953c.268.045.268.434 0 .478l-5.69.953a.5.5 0 0 0-.397.354l-1.403 4.85a.5.5 0 0 0 .714.545l13-6.5a.5.5 0 0 0 0-.894l-13-6.5z"/>
                    </svg>
                </fluent-button>
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
            this.addMessage('assistant', `Sorry, I encountered an error: ${error.message}`);
            console.error('Chat error:', error);
        }
    }

    getWeatherContext() {
        // Get last 5 recent locations with their weather data
        const recentLocations = this.stateManager.getRecentLocations().slice(0, 5);
        const context = {
            locations: [],
            currentLocation: this.stateManager.getUIState().selectedLocation
        };

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
                            if (parsed.content) {
                                fullText += parsed.content;
                                contentElement.textContent = fullText;
                                this.scrollToBottom();
                            }
                        } catch (e) {
                            // Skip invalid JSON
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
        messageDiv.innerHTML = `
            <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
            <div class="message-content">${this.escapeHtml(content)}</div>
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
