// Weather App - Core JavaScript Module
class WeatherApp {
    constructor() {
        this.selectedLocations = this.loadSelectedLocations();
        this.recentLocations = this.loadRecentLocations();
        this.favoriteLocations = this.loadFavoriteLocations();
        this.pinnedLocations = this.loadPinnedLocations();
        this.locationPresets = this.loadLocationPresets();
        this.tempUnit = localStorage.getItem('tempUnit') || 'celsius';
        this.autocompleteTimeout = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateLocationBadges();
        this.populateRecentLocations();
        this.populateFavoriteLocations();
        this.updateRefreshButton();
        this.updateLocationCount();
    }

    setupEventListeners() {
        // Enter key support for location input
        const zipcodeInput = document.getElementById('zipcodeInput');
        if (zipcodeInput) {
            zipcodeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addLocation();
                }
            });
            
            // Autocomplete on input
            zipcodeInput.addEventListener('input', (e) => {
                this.handleAutocomplete(e.target.value);
            });
            
            // Hide dropdown on blur
            zipcodeInput.addEventListener('blur', () => {
                setTimeout(() => this.hideAutocomplete(), 150);
            });
        }

        // Message bar auto-hide
        const messageBar = document.getElementById('messageBar');
        if (messageBar) {
            messageBar.addEventListener('dismiss', () => {
                messageBar.hidden = true;
            });
        }

        // Global click handler to close autocomplete
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.location-input-container')) {
                this.hideAutocomplete();
            }
            
            // Close Fluent UI menus when clicking outside
            if (!e.target.closest('fluent-menu') && !e.target.closest('fluent-menu-button')) {
                document.querySelectorAll('fluent-menu').forEach(menu => {
                    if (typeof menu.closeMenu === 'function') {
                        menu.closeMenu();
                    }
                });
            }
        });
    }

    // Enhanced Autocomplete Functionality
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
                const response = await fetch(`/api/search-locations?q=${encodeURIComponent(query)}`);
                if (response.ok) {
                    const results = await response.json();
                    this.showAutocomplete(results);
                }
            } catch (error) {
                console.error('Autocomplete error:', error);
            }
        }, 300);
    }

    showAutocomplete(results) {
        const dropdown = document.getElementById('autocompleteDropdown');
        const resultsContainer = document.getElementById('autocompleteResults');
        
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
                <div class="autocomplete-main">${result.name}</div>
                <div class="autocomplete-sub">${result.region}, ${result.country}</div>
            `;
            
            item.addEventListener('click', () => {
                this.selectAutocompleteItem(result.display);
            });
            
            // Keyboard navigation
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.selectAutocompleteItem(result.display);
                }
            });
            
            resultsContainer.appendChild(item);
        });

        dropdown.hidden = false;
    }

    selectAutocompleteItem(location) {
        const input = document.getElementById('zipcodeInput');
        if (input) {
            input.value = location;
        }
        this.hideAutocomplete();
        this.addLocation(location);
    }

    hideAutocomplete() {
        const dropdown = document.getElementById('autocompleteDropdown');
        if (dropdown) {
            dropdown.hidden = true;
        }
    }

    // Favorites Management
    toggleFavorite(location) {
        const index = this.favoriteLocations.findIndex(fav => fav.location === location);
        const starIcon = document.getElementById(`star-${location.replace(' ', '-')}`);
        
        if (index > -1) {
            // Remove from favorites
            this.favoriteLocations.splice(index, 1);
            if (starIcon) {
                starIcon.setAttribute('name', 'Star24Regular');
                starIcon.parentElement.classList.remove('active');
            }
            this.showMessage(`Removed ${location} from favorites`, 'info');
        } else {
            // Add to favorites
            this.favoriteLocations.push({
                location: location,
                addedAt: new Date().toISOString()
            });
            if (starIcon) {
                starIcon.setAttribute('name', 'StarFill24Regular');
                starIcon.parentElement.classList.add('active');
            }
            this.showMessage(`Added ${location} to favorites`, 'success');
        }
        
        this.saveFavoriteLocations();
        this.populateFavoriteLocations();
        this.updateLocationBadges();
    }

    pinToTop(location) {
        const index = this.pinnedLocations.indexOf(location);
        if (index === -1) {
            this.pinnedLocations.push(location);
            this.showMessage(`Pinned ${location} to top`, 'success');
        } else {
            this.pinnedLocations.splice(index, 1);
            this.showMessage(`Unpinned ${location}`, 'info');
        }
        this.savePinnedLocations();
        this.updateLocationBadges();
        this.sortLocationsByPriority();
    }

    sortLocationsByPriority() {
        // Sort selected locations: pinned first, then favorites, then regular
        this.selectedLocations.sort((a, b) => {
            const aPinned = this.pinnedLocations.includes(a);
            const bPinned = this.pinnedLocations.includes(b);
            const aFavorite = this.favoriteLocations.some(fav => fav.location === a);
            const bFavorite = this.favoriteLocations.some(fav => fav.location === b);
            
            if (aPinned && !bPinned) return -1;
            if (!aPinned && bPinned) return 1;
            if (aFavorite && !bFavorite) return -1;
            if (!aFavorite && bFavorite) return 1;
            return 0;
        });
        
        this.saveSelectedLocations();
        this.updateLocationBadges();
    }

    // Preset Management
    saveLocationPreset() {
        if (this.selectedLocations.length === 0) {
            this.showMessage('No locations to save as preset', 'warning');
            return;
        }

        const presetName = prompt('Enter a name for this preset:');
        if (!presetName || presetName.trim() === '') {
            return;
        }

        const preset = {
            name: presetName.trim(),
            locations: [...this.selectedLocations],
            createdAt: new Date().toISOString()
        };

        // Check if preset name already exists
        const existingIndex = this.locationPresets.findIndex(p => p.name === preset.name);
        if (existingIndex > -1) {
            if (!confirm(`Preset "${preset.name}" already exists. Overwrite?`)) {
                return;
            }
            this.locationPresets[existingIndex] = preset;
        } else {
            this.locationPresets.push(preset);
        }

        this.saveLocationPresets();
        this.showMessage(`Saved preset "${preset.name}"`, 'success');
    }

    loadLocationPreset(presetName) {
        const preset = this.locationPresets.find(p => p.name === presetName);
        if (!preset) {
            this.showMessage('Preset not found', 'error');
            return;
        }

        // Replace current locations with preset locations
        this.selectedLocations = [...preset.locations];
        this.saveSelectedLocations();
        this.updateLocationBadges();
        this.updateRefreshButton();
        this.updateLocationCount();
        
        // Refresh weather data
        if (this.selectedLocations.length > 0) {
            this.refreshWeatherData();
        }

        this.showMessage(`Loaded preset "${preset.name}"`, 'success');
    }

    // Enhanced Location Management
    addLocation(location = null) {
        const input = document.getElementById('zipcodeInput');
        const locationValue = location || input?.value?.trim();
        
        if (!locationValue) {
            this.showMessage('Please enter a location', 'warning');
            return;
        }

        if (this.selectedLocations.includes(locationValue)) {
            this.showMessage('Location already added', 'warning');
            return;
        }

        this.showLoading(true);
        
        // Validate location with API
        this.validateLocation(locationValue)
            .then(isValid => {
                if (isValid) {
                    this.selectedLocations.push(locationValue);
                    this.addToRecentLocations(locationValue);
                    this.saveSelectedLocations();
                    this.sortLocationsByPriority();
                    this.updateLocationBadges();
                    this.updateRefreshButton();
                    this.updateLocationCount();
                    
                    if (input) input.value = '';
                    this.showMessage(`Added ${locationValue}`, 'success');
                    
                    // Auto-refresh if this is the first location or user preference
                    if (this.selectedLocations.length === 1) {
                        setTimeout(() => this.refreshWeatherData(), 500);
                    }
                } else {
                    this.showMessage('Invalid location. Please try again.', 'error');
                }
            })
            .catch(error => {
                console.error('Location validation error:', error);
                this.showMessage('Error validating location', 'error');
            })
            .finally(() => {
                this.showLoading(false);
            });
    }

    removeLocation(location) {
        const index = this.selectedLocations.indexOf(location);
        if (index > -1) {
            this.selectedLocations.splice(index, 1);
            this.saveSelectedLocations();
            this.updateLocationBadges();
            this.updateRefreshButton();
            this.updateLocationCount();
            this.showMessage(`Removed ${location}`, 'info');
            
            // Remove weather card if on forecast page
            const weatherCard = document.querySelector(`[data-location="${location}"]`);
            if (weatherCard) {
                weatherCard.remove();
            }
            
            // Show empty state if no locations left
            if (this.selectedLocations.length === 0) {
                this.showEmptyState();
            }
        }
    }

    clearAllLocations() {
        if (this.selectedLocations.length === 0) {
            this.showMessage('No locations to clear', 'info');
            return;
        }

        const count = this.selectedLocations.length;
        this.selectedLocations = [];
        this.saveSelectedLocations();
        this.updateLocationBadges();
        this.updateRefreshButton();
        this.updateLocationCount();
        this.showMessage(`Cleared ${count} locations`, 'info');
        
        // Clear weather grid if on forecast page
        const weatherGrid = document.getElementById('weatherGrid');
        if (weatherGrid) {
            this.showEmptyState();
        }
    }

    selectRecentLocation(location) {
        if (location) {
            this.addLocation(location);
        }
    }

    selectFavoriteLocation(location) {
        if (location) {
            this.addLocation(location);
        }
    }

    // Enhanced UI Updates
    updateLocationBadges() {
        const container = document.getElementById('locationBadges');
        if (!container) return;

        container.innerHTML = '';
        
        if (this.selectedLocations.length === 0) {
            container.innerHTML = '<span class="no-locations">No locations selected</span>';
            return;
        }

        // Sort locations by priority (pinned, favorites, regular)
        const sortedLocations = [...this.selectedLocations].sort((a, b) => {
            const aPinned = this.pinnedLocations.includes(a);
            const bPinned = this.pinnedLocations.includes(b);
            const aFavorite = this.favoriteLocations.some(fav => fav.location === a);
            const bFavorite = this.favoriteLocations.some(fav => fav.location === b);
            
            if (aPinned && !bPinned) return -1;
            if (!aPinned && bPinned) return 1;
            if (aFavorite && !bFavorite) return -1;
            if (!aFavorite && bFavorite) return 1;
            return 0;
        });

        sortedLocations.forEach(location => {
            const badge = document.createElement('div');
            const isPinned = this.pinnedLocations.includes(location);
            const isFavorite = this.favoriteLocations.some(fav => fav.location === location);
            
            badge.className = `location-badge ${isPinned ? 'pinned' : ''} ${isFavorite ? 'favorite' : ''}`;
            badge.innerHTML = `
                <span>${location}</span>
                <fluent-button 
                    appearance="stealth" 
                    onclick="app.removeLocation('${location}')"
                    title="Remove ${location}">
                    <fluent-icon name="Dismiss16Regular"></fluent-icon>
                </fluent-button>
            `;
            container.appendChild(badge);
        });
    }

    populateFavoriteLocations() {
        const select = document.getElementById('favoriteLocations');
        if (!select) return;

        // Clear existing options
        select.innerHTML = '<fluent-option value="">Favorite locations</fluent-option>';
        
        this.favoriteLocations.forEach(favorite => {
            const option = document.createElement('fluent-option');
            option.value = favorite.location;
            option.textContent = favorite.location;
            select.appendChild(option);
        });
    }

    updateLocationCount() {
        const countElement = document.getElementById('locationCount');
        if (countElement) {
            const count = this.selectedLocations.length;
            countElement.textContent = `${count} location${count !== 1 ? 's' : ''}`;
        }
    }

    // Import/Export Functionality
    exportLocationData() {
        const data = {
            selectedLocations: this.selectedLocations,
            favoriteLocations: this.favoriteLocations,
            recentLocations: this.recentLocations,
            pinnedLocations: this.pinnedLocations,
            locationPresets: this.locationPresets,
            preferences: {
                tempUnit: this.tempUnit
            },
            exportDate: new Date().toISOString(),
            version: '1.0'
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `weather-app-data-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        this.showMessage('Location data exported successfully', 'success');
    }

    importLocationData() {
        const fileInput = document.getElementById('importFileInput');
        if (fileInput) {
            fileInput.click();
        }
    }

    async handleFileImport(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            // Validate data structure
            if (!data.version || !data.selectedLocations) {
                throw new Error('Invalid file format');
            }
            
            // Import data with user confirmation
            const confirmMessage = `Import will replace current data with:
• ${data.selectedLocations?.length || 0} selected locations
• ${data.favoriteLocations?.length || 0} favorite locations
• ${data.locationPresets?.length || 0} presets

Continue?`;
            
            if (confirm(confirmMessage)) {
                this.selectedLocations = data.selectedLocations || [];
                this.favoriteLocations = data.favoriteLocations || [];
                this.recentLocations = data.recentLocations || [];
                this.pinnedLocations = data.pinnedLocations || [];
                this.locationPresets = data.locationPresets || [];
                
                if (data.preferences?.tempUnit) {
                    this.tempUnit = data.preferences.tempUnit;
                    localStorage.setItem('tempUnit', this.tempUnit);
                }
                
                // Save all data
                this.saveSelectedLocations();
                this.saveFavoriteLocations();
                this.saveRecentLocations();
                this.savePinnedLocations();
                this.saveLocationPresets();
                
                // Update UI
                this.updateLocationBadges();
                this.populateRecentLocations();
                this.populateFavoriteLocations();
                this.updateRefreshButton();
                this.updateLocationCount();
                
                this.showMessage('Location data imported successfully', 'success');
                
                // Auto-refresh weather data if locations exist
                if (this.selectedLocations.length > 0) {
                    setTimeout(() => this.refreshWeatherData(), 1000);
                }
            }
        } catch (error) {
            console.error('Import error:', error);
            this.showMessage('Error importing file. Please check the file format.', 'error');
        }
        
        // Clear file input
        event.target.value = '';
    }

    useCurrentLocation() {
        this.showLoading(true);
        
        if (!navigator.geolocation) {
            this.showMessage('Geolocation is not supported by this browser', 'error');
            this.showLoading(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const location = `${lat},${lon}`;
                this.addLocation(location);
            },
            (error) => {
                console.error('Geolocation error:', error);
                this.showMessage('Unable to get your location', 'error');
                this.showLoading(false);
            }
        );
    }

    // Weather Data Management
    async refreshWeatherData() {
        if (this.selectedLocations.length === 0) {
            this.showMessage('No locations selected', 'warning');
            return;
        }

        this.showLoading(true);
        
        try {
            const response = await fetch('/api/weather/bulk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    locations: this.selectedLocations,
                    tempUnit: this.tempUnit
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const weatherData = await response.json();
            this.updateWeatherDisplay(weatherData);
            this.showMessage('Weather data refreshed', 'success');
            
        } catch (error) {
            console.error('Weather refresh error:', error);
            this.showMessage('Error refreshing weather data', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // API Helpers
    async validateLocation(location) {
        try {
            const response = await fetch(`/api/validate-location?location=${encodeURIComponent(location)}`);
            return response.ok;
        } catch (error) {
            console.error('Location validation error:', error);
            return false;
        }
    }

    // UI Updates
    updateLocationBadges() {
        const container = document.getElementById('locationBadges');
        if (!container) return;

        container.innerHTML = '';
        
        if (this.selectedLocations.length === 0) {
            container.innerHTML = '<span class="no-locations">No locations selected</span>';
            return;
        }

        this.selectedLocations.forEach(location => {
            const badge = document.createElement('div');
            badge.className = 'location-badge';
            badge.innerHTML = `
                <span>${location}</span>
                <fluent-button 
                    appearance="stealth" 
                    onclick="app.removeLocation('${location}')"
                    title="Remove ${location}">
                    <fluent-icon name="Dismiss16Regular"></fluent-icon>
                </fluent-button>
            `;
            container.appendChild(badge);
        });
    }

    populateRecentLocations() {
        const select = document.getElementById('recentLocations');
        if (!select) return;

        // Clear existing options
        select.innerHTML = '<fluent-option value="">Recent locations</fluent-option>';
        
        this.recentLocations.forEach(location => {
            const option = document.createElement('fluent-option');
            option.value = location;
            option.textContent = location;
            select.appendChild(option);
        });
    }

    updateRefreshButton() {
        const refreshBtn = document.getElementById('refreshWeatherBtn');
        if (refreshBtn) {
            refreshBtn.disabled = this.selectedLocations.length === 0;
        }
    }

    updateWeatherDisplay(weatherData) {
        const weatherGrid = document.getElementById('weatherGrid');
        if (!weatherGrid) return;

        if (weatherData.length === 0) {
            this.showEmptyState();
            return;
        }

        // Update existing cards or create new ones
        weatherGrid.innerHTML = '';
        weatherData.forEach(data => {
            const cardContainer = document.createElement('div');
            cardContainer.className = 'weather-card-container fade-in';
            cardContainer.innerHTML = this.createWeatherCardHTML(data);
            weatherGrid.appendChild(cardContainer);
        });
    }

    createWeatherCardHTML(data) {
        // This would be populated with actual weather card HTML
        // For now, return a placeholder
        return `
            <fluent-card class="weather-card" data-location="${data.location.name}">
                <div class="card-header">
                    <div class="location-info">
                        <h3>${data.location.name}</h3>
                        <p>${data.location.region}, ${data.location.country}</p>
                    </div>
                    <fluent-button 
                        appearance="stealth" 
                        onclick="app.removeLocation('${data.location.name}')"
                        class="remove-btn">
                        <fluent-icon name="Dismiss24Regular"></fluent-icon>
                    </fluent-button>
                </div>
                <div class="current-weather">
                    <div class="weather-icon">
                        <img src="${data.current.condition.icon}" alt="${data.current.condition.text}" />
                    </div>
                    <div class="temperature">
                        <span class="temp-value">${data.current.temp_c}°</span>
                        <span class="temp-unit">C</span>
                    </div>
                    <div class="condition">
                        <p class="condition-text">${data.current.condition.text}</p>
                        <p class="feels-like">Feels like ${data.current.feelslike_c}°C</p>
                    </div>
                </div>
            </fluent-card>
        `;
    }

    showEmptyState() {
        const weatherGrid = document.getElementById('weatherGrid');
        if (!weatherGrid) return;

        weatherGrid.innerHTML = `
            <div class="empty-state">
                <fluent-card class="empty-card">
                    <div class="empty-content">
                        <fluent-icon name="WeatherSunny24Regular" class="empty-icon"></fluent-icon>
                        <h3>No Locations Selected</h3>
                        <p>Add locations using the toolbar above to view weather forecasts.</p>
                        <fluent-button 
                            appearance="accent" 
                            onclick="focusLocationInput()">
                            <fluent-icon slot="start" name="Add24Regular"></fluent-icon>
                            Add Your First Location
                        </fluent-button>
                    </div>
                </fluent-card>
            </div>
        `;
    }

    // Utility Functions
    showMessage(message, type = 'info') {
        const messageBar = document.getElementById('messageBar');
        const messageText = document.getElementById('messageText');
        
        if (messageBar && messageText) {
            messageText.textContent = message;
            messageBar.setAttribute('intent', type);
            messageBar.hidden = false;
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                messageBar.hidden = true;
            }, 5000);
        }
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.hidden = !show;
        }
    }

    // Enhanced Local Storage Management
    saveSelectedLocations() {
        localStorage.setItem('selectedLocations', JSON.stringify(this.selectedLocations));
    }

    loadSelectedLocations() {
        try {
            const saved = localStorage.getItem('selectedLocations');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading selected locations:', error);
            return [];
        }
    }

    saveFavoriteLocations() {
        localStorage.setItem('favoriteLocations', JSON.stringify(this.favoriteLocations));
    }

    loadFavoriteLocations() {
        try {
            const saved = localStorage.getItem('favoriteLocations');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading favorite locations:', error);
            return [];
        }
    }

    savePinnedLocations() {
        localStorage.setItem('pinnedLocations', JSON.stringify(this.pinnedLocations));
    }

    loadPinnedLocations() {
        try {
            const saved = localStorage.getItem('pinnedLocations');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading pinned locations:', error);
            return [];
        }
    }

    saveLocationPresets() {
        localStorage.setItem('locationPresets', JSON.stringify(this.locationPresets));
    }

    loadLocationPresets() {
        try {
            const saved = localStorage.getItem('locationPresets');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading location presets:', error);
            return [];
        }
    }

    addToRecentLocations(location) {
        if (!this.recentLocations.includes(location)) {
            this.recentLocations.unshift(location);
            // Keep only last 10 recent locations
            this.recentLocations = this.recentLocations.slice(0, 10);
            this.saveRecentLocations();
            this.populateRecentLocations();
        }
    }

    saveRecentLocations() {
        localStorage.setItem('recentLocations', JSON.stringify(this.recentLocations));
    }

    loadRecentLocations() {
        try {
            const saved = localStorage.getItem('recentLocations');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading recent locations:', error);
            return [];
        }
    }
}

