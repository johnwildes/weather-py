// Forecast Page Specific JavaScript
let currentViewMode = 'grid';
let currentTempUnit = 'celsius';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize forecast page
    initializeForecastPage();
    
    // Load saved preferences
    loadUserPreferences();
    
    // Set up event listeners
    setupForecastListeners();
});

function initializeForecastPage() {
    // Auto-refresh weather data if locations are selected but no data is shown
    const weatherGrid = document.getElementById('weatherGrid');
    const hasWeatherCards = weatherGrid && weatherGrid.querySelector('.weather-card');
    
    if (window.app && window.app.selectedLocations.length > 0 && !hasWeatherCards) {
        // Auto-load weather data for selected locations
        setTimeout(() => {
            window.app.refreshWeatherData();
        }, 1000);
    }
}

function setupForecastListeners() {
    // Temperature unit change listener
    const tempUnitRadio = document.getElementById('tempUnit');
    if (tempUnitRadio) {
        tempUnitRadio.addEventListener('change', (e) => {
            changeTempUnit(e.target.value);
        });
    }
    
    // View mode change listener
    const viewModeRadio = document.getElementById('viewMode');
    if (viewModeRadio) {
        viewModeRadio.addEventListener('change', (e) => {
            changeViewMode(e.target.value);
        });
    }
}

function changeViewMode(mode) {
    currentViewMode = mode;
    localStorage.setItem('viewMode', mode);
    
    const weatherGrid = document.getElementById('weatherGrid');
    if (!weatherGrid) return;
    
    weatherGrid.classList.remove('grid-view', 'comparison-view');
    weatherGrid.classList.add(`${mode}-view`);
    
    if (mode === 'comparison') {
        showComparisonView();
    } else {
        showGridView();
    }
}

function changeTempUnit(unit) {
    currentTempUnit = unit;
    localStorage.setItem('tempUnit', unit);
    
    // Update all temperature displays
    updateTemperatureDisplays(unit);
    
    // Refresh data if we have locations selected
    if (window.app && window.app.selectedLocations.length > 0) {
        window.app.refreshWeatherData();
    }
}

function showGridView() {
    const weatherGrid = document.getElementById('weatherGrid');
    if (!weatherGrid) return;
    
    // Reset grid layout
    weatherGrid.style.display = 'grid';
    weatherGrid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(350px, 1fr))';
}

function showComparisonView() {
    const weatherGrid = document.getElementById('weatherGrid');
    if (!weatherGrid) return;
    
    // Create comparison table layout
    const weatherCards = weatherGrid.querySelectorAll('.weather-card');
    if (weatherCards.length < 2) {
        showMessage('Need at least 2 locations for comparison view', 'warning');
        // Reset to grid view
        document.querySelector('#viewMode input[value="grid"]').checked = true;
        changeViewMode('grid');
        return;
    }
    
    // Convert to comparison table format
    weatherGrid.style.display = 'block';
    createComparisonTable(weatherCards);
}

