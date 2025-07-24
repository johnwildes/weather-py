// Enhanced State Management - Phase 4 Implementation
// Manages application state with local storage persistence and real-time updates

class StateManager {
    constructor() {
        this.state = {
            selectedLocations: new Set(),
            recentLocations: [],
            favoriteLocations: new Set(),
            pinnedLocations: new Set(),
            weatherData: new Map(),
            userPreferences: {
                tempUnit: 'celsius',
                theme: 'auto',
                autoRefresh: true,
                refreshInterval: 300000, // 5 minutes
                maxLocations: 10,
                defaultView: 'grid'
            },
            ui: {
                isLoading: false,
                activeView: 'grid',
                selectedLocation: null,
                sortBy: 'name',
                sortOrder: 'asc'
            }
        };

        this.listeners = new Map();
        this.autoRefreshTimer = null;
        this.storageKeys = {
            selectedLocations: 'weather_selected_locations',
            recentLocations: 'weather_recent_locations',
            favoriteLocations: 'weather_favorite_locations',
            pinnedLocations: 'weather_pinned_locations',
            userPreferences: 'weather_user_preferences'
        };

        this.init();
    }

    init() {
        this.loadFromStorage();
        this.setupAutoRefresh();
        this.setupStorageListener();
    }

    // Event System for State Changes
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);

        // Return unsubscribe function
        return () => {
            const listeners = this.listeners.get(event);
            if (listeners) {
                listeners.delete(callback);
            }
        };
    }

    emit(event, data) {
        const listeners = this.listeners.get(event);
        if (listeners) {
            listeners.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    // State Getters
    getSelectedLocations() {
        return Array.from(this.state.selectedLocations);
    }

    getRecentLocations() {
        return [...this.state.recentLocations];
    }

    getFavoriteLocations() {
        return Array.from(this.state.favoriteLocations);
    }

    getPinnedLocations() {
        return Array.from(this.state.pinnedLocations);
    }

    getWeatherData(location) {
        return this.state.weatherData.get(location);
    }

    getAllWeatherData() {
        return Object.fromEntries(this.state.weatherData);
    }

    getUserPreferences() {
        return { ...this.state.userPreferences };
    }

    getUIState() {
        return { ...this.state.ui };
    }

    // Location Management
    addLocation(location, displayName) {
        if (this.state.selectedLocations.size >= this.state.userPreferences.maxLocations) {
            throw new Error(`Maximum ${this.state.userPreferences.maxLocations} locations allowed`);
        }

        if (this.state.selectedLocations.has(location)) {
            return false; // Already exists
        }

        this.state.selectedLocations.add(location);
        this.addToRecentLocations(location, displayName);
        this.saveToStorage('selectedLocations');
        
        this.emit('locationAdded', { location, displayName });
        this.emit('selectedLocationsChanged', this.getSelectedLocations());
        
        return true;
    }

    removeLocation(location) {
        if (this.state.selectedLocations.delete(location)) {
            this.state.weatherData.delete(location);
            this.saveToStorage('selectedLocations');
            
            this.emit('locationRemoved', { location });
            this.emit('selectedLocationsChanged', this.getSelectedLocations());
            
            return true;
        }
        return false;
    }

    clearAllLocations() {
        const removed = Array.from(this.state.selectedLocations);
        this.state.selectedLocations.clear();
        this.state.weatherData.clear();
        this.saveToStorage('selectedLocations');
        
        this.emit('allLocationsCleared', { removed });
        this.emit('selectedLocationsChanged', []);
    }

    // Recent Locations Management
    addToRecentLocations(location, displayName) {
        const recentItem = {
            location,
            displayName: displayName || location,
            timestamp: Date.now()
        };

        // Remove if already exists
        this.state.recentLocations = this.state.recentLocations.filter(
            item => item.location !== location
        );

        // Add to front
        this.state.recentLocations.unshift(recentItem);

        // Keep only last 20 items
        this.state.recentLocations = this.state.recentLocations.slice(0, 20);
        
        this.saveToStorage('recentLocations');
        this.emit('recentLocationsChanged', this.getRecentLocations());
    }

    // Favorites Management
    addToFavorites(location, displayName) {
        if (this.state.favoriteLocations.has(location)) {
            return false;
        }

        this.state.favoriteLocations.add(location);
        this.addToRecentLocations(location, displayName);
        this.saveToStorage('favoriteLocations');
        
        this.emit('locationFavorited', { location, displayName });
        this.emit('favoriteLocationsChanged', this.getFavoriteLocations());
        
        return true;
    }

    removeFromFavorites(location) {
        if (this.state.favoriteLocations.delete(location)) {
            this.saveToStorage('favoriteLocations');
            
            this.emit('locationUnfavorited', { location });
            this.emit('favoriteLocationsChanged', this.getFavoriteLocations());
            
            return true;
        }
        return false;
    }

    isFavorite(location) {
        return this.state.favoriteLocations.has(location);
    }

    // Pinned Locations Management
    togglePin(location) {
        if (this.state.pinnedLocations.has(location)) {
            this.state.pinnedLocations.delete(location);
            this.emit('locationUnpinned', { location });
        } else {
            this.state.pinnedLocations.add(location);
            this.emit('locationPinned', { location });
        }
        
        this.saveToStorage('pinnedLocations');
        this.emit('pinnedLocationsChanged', this.getPinnedLocations());
    }

    isPinned(location) {
        return this.state.pinnedLocations.has(location);
    }

    // Weather Data Management
    setWeatherData(location, data) {
        this.state.weatherData.set(location, {
            ...data,
            lastUpdated: Date.now()
        });
        
        this.emit('weatherDataUpdated', { location, data });
    }

    setBulkWeatherData(weatherDataMap) {
        for (const [location, data] of Object.entries(weatherDataMap)) {
            this.setWeatherData(location, data);
        }
        
        this.emit('bulkWeatherDataUpdated', weatherDataMap);
    }

    isWeatherDataStale(location, maxAge = 300000) { // 5 minutes default
        const data = this.state.weatherData.get(location);
        if (!data || !data.lastUpdated) {
            return true;
        }
        
        return Date.now() - data.lastUpdated > maxAge;
    }

    getStaleLocations(maxAge = 300000) {
        return this.getSelectedLocations().filter(location => 
            this.isWeatherDataStale(location, maxAge)
        );
    }

    // User Preferences Management
    updatePreference(key, value) {
        if (key in this.state.userPreferences) {
            this.state.userPreferences[key] = value;
            this.saveToStorage('userPreferences');
            
            this.emit('preferenceChanged', { key, value });
            
            // Handle special preference changes
            if (key === 'autoRefresh' || key === 'refreshInterval') {
                this.setupAutoRefresh();
            }
        }
    }

    updatePreferences(preferences) {
        Object.assign(this.state.userPreferences, preferences);
        this.saveToStorage('userPreferences');
        
        this.emit('preferencesChanged', preferences);
        this.setupAutoRefresh();
    }

    // UI State Management
    setLoading(isLoading, message = '') {
        this.state.ui.isLoading = isLoading;
        this.emit('loadingStateChanged', { isLoading, message });
    }

    setActiveView(view) {
        this.state.ui.activeView = view;
        this.emit('activeViewChanged', view);
    }

    setSelectedLocation(location) {
        this.state.ui.selectedLocation = location;
        this.emit('selectedLocationChanged', location);
    }

    setSorting(sortBy, sortOrder = 'asc') {
        this.state.ui.sortBy = sortBy;
        this.state.ui.sortOrder = sortOrder;
        this.emit('sortingChanged', { sortBy, sortOrder });
    }

    // Auto-refresh Management
    setupAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
        }

        if (this.state.userPreferences.autoRefresh && this.state.userPreferences.refreshInterval > 0) {
            this.autoRefreshTimer = setInterval(() => {
                this.emit('autoRefreshTriggered');
            }, this.state.userPreferences.refreshInterval);
        }
    }

    // Storage Management
    loadFromStorage() {
        try {
            // Load selected locations
            const savedSelected = localStorage.getItem(this.storageKeys.selectedLocations);
            if (savedSelected) {
                this.state.selectedLocations = new Set(JSON.parse(savedSelected));
            }

            // Load recent locations
            const savedRecent = localStorage.getItem(this.storageKeys.recentLocations);
            if (savedRecent) {
                this.state.recentLocations = JSON.parse(savedRecent);
            }

            // Load favorite locations
            const savedFavorites = localStorage.getItem(this.storageKeys.favoriteLocations);
            if (savedFavorites) {
                this.state.favoriteLocations = new Set(JSON.parse(savedFavorites));
            }

            // Load pinned locations
            const savedPinned = localStorage.getItem(this.storageKeys.pinnedLocations);
            if (savedPinned) {
                this.state.pinnedLocations = new Set(JSON.parse(savedPinned));
            }

            // Load user preferences
            const savedPrefs = localStorage.getItem(this.storageKeys.userPreferences);
            if (savedPrefs) {
                Object.assign(this.state.userPreferences, JSON.parse(savedPrefs));
            }
        } catch (error) {
            console.error('Error loading from storage:', error);
        }
    }

    saveToStorage(key) {
        try {
            switch (key) {
                case 'selectedLocations':
                    localStorage.setItem(
                        this.storageKeys.selectedLocations,
                        JSON.stringify(Array.from(this.state.selectedLocations))
                    );
                    break;
                case 'recentLocations':
                    localStorage.setItem(
                        this.storageKeys.recentLocations,
                        JSON.stringify(this.state.recentLocations)
                    );
                    break;
                case 'favoriteLocations':
                    localStorage.setItem(
                        this.storageKeys.favoriteLocations,
                        JSON.stringify(Array.from(this.state.favoriteLocations))
                    );
                    break;
                case 'pinnedLocations':
                    localStorage.setItem(
                        this.storageKeys.pinnedLocations,
                        JSON.stringify(Array.from(this.state.pinnedLocations))
                    );
                    break;
                case 'userPreferences':
                    localStorage.setItem(
                        this.storageKeys.userPreferences,
                        JSON.stringify(this.state.userPreferences)
                    );
                    break;
            }
        } catch (error) {
            console.error(`Error saving ${key} to storage:`, error);
        }
    }

    setupStorageListener() {
        window.addEventListener('storage', (e) => {
            if (Object.values(this.storageKeys).includes(e.key)) {
                this.loadFromStorage();
                this.emit('storageChanged', { key: e.key, newValue: e.newValue });
            }
        });
    }

    // Import/Export functionality
    exportData() {
        return {
            selectedLocations: Array.from(this.state.selectedLocations),
            recentLocations: this.state.recentLocations,
            favoriteLocations: Array.from(this.state.favoriteLocations),
            pinnedLocations: Array.from(this.state.pinnedLocations),
            userPreferences: this.state.userPreferences,
            exportedAt: new Date().toISOString()
        };
    }

    importData(data) {
        try {
            if (data.selectedLocations) {
                this.state.selectedLocations = new Set(data.selectedLocations);
                this.saveToStorage('selectedLocations');
            }
            
            if (data.recentLocations) {
                this.state.recentLocations = data.recentLocations;
                this.saveToStorage('recentLocations');
            }
            
            if (data.favoriteLocations) {
                this.state.favoriteLocations = new Set(data.favoriteLocations);
                this.saveToStorage('favoriteLocations');
            }
            
            if (data.pinnedLocations) {
                this.state.pinnedLocations = new Set(data.pinnedLocations);
                this.saveToStorage('pinnedLocations');
            }
            
            if (data.userPreferences) {
                Object.assign(this.state.userPreferences, data.userPreferences);
                this.saveToStorage('userPreferences');
            }

            this.emit('dataImported', data);
            return true;
        } catch (error) {
            console.error('Error importing data:', error);
            return false;
        }
    }

    // Cleanup
    destroy() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
        }
        this.listeners.clear();
    }
}

// Export for global use
window.StateManager = StateManager;
