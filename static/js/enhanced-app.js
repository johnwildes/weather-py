// Enhanced Weather App - Phase 4 Integration
// Main application class with state management and API integration

class EnhancedWeatherApp {
    constructor() {
        // Initialize Phase 4 modules
        this.stateManager = new StateManager();
        this.weatherAPI = new WeatherAPI();
        
        // UI elements cache
        this.elements = {};
        
        // Debounce timers
        this.autocompleteTimeout = null;
        this.refreshTimeout = null;
        
        this.init();
    }

    async init() {
        await this.initializeElements();
        this.setupEventListeners();
        this.setupStateListeners();
        this.loadInitialData();
        
        // Load weather data for existing locations
        const selectedLocations = this.stateManager.getSelectedLocations();
        if (selectedLocations.length > 0) {
            await this.refreshWeatherData(selectedLocations);
        }
    }

    initializeElements() {
        // Cache commonly used DOM elements
        this.elements = {
            zipcodeInput: document.getElementById('zipcodeInput'),
            addLocationBtn: document.getElementById('addLocationBtn'),
            currentLocationBtn: document.getElementById('currentLocationBtn'),
            refreshBtn: document.getElementById('refreshBtn'),
            clearAllBtn: document.getElementById('clearAllBtn'),
            locationBadges: document.getElementById('locationBadges'),
            weatherCards: document.getElementById('weatherCards'),
            messageBar: document.getElementById('messageBar'),
            autocompleteDropdown: document.getElementById('autocompleteDropdown'),
            autocompleteResults: document.getElementById('autocompleteResults'),
            locationCount: document.getElementById('locationCount'),
            tempUnitToggle: document.getElementById('tempUnitToggle'),
            viewToggle: document.getElementById('viewToggle')
        };
    }