function createComparisonTable(weatherCards) {
    const weatherGrid = document.getElementById('weatherGrid');
    
    // Extract data from weather cards
    const locationData = Array.from(weatherCards).map(card => {
        const locationName = card.querySelector('.location-name')?.textContent || 'Unknown';
        const temp = card.querySelector('.temp-value')?.textContent || '0';
        const condition = card.querySelector('.condition-text')?.textContent || 'Unknown';
        const icon = card.querySelector('.weather-icon img')?.src || '';
        
        return { locationName, temp, condition, icon };
    });
    
    // Create comparison table
    const tableHTML = `
        <fluent-card class="comparison-table-card">
            <h3>Weather Comparison</h3>
            <div class="table-responsive">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Location</th>
                            <th>Current Weather</th>
                            <th>Temperature</th>
                            <th>Condition</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${locationData.map(data => `
                            <tr>
                                <td class="location-cell">
                                    <strong>${data.locationName}</strong>
                                </td>
                                <td class="weather-icon-cell">
                                    <img src="${data.icon}" alt="${data.condition}" width="48" height="48" />
                                </td>
                                <td class="temperature-cell">
                                    <span class="temp-large">${data.temp}°</span>
                                </td>
                                <td class="condition-cell">
                                    ${data.condition}
                                </td>
                                <td class="actions-cell">
                                    <fluent-button 
                                        appearance="outline" 
                                        size="small"
                                        onclick="showDetailedForecast('${data.locationName}')">
                                        Details
                                    </fluent-button>
                                    <fluent-button 
                                        appearance="stealth" 
                                        size="small"
                                        onclick="removeLocation('${data.locationName}')">
                                        <fluent-icon name="Delete16Regular"></fluent-icon>
                                    </fluent-button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </fluent-card>
    `;
    
    weatherGrid.innerHTML = tableHTML;
}

function updateTemperatureDisplays(unit) {
    const tempElements = document.querySelectorAll('.temp-value, .high-temp, .low-temp, .feels-like');
    
    tempElements.forEach(element => {
        const currentText = element.textContent;
        const tempMatch = currentText.match(/(-?\d+(?:\.\d+)?)/);
        
        if (tempMatch) {
            const tempValue = parseFloat(tempMatch[1]);
            let convertedTemp;
            
            if (unit === 'fahrenheit' && currentText.includes('°C')) {
                convertedTemp = Math.round((tempValue * 9/5) + 32);
                element.textContent = currentText.replace(/(-?\d+(?:\.\d+)?)°C/, `${convertedTemp}°F`);
            } else if (unit === 'celsius' && currentText.includes('°F')) {
                convertedTemp = Math.round((tempValue - 32) * 5/9);
                element.textContent = currentText.replace(/(-?\d+(?:\.\d+)?)°F/, `${convertedTemp}°C`);
            }
        }
    });
}

function showDetailedForecast(locationName) {
    const dialog = document.getElementById('detailDialog');
    const dialogTitle = document.getElementById('dialogTitle');
    const dialogBody = document.getElementById('dialogBody');
    
    if (!dialog || !dialogTitle || !dialogBody) return;
    
    dialogTitle.textContent = `Detailed Forecast - ${locationName}`;
    dialogBody.innerHTML = '<fluent-progress-ring></fluent-progress-ring>';
    dialog.hidden = false;
    
    // Fetch detailed forecast data
    fetchDetailedForecast(locationName)
        .then(data => {
            displayDetailedForecast(data, dialogBody);
        })
        .catch(error => {
            console.error('Error fetching detailed forecast:', error);
            dialogBody.innerHTML = `
                <div class="error-message">
                    <fluent-icon name="ErrorCircle24Regular"></fluent-icon>
                    <p>Error loading detailed forecast</p>
                </div>
            `;
        });
}

async function fetchDetailedForecast(locationName) {
    const response = await fetch(`/api/detailed-forecast?location=${encodeURIComponent(locationName)}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

function displayDetailedForecast(data, container) {
    // Create detailed forecast display
    const detailHTML = `
        <div class="detailed-forecast">
            <div class="current-details">
                <h4>Current Conditions</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="label">Temperature:</span>
                        <span class="value">${data.current.temp_c}°C / ${data.current.temp_f}°F</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Feels Like:</span>
                        <span class="value">${data.current.feelslike_c}°C / ${data.current.feelslike_f}°F</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Humidity:</span>
                        <span class="value">${data.current.humidity}%</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Wind:</span>
                        <span class="value">${data.current.wind_kph} km/h ${data.current.wind_dir}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Pressure:</span>
                        <span class="value">${data.current.pressure_mb} mb</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Visibility:</span>
                        <span class="value">${data.current.vis_km} km</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">UV Index:</span>
                        <span class="value">${data.current.uv}</span>
                    </div>
                </div>
            </div>
            
            <div class="extended-forecast">
                <h4>Extended Forecast</h4>
                <div class="forecast-timeline">
                    ${data.forecast.forecastday.map(day => `
                        <div class="forecast-day-detail">
                            <div class="day-header">
                                <strong>${formatDate(day.date)}</strong>
                                <img src="${day.day.condition.icon}" alt="${day.day.condition.text}" />
                            </div>
                            <div class="day-summary">
                                <p>${day.day.condition.text}</p>
                                <p>High: ${day.day.maxtemp_c}°C | Low: ${day.day.mintemp_c}°C</p>
                                <p>Rain: ${day.day.daily_chance_of_rain}% | Wind: ${day.day.maxwind_kph} km/h</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = detailHTML;
}

function closeDetailDialog() {
    const dialog = document.getElementById('detailDialog');
    if (dialog) {
        dialog.hidden = true;
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow';
    } else {
        return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
    }
}

function loadUserPreferences() {
    // Load view mode preference
    const savedViewMode = localStorage.getItem('viewMode') || 'grid';
    const viewModeRadio = document.querySelector(`#viewMode input[value="${savedViewMode}"]`);
    if (viewModeRadio) {
        viewModeRadio.checked = true;
        currentViewMode = savedViewMode;
    }
    
    // Load temperature unit preference
    const savedTempUnit = localStorage.getItem('tempUnit') || 'celsius';
    const tempUnitRadio = document.querySelector(`#tempUnit input[value="${savedTempUnit}"]`);
    if (tempUnitRadio) {
        tempUnitRadio.checked = true;
        currentTempUnit = savedTempUnit;
    }
}

function removeLocation(locationName) {
    if (window.app) {
        window.app.removeLocation(locationName);
        
        // If we're in comparison view and now have less than 2 locations, switch to grid view
        if (currentViewMode === 'comparison' && window.app.selectedLocations.length < 2) {
            document.querySelector('#viewMode input[value="grid"]').checked = true;
            changeViewMode('grid');
        }
    }
}

// Global function for template onclick handlers
function focusLocationInput() {
    const input = document.getElementById('zipcodeInput');
    if (input) {
        input.focus();
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Utility function to show messages (if not available from main app)
function showMessage(message, type = 'info') {
    if (window.app && window.app.showMessage) {
        window.app.showMessage(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}
