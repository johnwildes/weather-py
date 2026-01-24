// Weather App - Main Application JavaScript
// Handles search functionality, recent cities bar, and 10-day forecast display

class WeatherApp {
    constructor() {
        this.stateManager = new StateManager();
        this.weatherAPI = new WeatherAPI();
        this.chatAgent = null;
        this.elements = {};
        this.autocompleteTimeout = null;
        this.init();
    }

    init() {
        this.cacheElements();
        this.setupEventListeners();
        this.loadRecentCities();
        this.disableAutofillOnSearch();
        this.storeCurrentWeatherData();
        this.initializeChatAgent();
    }

    storeCurrentWeatherData() {
        // Store server-rendered weather data in state manager for chat agent
        if (window.currentWeatherData) {
            const data = window.currentWeatherData;
            const locationKey = data.location.name;
            
            // Store the weather data in state manager
            this.stateManager.setWeatherData(locationKey, data);
            
            // Set as the currently selected/viewed location
            this.stateManager.setSelectedLocation(locationKey);
            
            // Also store the full display name
            const displayName = [data.location.name, data.location.region, data.location.country]
                .filter(Boolean)
                .join(', ');
            
            // Add to recent locations for context
            this.stateManager.addToRecentLocations(locationKey, displayName);
        }
    }

    initializeChatAgent() {
        // Initialize chat agent if ChatAgent class is available
        if (window.ChatAgent) {
            this.chatAgent = new ChatAgent(this.stateManager);
        }
    }

    // Disable password manager autofill on search input
    disableAutofillOnSearch() {
        const searchField = this.elements.locationSearch;
        if (searchField) {
            // Wait for the fluent component to fully render
            requestAnimationFrame(() => {
                // Try to access the shadow DOM input
                const shadowInput = searchField.shadowRoot?.querySelector('input');
                if (shadowInput) {
                    shadowInput.setAttribute('autocomplete', 'off');
                    shadowInput.setAttribute('type', 'search');
                    shadowInput.setAttribute('data-1p-ignore', '');
                    shadowInput.setAttribute('data-lpignore', 'true');
                    shadowInput.setAttribute('data-form-type', 'other');
                    shadowInput.setAttribute('name', 'weather-search-' + Date.now());
                }
                // Also set on the control property if available
                if (searchField.control) {
                    searchField.control.setAttribute('autocomplete', 'off');
                    searchField.control.setAttribute('type', 'search');
                    searchField.control.setAttribute('data-1p-ignore', '');
                    searchField.control.setAttribute('data-lpignore', 'true');
                    searchField.control.setAttribute('data-form-type', 'other');
                }
            });
        }
    }

    cacheElements() {
        this.elements = {
            locationSearch: document.getElementById('locationSearch'),
            searchBtn: document.getElementById('searchBtn'),
            autocompleteDropdown: document.getElementById('autocompleteDropdown'),
            autocompleteResults: document.getElementById('autocompleteResults'),
            recentCitiesSection: document.getElementById('recentCitiesSection'),
            recentCitiesList: document.getElementById('recentCitiesList'),
            forecastContent: document.getElementById('forecastContent'),
            messageBar: document.getElementById('messageBar'),
            messageText: document.getElementById('messageText')
        };
    }

