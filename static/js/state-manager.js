/**
 * State Manager - COMPLETELY REWRITTEN FROM SCRATCH
 * NO AUTO-LOADING - MANUAL LOADING ONLY
 */

class StateManager {
    constructor() {
        this.settings = {
            autoRefresh: false, // COMPLETELY DISABLED
            refreshInterval: 30000,
            theme: 'light',
            language: 'en'
        };
        this.isInitialized = false;
        this.logger = window.frontendLogger || console;
        
        // Initialize only when explicitly called
        this.logger.log('INFO', 'StateManager created - NO AUTO-INITIALIZATION');
    }
    
    // Manual initialization only
    init() {
        if (this.isInitialized) {
            this.logger.log('INFO', 'StateManager already initialized, skipping');
            return;
        }
        
        this.logger.log('INFO', 'StateManager manually initialized');
        this.loadSettings();
        this.setupEventListeners();
        this.isInitialized = true;
    }
    
    loadSettings() {
        // Load settings from localStorage - NO AUTO-LOADING
        try {
            const savedSettings = localStorage.getItem('dashboardSettings');
            if (savedSettings) {
                this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
            }
        } catch (error) {
            this.logger.log('ERROR', 'Failed to load settings:', error);
        }
        
        this.logger.log('INFO', 'Settings loaded - NO AUTO-LOADING');
    }
    
    setupEventListeners() {
        // Only setup basic event listeners - NO AUTO-LOADING
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.logger.log('INFO', 'Page became visible - NO AUTO-REFRESH');
                // NO AUTO-REFRESH - Manual loading only
            }
        });
        
        this.logger.log('INFO', 'Event listeners setup - NO AUTO-LOADING');
    }
    
    // Manual refresh function
    refreshData() {
        this.logger.log('INFO', 'Manual data refresh triggered');
        // This will be implemented when needed
    }
    
    // Save settings
    saveSettings() {
        try {
            localStorage.setItem('dashboardSettings', JSON.stringify(this.settings));
            this.logger.log('INFO', 'Settings saved');
        } catch (error) {
            this.logger.log('ERROR', 'Failed to save settings:', error);
        }
    }
}

// Create global instance - NO AUTO-INITIALIZATION
window.stateManager = new StateManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StateManager;
}