// Enhanced Global Functions (for onclick handlers)
function addLocation() {
    if (window.app) {
        window.app.addLocation();
    }
}

function useCurrentLocation() {
    if (window.app) {
        window.app.useCurrentLocation();
    }
}

function selectRecentLocation(location) {
    if (window.app) {
        window.app.selectRecentLocation(location);
    }
}

function selectFavoriteLocation(location) {
    if (window.app) {
        window.app.selectFavoriteLocation(location);
    }
}

function refreshWeatherData() {
    if (window.app) {
        window.app.refreshWeatherData();
    }
}

function clearAllLocations() {
    if (window.app) {
        window.app.clearAllLocations();
    }
}

function saveLocationPreset() {
    if (window.app) {
        window.app.saveLocationPreset();
    }
}

function exportLocationData() {
    if (window.app) {
        window.app.exportLocationData();
    }
}

function importLocationData() {
    if (window.app) {
        window.app.importLocationData();
    }
}

function handleFileImport(event) {
    if (window.app) {
        window.app.handleFileImport(event);
    }
}

function toggleFavorite(location) {
    if (window.app) {
        window.app.toggleFavorite(location);
    }
}

function pinToTop(location) {
    if (window.app) {
        window.app.pinToTop(location);
    }
}

function removeLocation(location) {
    if (window.app) {
        window.app.removeLocation(location);
    }
}

