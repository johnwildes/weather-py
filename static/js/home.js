// Home Page Specific JavaScript
document.addEventListener('DOMContentLoaded', () => {
    const locationManager = new LocationManager();
    
    // Populate recent locations on home page
    populateRecentLocationsList();
    
    // Set up event listeners for home page specific elements
    setupHomePageListeners();
});

function populateRecentLocationsList() {
    const recentList = document.getElementById('recentLocationsList');
    if (!recentList) return;
    
    const locationManager = new LocationManager();
    const recentLocations = locationManager.getRecentlyUsedLocations(5);
    
    if (recentLocations.length === 0) {
        recentList.innerHTML = '<p class="no-recent">No recent locations</p>';
        return;
    }
    
    recentList.innerHTML = '';
    recentLocations.forEach(location => {
        const item = document.createElement('div');
        item.className = 'recent-item';
        item.innerHTML = `
            <div class="recent-location-info">
                <span class="location-name">${location}</span>
                <fluent-button 
                    appearance="subtle" 
                    size="small"
                    onclick="addLocationFromRecent('${location}')"
                    title="Add to selected locations">
                    <fluent-icon name="Add16Regular"></fluent-icon>
                </fluent-button>
            </div>
        `;
        recentList.appendChild(item);
    });
}

function addLocationFromRecent(location) {
    if (window.app) {
        window.app.addLocation(location);
        // Navigate to forecast page to show the result
        setTimeout(() => {
            window.location.href = '/forecast';
        }, 1000);
    }
}

function setupHomePageListeners() {
    // Add any home page specific event listeners here
    const quickForecastBtn = document.querySelector('[onclick*="forecast"]');
    if (quickForecastBtn) {
        quickForecastBtn.addEventListener('click', (e) => {
            // Add some visual feedback
            e.target.classList.add('loading');
        });
    }
}