    setupEventListeners() {
        // Location input events
        if (this.elements.zipcodeInput) {
            this.elements.zipcodeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.addLocation();
                }
            });

            this.elements.zipcodeInput.addEventListener('input', (e) => {
                this.handleAutocomplete(e.target.value);
            });

            this.elements.zipcodeInput.addEventListener('blur', () => {
                setTimeout(() => this.hideAutocomplete(), 150);
            });
        }

        // Button events
        if (this.elements.addLocationBtn) {
            this.elements.addLocationBtn.addEventListener('click', () => this.addLocation());
        }

        if (this.elements.currentLocationBtn) {
            this.elements.currentLocationBtn.addEventListener('click', () => this.addCurrentLocation());
        }

        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => this.refreshAllWeatherData());
        }

        if (this.elements.clearAllBtn) {
            this.elements.clearAllBtn.addEventListener('click', () => this.clearAllLocations());
        }

        // Temperature unit toggle
        if (this.elements.tempUnitToggle) {
            this.elements.tempUnitToggle.addEventListener('change', (e) => {
                this.stateManager.updatePreference('tempUnit', e.target.checked ? 'fahrenheit' : 'celsius');
            });
        }

        // View toggle
        if (this.elements.viewToggle) {
            this.elements.viewToggle.addEventListener('change', (e) => {
                this.stateManager.setActiveView(e.target.checked ? 'table' : 'grid');
            });
        }

        // Global click handler
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.location-input-container')) {
                this.hideAutocomplete();
            }
        });

        // Message bar events
        if (this.elements.messageBar) {
            this.elements.messageBar.addEventListener('dismiss', () => {
                this.elements.messageBar.hidden = true;
            });
        }
    }

    setupStateListeners() {
        // Location changes
        this.stateManager.on('selectedLocationsChanged', (locations) => {
            this.updateLocationBadges();
            this.updateLocationCount();
            this.updateRefreshButton();
        });

        this.stateManager.on('locationAdded', ({ location, displayName }) => {
            this.refreshWeatherData([location]);
            MessageBar.success(`Added ${displayName || location}`);
            this.clearInput();
        });

        this.stateManager.on('locationRemoved', ({ location }) => {
            MessageBar.info(`Removed ${location}`);
        });

        this.stateManager.on('weatherDataUpdated', ({ location, data }) => {
            this.updateWeatherCard(location, data);
        });

        this.stateManager.on('bulkWeatherDataUpdated', (weatherData) => {
            this.updateAllWeatherCards();
        });

        this.stateManager.on('loadingStateChanged', ({ isLoading, message }) => {
            if (isLoading) {
                ProgressIndicator.show(message);
                this.setButtonStates(true);
            } else {
                ProgressIndicator.hide();
                this.setButtonStates(false);
            }
        });

        this.stateManager.on('preferenceChanged', ({ key, value }) => {
            if (key === 'tempUnit') {
                this.updateTemperatureUnit(value);
            }
        });

        this.stateManager.on('activeViewChanged', (view) => {
            this.updateViewDisplay(view);
        });

        this.stateManager.on('autoRefreshTriggered', () => {
            this.refreshAllWeatherData(true);
        });
    }

    loadInitialData() {
        // Update UI with initial state
        this.updateLocationBadges();
        this.updateLocationCount();
        this.updateRefreshButton();
        
        // Set initial temp unit toggle
        const preferences = this.stateManager.getUserPreferences();
        if (this.elements.tempUnitToggle) {
            this.elements.tempUnitToggle.checked = preferences.tempUnit === 'fahrenheit';
        }
    }

    // Location Management
    async addLocation() {
        const input = this.elements.zipcodeInput;
        if (!input) return;

        const location = input.value.trim();
        if (!location) {
            MessageBar.warning('Please enter a location');
            return;
        }

        try {
            this.stateManager.setLoading(true, 'Validating location...');

            // Validate location first
            const validation = await this.weatherAPI.validateLocation(location);
            
            if (!validation.valid) {
                MessageBar.error(`Invalid location: ${location}`);
                return;
            }

            // Add to state manager
            const added = this.stateManager.addLocation(location, validation.displayName);
            
            if (!added) {
                MessageBar.warning('Location already added');
            }

        } catch (error) {
            console.error('Error adding location:', error);
            if (error instanceof APIError) {
                MessageBar.error(`Error: ${error.message}`);
            } else {
                MessageBar.error('Failed to add location. Please try again.');
            }
        } finally {
            this.stateManager.setLoading(false);
        }
    }

    async addCurrentLocation() {
        if (!navigator.geolocation) {
            MessageBar.error('Geolocation is not supported by this browser');
            return;
        }

        try {
            this.stateManager.setLoading(true, 'Getting your location...');

            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    timeout: 10000,
                    enableHighAccuracy: true
                });
            });

            const { latitude, longitude } = position.coords;
            const coordinates = `${latitude},${longitude}`;

            // Validate and add the coordinates
            const validation = await this.weatherAPI.validateLocation(coordinates);
            
            if (validation.valid) {
                const added = this.stateManager.addLocation(coordinates, validation.displayName);
                if (!added) {
                    MessageBar.warning('Current location already added');
                }
            } else {
                MessageBar.error('Unable to determine your location');
            }

        } catch (error) {
            console.error('Geolocation error:', error);
            if (error.code === error.PERMISSION_DENIED) {
                MessageBar.error('Location permission denied');
            } else if (error.code === error.TIMEOUT) {
                MessageBar.error('Location request timed out');
            } else {
                MessageBar.error('Unable to get your location');
            }
        } finally {
            this.stateManager.setLoading(false);
        }
    }

    removeLocation(location) {
        this.stateManager.removeLocation(location);
    }

    clearAllLocations() {
        // Close the menu first
        this.closeMoreActionsMenu();
        
        if (this.stateManager.getSelectedLocations().length === 0) {
            MessageBar.info('No locations to clear');
            return;
        }

        // Show confirmation dialog
        if (confirm('Are you sure you want to remove all locations?')) {
            this.stateManager.clearAllLocations();
            MessageBar.success('All locations cleared');
        }
    }

    // Weather Data Management
    async refreshWeatherData(locations = null) {
        const locationsToRefresh = locations || this.stateManager.getSelectedLocations();
        
        if (locationsToRefresh.length === 0) {
            return;
        }

        try {
            this.stateManager.setLoading(true, `Loading weather data for ${locationsToRefresh.length} location(s)...`);

            // Use bulk API for multiple locations
            if (locationsToRefresh.length > 1) {
                const result = await this.weatherAPI.getBulkWeatherWithProgress(
                    locationsToRefresh,
                    (completed, total) => {
                        ProgressIndicator.update(`Loading weather data: ${completed}/${total}`);
                    }
                );

                if (result.results) {
                    // Handle individual results
                    for (const item of result.results) {
                        if (item.success) {
                            this.stateManager.setWeatherData(item.location, item.data);
                        } else {
                            console.error(`Failed to load weather for ${item.location}:`, item.error);
                            MessageBar.error(`Failed to load weather for ${item.location}`);
                        }
                    }
                } else {
                    // Handle bulk response
                    this.stateManager.setBulkWeatherData(result);
                }
            } else {
                // Single location
                const location = locationsToRefresh[0];
                const data = await this.weatherAPI.getCurrentWeather(location);
                this.stateManager.setWeatherData(location, data);
            }

        } catch (error) {
            console.error('Error refreshing weather data:', error);
            MessageBar.error('Failed to refresh weather data');
        } finally {
            this.stateManager.setLoading(false);
        }
    }

    async refreshAllWeatherData(isAutoRefresh = false) {
        const selectedLocations = this.stateManager.getSelectedLocations();
        
        if (selectedLocations.length === 0) {
            if (!isAutoRefresh) {
                MessageBar.info('No locations selected');
            }
            return;
        }

        await this.refreshWeatherData();
        
        if (!isAutoRefresh) {
            MessageBar.success('Weather data refreshed');
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
        const resultsContainer = this.elements.autocompleteResults;
        
        if (!dropdown || !resultsContainer) return;

        if (results.length === 0) {
            this.hideAutocomplete();
            return;
        }

        resultsContainer.innerHTML = '';
        
        results.forEach((result, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = `
                <div class="autocomplete-main">
                    <span class="autocomplete-name">${result.name}</span>
                    <span class="autocomplete-region">${result.region}, ${result.country}</span>
                </div>
                <div class="autocomplete-meta">
                    ${result.lat}, ${result.lon}
                </div>
            `;
            
            item.addEventListener('click', () => {
                this.selectAutocompleteItem(result);
            });
            
            resultsContainer.appendChild(item);
        });
        
        dropdown.hidden = false;
    }

    hideAutocomplete() {
        const dropdown = this.elements.autocompleteDropdown;
        if (dropdown) {
            dropdown.hidden = true;
        }
    }

    selectAutocompleteItem(result) {
        const input = this.elements.zipcodeInput;
        if (input) {
            input.value = result.name;
        }
        this.hideAutocomplete();
        this.addLocation();
    }

    // UI Updates
    updateLocationBadges() {
        const container = this.elements.locationBadges;
        if (!container) return;

        const selectedLocations = this.stateManager.getSelectedLocations();
        const pinnedLocations = this.stateManager.getPinnedLocations();

        container.innerHTML = '';

        selectedLocations.forEach(location => {
            const badge = document.createElement('fluent-badge');
            badge.className = 'location-badge';
            badge.innerHTML = `
                <span class="badge-text">${location}</span>
                <fluent-button appearance="stealth" size="small" class="remove-btn" 
                              onclick="window.weatherApp.removeLocation('${location}')">
                    <fluent-icon name="Dismiss16Regular"></fluent-icon>
                </fluent-button>
                ${pinnedLocations.includes(location) ? 
                    '<fluent-icon name="Pin16Filled" class="pin-icon"></fluent-icon>' : 
                    '<fluent-button appearance="stealth" size="small" class="pin-btn" onclick="window.weatherApp.togglePin(\'' + location + '\')"><fluent-icon name="Pin16Regular"></fluent-icon></fluent-button>'
                }
            `;
            container.appendChild(badge);
        });
    }

    updateLocationCount() {
        const countElement = this.elements.locationCount;
        if (countElement) {
            const selectedCount = this.stateManager.getSelectedLocations().length;
            const maxCount = this.stateManager.getUserPreferences().maxLocations;
            countElement.textContent = `${selectedCount}/${maxCount}`;
        }
    }

    updateRefreshButton() {
        const refreshBtn = this.elements.refreshBtn;
        if (refreshBtn) {
            const hasLocations = this.stateManager.getSelectedLocations().length > 0;
            refreshBtn.disabled = !hasLocations;
        }
    }

    updateWeatherCard(location, data) {
        // This will be implemented based on the specific card structure
        const weatherCards = this.elements.weatherCards;
        if (!weatherCards) return;

        let card = weatherCards.querySelector(`[data-location="${location}"]`);
        
        if (!card) {
            card = this.createWeatherCard(location, data);
            weatherCards.appendChild(card);
        } else {
            this.updateExistingCard(card, data);
        }
    }

    updateAllWeatherCards() {
        const selectedLocations = this.stateManager.getSelectedLocations();
        const weatherCards = this.elements.weatherCards;
        
        if (!weatherCards) return;

        // Remove cards for locations no longer selected
        const existingCards = weatherCards.querySelectorAll('[data-location]');
        existingCards.forEach(card => {
            const location = card.dataset.location;
            if (!selectedLocations.includes(location)) {
                card.remove();
            }
        });

        // Update/create cards for selected locations
        selectedLocations.forEach(location => {
            const data = this.stateManager.getWeatherData(location);
            if (data) {
                this.updateWeatherCard(location, data);
            }
        });
    }

    createWeatherCard(location, data) {
        const card = document.createElement('fluent-card');
        card.className = 'weather-card';
        card.dataset.location = location;
        
        // This will create the weather card HTML based on data
        card.innerHTML = this.generateWeatherCardHTML(location, data);
        
        return card;
    }

    updateExistingCard(card, data) {
        // Update the existing card with new data
        card.innerHTML = this.generateWeatherCardHTML(card.dataset.location, data);
    }

    generateWeatherCardHTML(location, data) {
        // Generate weather card HTML - this will be customized based on the data structure
        return `
            <div class="weather-card-header">
                <h3>${data.location?.name || location}</h3>
                <div class="weather-actions">
                    <fluent-button appearance="stealth" size="small" onclick="window.weatherApp.toggleFavorite('${location}')">
                        <fluent-icon name="${this.stateManager.isFavorite(location) ? 'Heart24Filled' : 'Heart24Regular'}"></fluent-icon>
                    </fluent-button>
                </div>
            </div>
            <div class="weather-content">
                <div class="current-weather">
                    <div class="temperature">${data.current?.temp_c || ''}°C</div>
                    <div class="condition">${data.current?.condition?.text || ''}</div>
                </div>
                <div class="weather-icon">
                    <img src="https:${data.current?.condition?.icon || ''}" alt="${data.current?.condition?.text || ''}" />
                </div>
            </div>
            <div class="weather-details">
                <div class="detail-item">
                    <span>Humidity:</span>
                    <span>${data.current?.humidity || ''}%</span>
                </div>
                <div class="detail-item">
                    <span>Wind:</span>
                    <span>${data.current?.wind_kph || ''} km/h</span>
                </div>
            </div>
        `;
    }

    // Utility methods
    clearInput() {
        if (this.elements.zipcodeInput) {
            this.elements.zipcodeInput.value = '';
        }
    }

    setButtonStates(loading) {
        const buttons = [
            this.elements.addLocationBtn,
            this.elements.currentLocationBtn,
            this.elements.refreshBtn,
            this.elements.clearAllBtn
        ];

        buttons.forEach(btn => {
            if (btn) {
                btn.disabled = loading;
            }
        });
    }

    toggleFavorite(location) {
        if (this.stateManager.isFavorite(location)) {
            this.stateManager.removeFromFavorites(location);
        } else {
            this.stateManager.addToFavorites(location);
        }
        this.updateAllWeatherCards();
    }

    togglePin(location) {
        this.stateManager.togglePin(location);
        this.updateLocationBadges();
    }

    updateTemperatureUnit(unit) {
        // Update all weather cards to show new temperature unit
        this.updateAllWeatherCards();
    }

    updateViewDisplay(view) {
        const weatherCards = this.elements.weatherCards;
        if (weatherCards) {
            weatherCards.className = `weather-cards ${view}-view`;
        }
    }

    // Export/Import functionality
    exportSettings() {
        // Close the menu first
        this.closeMoreActionsMenu();
        
        const data = this.stateManager.exportData();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `weather-app-settings-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        MessageBar.success('Settings exported successfully');
    }

    async importSettings(file) {
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            if (this.stateManager.importData(data)) {
                MessageBar.success('Settings imported successfully');
                this.loadInitialData();
                await this.refreshAllWeatherData();
            } else {
                MessageBar.error('Failed to import settings');
            }
        } catch (error) {
            console.error('Import error:', error);
            MessageBar.error('Invalid settings file');
        }
    }

    // Helper to close the More Actions menu
    closeMoreActionsMenu() {
        const menu = document.getElementById('moreActionsMenu');
        if (menu && typeof menu.closeMenu === 'function') {
            menu.closeMenu();
        }
    }
}

// Initialize the enhanced app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we have the required modules
    if (typeof StateManager !== 'undefined' && typeof WeatherAPI !== 'undefined') {
        window.weatherApp = new EnhancedWeatherApp();
    } else {
        console.error('Phase 4 modules not loaded. Falling back to basic app.');
        // Fallback to original WeatherApp if needed
        if (typeof WeatherApp !== 'undefined') {
            window.weatherApp = new WeatherApp();
        }
    }
});

// Export for global access
window.EnhancedWeatherApp = EnhancedWeatherApp;
