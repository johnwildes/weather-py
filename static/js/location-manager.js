// Location Manager - Handles location-specific functionality
class LocationManager {
    constructor() {
        this.favorites = this.loadFavorites();
    }

    // Favorite Locations Management
    addToFavorites(location, displayName) {
        const favorite = {
            location: location,
            displayName: displayName || location,
            addedAt: new Date().toISOString()
        };

        if (!this.favorites.find(fav => fav.location === location)) {
            this.favorites.push(favorite);
            this.saveFavorites();
            return true;
        }
        return false;
    }

    removeFromFavorites(location) {
        const index = this.favorites.findIndex(fav => fav.location === location);
        if (index > -1) {
            this.favorites.splice(index, 1);
            this.saveFavorites();
            return true;
        }
        return false;
    }

    isFavorite(location) {
        return this.favorites.some(fav => fav.location === location);
    }

    getFavorites() {
        return [...this.favorites];
    }

    // Location Search and Autocomplete
    async searchLocations(query) {
        if (!query || query.length < 2) {
            return [];
        }

        try {
            const response = await fetch(`/api/search-locations?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const results = await response.json();
                return results.slice(0, 10); // Limit to 10 suggestions
            }
        } catch (error) {
            console.error('Location search error:', error);
        }
        return [];
    }

    // Location Formatting and Display
    formatLocationName(locationData) {
        if (!locationData) return 'Unknown Location';
        
        const { name, region, country } = locationData;
        let formatted = name || 'Unknown';
        
        if (region && region !== name) {
            formatted += `, ${region}`;
        }
        
        if (country) {
            formatted += `, ${country}`;
        }
        
        return formatted;
    }

    getLocationShortName(locationData) {
        if (!locationData) return 'Unknown';
        return locationData.name || 'Unknown';
    }

    // Geolocation Utilities
    async getCurrentPosition(options = {}) {
        const defaultOptions = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5 minutes
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                (error) => {
                    let message = 'Unknown geolocation error';
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            message = 'Location access denied by user';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            message = 'Location information unavailable';
                            break;
                        case error.TIMEOUT:
                            message = 'Location request timed out';
                            break;
                    }
                    reject(new Error(message));
                },
                finalOptions
            );
        });
    }

    formatCoordinates(lat, lon) {
        return `${lat.toFixed(4)},${lon.toFixed(4)}`;
    }

    // Location History and Analytics
    trackLocationUsage(location) {
        const usage = this.loadLocationUsage();
        const key = location.toLowerCase();
        
        if (usage[key]) {
            usage[key].count++;
            usage[key].lastUsed = new Date().toISOString();
        } else {
            usage[key] = {
                location: location,
                count: 1,
                firstUsed: new Date().toISOString(),
                lastUsed: new Date().toISOString()
            };
        }
        
        this.saveLocationUsage(usage);
    }

    getPopularLocations(limit = 5) {
        const usage = this.loadLocationUsage();
        return Object.values(usage)
            .sort((a, b) => b.count - a.count)
            .slice(0, limit)
            .map(item => item.location);
    }

    getRecentlyUsedLocations(limit = 5) {
        const usage = this.loadLocationUsage();
        return Object.values(usage)
            .sort((a, b) => new Date(b.lastUsed) - new Date(a.lastUsed))
            .slice(0, limit)
            .map(item => item.location);
    }

    // Location Validation
    validateZipCode(zipCode) {
        // US ZIP code patterns
        const usZipPattern = /^\d{5}(-\d{4})?$/;
        // Canadian postal code pattern
        const caPostalPattern = /^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$/;
        // UK postcode pattern (simplified)
        const ukPostcodePattern = /^[A-Za-z]{1,2}\d{1,2}[A-Za-z]? ?\d[A-Za-z]{2}$/;
        
        return usZipPattern.test(zipCode) || 
               caPostalPattern.test(zipCode) || 
               ukPostcodePattern.test(zipCode);
    }

    validateCoordinates(lat, lon) {
        const latitude = parseFloat(lat);
        const longitude = parseFloat(lon);
        
        return !isNaN(latitude) && 
               !isNaN(longitude) && 
               latitude >= -90 && 
               latitude <= 90 && 
               longitude >= -180 && 
               longitude <= 180;
    }

    parseLocationInput(input) {
        if (!input) return null;
        
        const trimmed = input.trim();
        
        // Check if it's coordinates (lat,lon)
        const coordMatch = trimmed.match(/^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$/);
        if (coordMatch) {
            const lat = parseFloat(coordMatch[1]);
            const lon = parseFloat(coordMatch[2]);
            if (this.validateCoordinates(lat, lon)) {
                return {
                    type: 'coordinates',
                    value: `${lat},${lon}`,
                    latitude: lat,
                    longitude: lon
                };
            }
        }
        
        // Check if it's a ZIP code
        if (this.validateZipCode(trimmed)) {
            return {
                type: 'zipcode',
                value: trimmed
            };
        }
        
        // Otherwise treat as city name
        return {
            type: 'city',
            value: trimmed
        };
    }

    // Storage Management
    saveFavorites() {
        try {
            localStorage.setItem('favoriteLocations', JSON.stringify(this.favorites));
        } catch (error) {
            console.error('Error saving favorites:', error);
        }
    }

    loadFavorites() {
        try {
            const saved = localStorage.getItem('favoriteLocations');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading favorites:', error);
            return [];
        }
    }

    saveLocationUsage(usage) {
        try {
            localStorage.setItem('locationUsage', JSON.stringify(usage));
        } catch (error) {
            console.error('Error saving location usage:', error);
        }
    }

    loadLocationUsage() {
        try {
            const saved = localStorage.getItem('locationUsage');
            return saved ? JSON.parse(saved) : {};
        } catch (error) {
            console.error('Error loading location usage:', error);
            return {};
        }
    }

    // Import/Export Functions
    exportLocationData() {
        const data = {
            favorites: this.favorites,
            usage: this.loadLocationUsage(),
            recent: JSON.parse(localStorage.getItem('recentLocations') || '[]'),
            selected: JSON.parse(localStorage.getItem('selectedLocations') || '[]'),
            exportDate: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `weather-app-locations-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }

    async importLocationData(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    if (data.favorites) {
                        this.favorites = data.favorites;
                        this.saveFavorites();
                    }
                    
                    if (data.usage) {
                        this.saveLocationUsage(data.usage);
                    }
                    
                    if (data.recent) {
                        localStorage.setItem('recentLocations', JSON.stringify(data.recent));
                    }
                    
                    if (data.selected) {
                        localStorage.setItem('selectedLocations', JSON.stringify(data.selected));
                    }
                    
                    resolve(data);
                } catch (error) {
                    reject(new Error('Invalid file format'));
                }
            };
            reader.onerror = () => reject(new Error('Error reading file'));
            reader.readAsText(file);
        });
    }
}

// Export for use in other modules
window.LocationManager = LocationManager;