function setAsHome(location) {
    if (window.app) {
        localStorage.setItem('homeLocation', location);
        window.app.showMessage(`Set ${location} as home location`, 'success');
    }
}

function createAlert(location) {
    if (window.app) {
        // Placeholder for weather alert functionality
        window.app.showMessage(`Weather alerts for ${location} (feature coming soon)`, 'info');
    }
}

function shareWeatherInfo(location) {
    if (navigator.share) {
        // Use native sharing if available
        navigator.share({
            title: `Weather in ${location}`,
            text: `Check out the current weather in ${location}`,
            url: window.location.href
        }).catch(console.error);
    } else {
        // Fallback to clipboard
        const url = `${window.location.origin}/forecast?zip=${encodeURIComponent(location)}`;
        navigator.clipboard.writeText(url).then(() => {
            if (window.app) {
                window.app.showMessage('Weather link copied to clipboard', 'success');
            }
        }).catch(() => {
            if (window.app) {
                window.app.showMessage('Unable to copy link', 'error');
            }
        });
    }
}

function showHourlyForecast(location, date) {
    if (window.app) {
        // Placeholder for hourly forecast modal
        window.app.showMessage(`Hourly forecast for ${location} on ${date} (feature coming soon)`, 'info');
    }
}

function focusLocationInput() {
    const input = document.getElementById('zipcodeInput');
    if (input) {
        input.focus();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WeatherApp();
    
    // Initialize favorites display
    setTimeout(() => {
        document.querySelectorAll('[data-location]').forEach(card => {
            const location = card.getAttribute('data-location');
            const starIcon = card.querySelector(`#star-${location.replace(' ', '-')}`);
            if (starIcon && window.app.favoriteLocations.some(fav => fav.location === location)) {
                starIcon.setAttribute('name', 'StarFill24Regular');
                starIcon.parentElement.classList.add('active');
            }
        });
    }, 100);
});;
