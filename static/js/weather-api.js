// Weather API Integration - Phase 4 Implementation
// Handles all API calls and async operations with Fluent UI components

class WeatherAPI {
    constructor() {
        this.baseUrl = window.location.origin;
        this.requestQueue = new Map();
        this.cache = new Map();
        this.cacheExpiry = 5 * 60 * 1000; // 5 minutes cache
    }

    // Generic API request method with error handling
    async makeRequest(url, options = {}) {
        const requestId = `${options.method || 'GET'}_${url}`;
        
        // Prevent duplicate requests
        if (this.requestQueue.has(requestId)) {
            return this.requestQueue.get(requestId);
        }

        // Check cache for GET requests
        if (!options.method || options.method === 'GET') {
            const cached = this.getFromCache(url);
            if (cached) {
                return cached;
            }
        }

        const requestPromise = this._executeRequest(url, options);
        this.requestQueue.set(requestId, requestPromise);

        try {
            const result = await requestPromise;
            this.requestQueue.delete(requestId);
            
            // Cache successful GET requests
            if (!options.method || options.method === 'GET') {
                this.setCache(url, result);
            }
            
            return result;
        } catch (error) {
            this.requestQueue.delete(requestId);
            throw error;
        }
    }

    async _executeRequest(url, options) {
        const fullUrl = url.startsWith('http') ? url : `${this.baseUrl}${url}`;
        
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(fullUrl, finalOptions);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: response.statusText }));
                throw new APIError(errorData.error || `HTTP ${response.status}`, response.status);
            }

            return await response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError(`Network error: ${error.message}`, 0);
        }
    }

    // Cache management
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
            return cached.data;
        }
        this.cache.delete(key);
        return null;
    }

    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    clearCache() {
        this.cache.clear();
    }

    // API Methods for weather operations

    // Bulk weather data retrieval
    async getBulkWeather(locations, tempUnit = 'celsius') {
        return this.makeRequest('/api/weather/bulk', {
            method: 'POST',
            body: JSON.stringify({
                locations: locations,
                tempUnit: tempUnit
            })
        });
    }

    // Location validation
    async validateLocation(location) {
        return this.makeRequest(`/api/validate-location?location=${encodeURIComponent(location)}`);
    }

    // Location search/autocomplete
    async searchLocations(query) {
        if (!query || query.length < 2) {
            return [];
        }
        return this.makeRequest(`/api/search-locations?q=${encodeURIComponent(query)}`);
    }

    // Detailed forecast for single location
    async getDetailedForecast(location) {
        return this.makeRequest(`/api/detailed-forecast?location=${encodeURIComponent(location)}`);
    }

    // Hourly forecast
    async getHourlyForecast(location, days = 3) {
        return this.makeRequest(`/api/hourly-forecast?location=${encodeURIComponent(location)}&days=${days}`);
    }

    // Get current weather for single location
    async getCurrentWeather(location) {
        return this.makeRequest(`/forecast?zip=${encodeURIComponent(location)}`, {
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'WeatherApp/1.0'
            }
        });
    }

    // Batch operations with progress tracking
    async getBulkWeatherWithProgress(locations, progressCallback) {
        const total = locations.length;
        let completed = 0;

        if (progressCallback) {
            progressCallback(0, total);
        }

        try {
            const results = await this.getBulkWeather(locations);
            
            if (progressCallback) {
                progressCallback(total, total);
            }
            
            return results;
        } catch (error) {
            // If bulk fails, try individual requests
            const results = [];
            
            for (const location of locations) {
                try {
                    const result = await this.getCurrentWeather(location);
                    results.push({ location, data: result, success: true });
                } catch (err) {
                    results.push({ location, error: err.message, success: false });
                }
                
                completed++;
                if (progressCallback) {
                    progressCallback(completed, total);
                }
            }
            
            return { results };
        }
    }
}

// Custom API Error class
class APIError extends Error {
    constructor(message, status = 0) {
        super(message);
        this.name = 'APIError';
        this.status = status;
    }
}

// Progress indicator utilities for Fluent UI integration
class ProgressIndicator {
    static show(message = 'Loading...') {
        let indicator = document.getElementById('globalProgressIndicator');
        
        if (!indicator) {
            indicator = document.createElement('fluent-progress-ring');
            indicator.id = 'globalProgressIndicator';
            indicator.className = 'global-progress';
            
            const container = document.createElement('div');
            container.className = 'progress-container';
            container.innerHTML = `
                <div class="progress-content">
                    ${indicator.outerHTML}
                    <span class="progress-message">${message}</span>
                </div>
            `;
            
            document.body.appendChild(container);
        } else {
            const container = indicator.closest('.progress-container');
            if (container) {
                container.querySelector('.progress-message').textContent = message;
                container.style.display = 'flex';
            }
        }
    }

    static hide() {
        const container = document.querySelector('.progress-container');
        if (container) {
            container.style.display = 'none';
        }
    }

    static update(message) {
        const messageElement = document.querySelector('.progress-message');
        if (messageElement) {
            messageElement.textContent = message;
        }
    }
}

// Message bar utilities for error handling
class MessageBar {
    static show(message, type = 'info', duration = 5000) {
        const messageBar = document.getElementById('messageBar');
        if (messageBar) {
            messageBar.setAttribute('intent', type);
            messageBar.querySelector('.message-content').textContent = message;
            messageBar.hidden = false;

            if (duration > 0) {
                setTimeout(() => {
                    messageBar.hidden = true;
                }, duration);
            }
        } else {
            // Create a new message bar if one doesn't exist
            this.createMessageBar(message, type, duration);
        }
    }

    static createMessageBar(message, type, duration) {
        const messageBar = document.createElement('fluent-message-bar');
        messageBar.id = 'dynamicMessageBar';
        messageBar.setAttribute('intent', type);
        messageBar.innerHTML = `
            <span class="message-content">${message}</span>
            <fluent-button slot="action" appearance="lightweight" onclick="this.closest('fluent-message-bar').hidden = true">
                Dismiss
            </fluent-button>
        `;
        
        // Insert at top of main content
        const main = document.querySelector('.app-main') || document.body;
        main.insertBefore(messageBar, main.firstChild);

        if (duration > 0) {
            setTimeout(() => {
                messageBar.remove();
            }, duration);
        }
    }

    static hide() {
        const messageBar = document.getElementById('messageBar') || document.getElementById('dynamicMessageBar');
        if (messageBar) {
            messageBar.hidden = true;
        }
    }

    static success(message, duration = 3000) {
        this.show(message, 'success', duration);
    }

    static error(message, duration = 7000) {
        this.show(message, 'error', duration);
    }

    static warning(message, duration = 5000) {
        this.show(message, 'warning', duration);
    }

    static info(message, duration = 4000) {
        this.show(message, 'info', duration);
    }
}

// Export for use in other modules
window.WeatherAPI = WeatherAPI;
window.APIError = APIError;
window.ProgressIndicator = ProgressIndicator;
window.MessageBar = MessageBar;
