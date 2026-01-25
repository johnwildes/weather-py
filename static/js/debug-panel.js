// Debug Panel - Development debugging tools
// Only loaded when WEATHER_DEBUG_MODE=true

class DebugPanel {
    constructor() {
        this.isOpen = false;
        this.activeTab = 'weather';
        this.requestLog = [];
        this.eventLog = [];
        this.maxLogItems = 50;
        
        this.init();
    }

    init() {
        this.loadState();
        this.createPanel();
        this.setupEventInterceptors();
        this.setupKeyboardShortcut();
        this.fetchEnvironmentInfo();
        
        // Restore open state
        if (this.isOpen) {
            this.open();
        }
    }

    loadState() {
        try {
            const saved = localStorage.getItem('debug_panel_state');
            if (saved) {
                const state = JSON.parse(saved);
                this.isOpen = state.isOpen || false;
                this.activeTab = state.activeTab || 'weather';
            }
        } catch (e) {
            console.error('Error loading debug panel state:', e);
        }
    }

    saveState() {
        try {
            localStorage.setItem('debug_panel_state', JSON.stringify({
                isOpen: this.isOpen,
                activeTab: this.activeTab
            }));
        } catch (e) {
            console.error('Error saving debug panel state:', e);
        }
    }

    createPanel() {
        // Create wrapper for push effect
        const main = document.querySelector('.app-main');
        if (main && !main.parentElement.classList.contains('app-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'app-wrapper';
            main.parentNode.insertBefore(wrapper, main);
            wrapper.appendChild(main);
        }

        // Create toggle tab
        this.toggleTab = document.createElement('div');
        this.toggleTab.className = 'debug-toggle-tab';
        this.toggleTab.innerHTML = '🔧 DEBUG';
        this.toggleTab.addEventListener('click', () => this.toggle());
        document.body.appendChild(this.toggleTab);

        // Create panel
        this.panel = document.createElement('div');
        this.panel.className = 'debug-panel';
        this.panel.innerHTML = this.getPanelHTML();
        document.body.appendChild(this.panel);

        // Setup tab switching
        this.panel.querySelectorAll('.debug-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });

        // Setup close button
        this.panel.querySelector('.debug-close-btn').addEventListener('click', () => this.close());

        // Setup action buttons
        this.setupActionButtons();

        // Initial content render
        this.switchTab(this.activeTab);
    }

    getPanelHTML() {
        return `
            <div class="debug-panel-header">
                <h3>🔧 Debug Panel</h3>
                <button class="debug-close-btn">×</button>
            </div>
            <div class="debug-tabs">
                <button class="debug-tab" data-tab="weather">Weather</button>
                <button class="debug-tab" data-tab="cache">Cache</button>
                <button class="debug-tab" data-tab="state">State</button>
                <button class="debug-tab" data-tab="requests">Requests</button>
                <button class="debug-tab" data-tab="env">Environment</button>
            </div>
            <div class="debug-tab-content" data-content="weather">
                <div class="debug-content-scroll">
                    <div class="debug-json" id="debugWeatherJson"></div>
                </div>
                <div class="debug-actions">
                    <button class="debug-btn" id="debugCopyWeather">Copy JSON</button>
                    <button class="debug-btn" id="debugRefreshWeather">Refresh</button>
                </div>
            </div>
            <div class="debug-tab-content" data-content="cache">
                <div class="debug-content-scroll" id="debugCacheList"></div>
                <div class="debug-actions">
                    <button class="debug-btn primary" id="debugClearCache">Clear Cache</button>
                </div>
            </div>
            <div class="debug-tab-content" data-content="state">
                <div class="debug-content-scroll">
                    <div class="debug-state-tree" id="debugStateTree"></div>
                    <h4 style="margin-top: 16px; color: #fff;">Event Log</h4>
                    <div id="debugEventLog"></div>
                </div>
            </div>
            <div class="debug-tab-content" data-content="requests">
                <div class="debug-content-scroll" id="debugRequestLog"></div>
                <div class="debug-actions">
                    <button class="debug-btn" id="debugClearRequests">Clear Log</button>
                </div>
            </div>
            <div class="debug-tab-content" data-content="env">
                <div class="debug-content-scroll" id="debugEnvInfo"></div>
                <div class="debug-actions">
                    <button class="debug-btn" id="debugRefreshEnv">Refresh</button>
                </div>
            </div>
        `;
    }

    setupActionButtons() {
        // Weather tab
        this.panel.querySelector('#debugCopyWeather')?.addEventListener('click', () => {
            const json = window.currentWeatherData;
            navigator.clipboard.writeText(JSON.stringify(json, null, 2))
                .then(() => MessageBar?.success('JSON copied to clipboard'))
                .catch(() => MessageBar?.error('Failed to copy'));
        });

        this.panel.querySelector('#debugRefreshWeather')?.addEventListener('click', () => {
            this.renderWeatherTab();
        });

        // Cache tab
        this.panel.querySelector('#debugClearCache')?.addEventListener('click', () => {
            if (window.weatherAPI) {
                window.weatherAPI.clearCache();
                this.renderCacheTab();
                MessageBar?.success('Cache cleared');
            }
        });

        // Requests tab
        this.panel.querySelector('#debugClearRequests')?.addEventListener('click', () => {
            this.requestLog = [];
            this.renderRequestsTab();
        });

        // Environment tab
        this.panel.querySelector('#debugRefreshEnv')?.addEventListener('click', () => {
            this.fetchEnvironmentInfo();
        });
    }

    setupEventInterceptors() {
        // Intercept fetch for request logging
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();
            const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || 'unknown';
            const method = args[1]?.method || 'GET';
            
            try {
                const response = await originalFetch.apply(window, args);
                const duration = performance.now() - startTime;
                
                this.logRequest({
                    url,
                    method,
                    status: response.status,
                    duration,
                    success: response.ok,
                    timestamp: new Date()
                });
                
                return response;
            } catch (error) {
                const duration = performance.now() - startTime;
                this.logRequest({
                    url,
                    method,
                    status: 0,
                    duration,
                    success: false,
                    error: error.message,
                    timestamp: new Date()
                });
                throw error;
            }
        };

        // Subscribe to StateManager events
        if (window.stateManager) {
            const originalEmit = window.stateManager.emit.bind(window.stateManager);
            window.stateManager.emit = (event, data) => {
                this.logEvent(event, data);
                return originalEmit(event, data);
            };
        }
    }

    setupKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+D to toggle
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggle();
            }
        });
    }

    async fetchEnvironmentInfo() {
        try {
            const response = await fetch('/api/debug/info');
            if (response.ok) {
                this.envInfo = await response.json();
                this.renderEnvTab();
            }
        } catch (e) {
            console.error('Failed to fetch debug info:', e);
        }
    }

    logRequest(request) {
        this.requestLog.unshift(request);
        if (this.requestLog.length > this.maxLogItems) {
            this.requestLog.pop();
        }
        if (this.activeTab === 'requests') {
            this.renderRequestsTab();
        }
    }

    logEvent(event, data) {
        this.eventLog.unshift({
            event,
            data,
            timestamp: new Date()
        });
        if (this.eventLog.length > this.maxLogItems) {
            this.eventLog.pop();
        }
        if (this.activeTab === 'state') {
            this.renderStateTab();
        }
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.isOpen = true;
        this.panel.classList.add('open');
        this.toggleTab.classList.add('panel-open');
        document.querySelector('.app-wrapper')?.classList.add('debug-panel-open');
        this.saveState();
        this.refreshCurrentTab();
    }

    close() {
        this.isOpen = false;
        this.panel.classList.remove('open');
        this.toggleTab.classList.remove('panel-open');
        document.querySelector('.app-wrapper')?.classList.remove('debug-panel-open');
        this.saveState();
    }

    switchTab(tabName) {
        this.activeTab = tabName;
        
        // Update tab buttons
        this.panel.querySelectorAll('.debug-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // Update tab content
        this.panel.querySelectorAll('.debug-tab-content').forEach(content => {
            content.classList.toggle('active', content.dataset.content === tabName);
        });
        
        this.refreshCurrentTab();
        this.saveState();
    }

    refreshCurrentTab() {
        switch (this.activeTab) {
            case 'weather': this.renderWeatherTab(); break;
            case 'cache': this.renderCacheTab(); break;
            case 'state': this.renderStateTab(); break;
            case 'requests': this.renderRequestsTab(); break;
            case 'env': this.renderEnvTab(); break;
        }
    }

    renderWeatherTab() {
        const container = this.panel.querySelector('#debugWeatherJson');
        const data = window.currentWeatherData;
        
        if (data) {
            container.innerHTML = this.syntaxHighlight(JSON.stringify(data, null, 2));
        } else {
            container.innerHTML = '<div class="debug-empty">No weather data loaded</div>';
        }
    }

    renderCacheTab() {
        const container = this.panel.querySelector('#debugCacheList');
        const api = window.weatherAPI;
        
        if (!api || api.cache.size === 0) {
            container.innerHTML = '<div class="debug-empty">Cache is empty</div>';
            return;
        }

        let html = '';
        api.cache.forEach((value, key) => {
            const age = Date.now() - value.timestamp;
            const ttl = api.cacheExpiry - age;
            const ttlClass = ttl < 60000 ? (ttl < 0 ? 'expired' : 'expiring') : '';
            
            html += `
                <div class="debug-cache-item">
                    <div class="debug-cache-url">${this.escapeHtml(key)}</div>
                    <div class="debug-cache-meta">
                        <span>Cached: ${this.formatTime(new Date(value.timestamp))}</span>
                        <span class="debug-cache-ttl ${ttlClass}">
                            TTL: ${ttl > 0 ? Math.round(ttl / 1000) + 's' : 'expired'}
                        </span>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    renderStateTab() {
        const stateContainer = this.panel.querySelector('#debugStateTree');
        const eventContainer = this.panel.querySelector('#debugEventLog');
        
        if (window.stateManager) {
            const state = {
                selectedLocations: window.stateManager.getSelectedLocations(),
                recentLocations: window.stateManager.getRecentLocations(),
                favoriteLocations: window.stateManager.getFavoriteLocations(),
                preferences: window.stateManager.getUserPreferences(),
                ui: window.stateManager.getUIState()
            };
            stateContainer.innerHTML = this.syntaxHighlight(JSON.stringify(state, null, 2));
        } else {
            stateContainer.innerHTML = '<div class="debug-empty">StateManager not available</div>';
        }

        // Render event log
        if (this.eventLog.length === 0) {
            eventContainer.innerHTML = '<div class="debug-empty">No events logged</div>';
        } else {
            let html = '';
            this.eventLog.slice(0, 20).forEach(item => {
                html += `
                    <div class="debug-event-item">
                        <span class="debug-event-time">${this.formatTime(item.timestamp)}</span>
                        <span class="debug-event-name">${this.escapeHtml(item.event)}</span>
                    </div>
                `;
            });
            eventContainer.innerHTML = html;
        }
    }

    renderRequestsTab() {
        const container = this.panel.querySelector('#debugRequestLog');
        
        if (this.requestLog.length === 0) {
            container.innerHTML = '<div class="debug-empty">No requests logged</div>';
            return;
        }

        let html = '';
        this.requestLog.forEach(req => {
            const statusClass = req.success ? 'success' : 'error';
            html += `
                <div class="debug-request-item">
                    <div class="debug-request-header">
                        <span class="debug-request-method ${req.method}">${req.method}</span>
                        <span class="debug-request-status ${statusClass}">${req.status || 'ERR'}</span>
                    </div>
                    <div class="debug-request-url">${this.escapeHtml(req.url)}</div>
                    <div class="debug-request-timing">
                        ${this.formatTime(req.timestamp)} · ${Math.round(req.duration)}ms
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    renderEnvTab() {
        const container = this.panel.querySelector('#debugEnvInfo');
        
        if (!this.envInfo) {
            container.innerHTML = '<div class="debug-empty">Loading environment info...</div>';
            return;
        }

        let html = `
            <div class="debug-env-section">
                <h4>Environment Variables</h4>
                ${this.renderEnvItems(this.envInfo.environment)}
            </div>
            <div class="debug-env-section">
                <h4>Server Info</h4>
                ${this.renderEnvItems(this.envInfo.server)}
            </div>
            <div class="debug-env-section">
                <h4>Debug Info</h4>
                <div class="debug-env-item">
                    <span class="debug-env-key">fetched_at</span>
                    <span class="debug-env-value">${this.envInfo.timestamp}</span>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    renderEnvItems(obj) {
        return Object.entries(obj).map(([key, value]) => `
            <div class="debug-env-item">
                <span class="debug-env-key">${this.escapeHtml(key)}</span>
                <span class="debug-env-value">${this.escapeHtml(String(value))}</span>
            </div>
        `).join('');
    }

    syntaxHighlight(json) {
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', { 
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    }

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

// Initialize debug panel when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new DebugPanel());
} else {
    new DebugPanel();
}

// Export for global access
window.DebugPanel = DebugPanel;