    setupEventListeners() {
        // Search input events
        if (this.elements.locationSearch) {
            this.elements.locationSearch.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.searchLocation();
                }
            });

            this.elements.locationSearch.addEventListener('input', (e) => {
                this.handleAutocomplete(e.target.value);
            });

            this.elements.locationSearch.addEventListener('blur', () => {
                setTimeout(() => this.hideAutocomplete(), 275);
            });
        }

        // Search button click
        if (this.elements.searchBtn) {
            this.elements.searchBtn.addEventListener('click', () => this.searchLocation());
        }

        // Global click to close autocomplete
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-input-wrapper')) {
                this.hideAutocomplete();
            }
        });
    }

    // Search functionality
    async searchLocation() {
        const input = this.elements.locationSearch;
        if (!input) return;

        const query = input.value.trim();
        if (!query) {
            this.showMessage('Please enter a city name or zip code', 'warning');
            return;
        }

        try {
            this.setLoading(true);

            // Validate and get weather data
            const validation = await this.weatherAPI.validateLocation(query);
            
            if (!validation.valid) {
                this.showMessage(`Location "${query}" not found`, 'error');
                return;
            }

            // Add to recent cities
            this.addToRecentCities(query, validation.location?.name || query);

            // Navigate to show weather data
            window.location.href = `/?location=${encodeURIComponent(query)}`;

        } catch (error) {
            console.error('Search error:', error);
            this.showMessage('Failed to search location. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    // Autocomplete functionality
    async handleAutocomplete(query) {
        if (this.autocompleteTimeout) {
            clearTimeout(this.autocompleteTimeout);
        }

        if (!query || query.length < 2) {
            this.hideAutocomplete();
            return;
        }

        this.autocompleteTimeout = setTimeout(async () => {
            try {
                const results = await this.weatherAPI.searchLocations(query);
                this.showAutocomplete(results);
            } catch (error) {
                console.error('Autocomplete error:', error);
                this.hideAutocomplete();
            }
        }, 300);
    }

    showAutocomplete(results) {
        const dropdown = this.elements.autocompleteDropdown;
        const container = this.elements.autocompleteResults;
        const searchInput = this.elements.locationSearch;
        
        if (!dropdown || !container) return;

        if (!results || results.length === 0) {
            this.hideAutocomplete();
            return;
        }

        // Position dropdown below the search input
        if (searchInput) {
            const inputRect = searchInput.getBoundingClientRect();
            const containerRect = dropdown.parentElement.getBoundingClientRect();
            dropdown.style.top = (inputRect.bottom - containerRect.top + 4) + 'px';
            dropdown.style.left = (inputRect.left - containerRect.left) + 'px';
            dropdown.style.width = inputRect.width + 'px';
        }

        container.innerHTML = '';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';

            const mainDiv = document.createElement('div');
            mainDiv.className = 'autocomplete-main';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'autocomplete-name';
            nameSpan.textContent = result.name || '';

            mainDiv.appendChild(nameSpan);

            const subDiv = document.createElement('div');
            subDiv.className = 'autocomplete-sub';

            let subText = '';
            if (result.region) {
                subText += result.region + ', ';
            }
            if (result.country) {
                subText += result.country;
            }
            subDiv.textContent = subText;

            item.appendChild(mainDiv);
            item.appendChild(subDiv);
            
            item.addEventListener('click', () => {
                this.selectAutocompleteItem(result);
            });
            
            container.appendChild(item);
        });
        
        dropdown.hidden = false;
    }

    hideAutocomplete() {
        if (this.elements.autocompleteDropdown) {
            this.elements.autocompleteDropdown.hidden = true;
        }
    }

    selectAutocompleteItem(result) {
        if (this.elements.locationSearch) {
            this.elements.locationSearch.value = result.name;
        }
        this.hideAutocomplete();
        this.searchLocation();
    }

    // Recent cities functionality
    addToRecentCities(query, displayName) {
        const recentCities = this.getRecentCities();
        
        // Remove if already exists
        const filteredCities = recentCities.filter(city => 
            city.query.toLowerCase() !== query.toLowerCase()
        );
        
        // Add to beginning
        filteredCities.unshift({
            query: query,
            displayName: displayName,
            timestamp: Date.now()
        });
        
        // Keep only last 10
        const limitedCities = filteredCities.slice(0, 10);
        
        try {
            localStorage.setItem('weather_recent_cities', JSON.stringify(limitedCities));
            this.loadRecentCities();
        } catch (e) {
            // Gracefully handle storage failures (QuotaExceededError, SecurityError, etc.)
            // Continue to update UI with in-memory data even if localStorage is unavailable
            console.warn('Failed to save recent cities to localStorage:', e);
            this.loadRecentCities(limitedCities);
        }
    }

    getRecentCities() {
        try {
            const stored = localStorage.getItem('weather_recent_cities');
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    loadRecentCities(cities) {
        const recentCities = cities || this.getRecentCities();
        const section = this.elements.recentCitiesSection;
        const list = this.elements.recentCitiesList;
        
        if (!section || !list) return;

        // Show recent cities bar only when 2+ cities have been searched
        if (recentCities.length >= 2) {
            section.style.display = 'block';
            
            list.innerHTML = '';
            recentCities.slice(0, 5).forEach(city => {
                const badge = document.createElement('fluent-badge');
                badge.className = 'recent-city-badge';
                badge.setAttribute('appearance', 'outline');
                badge.innerHTML = `
                    <span class="badge-text">${city.displayName}</span>
                `;
                badge.style.cursor = 'pointer';
                badge.addEventListener('click', () => {
                    if (this.elements.locationSearch) {
                        this.elements.locationSearch.value = city.query;
                    }
                    this.searchLocation();
                });
                list.appendChild(badge);
            });
        } else {
            section.style.display = 'none';
        }
    }

    // UI helpers
    setLoading(isLoading) {
        if (this.elements.searchBtn) {
            this.elements.searchBtn.disabled = isLoading;
        }
        if (this.elements.locationSearch) {
            this.elements.locationSearch.disabled = isLoading;
        }
    }

    showMessage(message, type = 'info') {
        const messageBar = this.elements.messageBar;
        const messageText = this.elements.messageText;
        
        if (messageBar && messageText) {
            messageBar.setAttribute('intent', type);
            messageText.textContent = message;
            messageBar.hidden = false;
            
            setTimeout(() => {
                messageBar.hidden = true;
            }, 5000);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.weatherApp = new WeatherApp();
});
