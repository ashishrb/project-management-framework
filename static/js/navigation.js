/**
 * Navigation Manager - COMPLETELY REWRITTEN FROM SCRATCH
 * NO AUTO-LOADING - MANUAL LOADING ONLY
 */

class NavigationManager {
    constructor() {
        this.currentView = null;
        this.isInitialized = false;
        this.logger = window.frontendLogger || console;
        
        // Initialize only when explicitly called
        this.logger.log('INFO', 'NavigationManager created - NO AUTO-INITIALIZATION');
    }
    
    // Manual initialization only
    init() {
        if (this.isInitialized) {
            this.logger.log('INFO', 'NavigationManager already initialized, skipping');
            return;
        }
        
        this.logger.log('INFO', 'NavigationManager manually initialized');
        this.setupEventListeners();
        this.isInitialized = true;
    }
    
    setupEventListeners() {
        // Only setup basic navigation links - NO AUTO-LOADING
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                if (href && href !== '#') {
                    this.navigateToRoute(href);
                }
            });
        });
        
        this.logger.log('INFO', 'Navigation event listeners setup - NO AUTO-LOADING');
    }
    
    navigateToRoute(route) {
        this.logger.log('INFO', `Manual navigation to: ${route}`);
        
        // Simple route handling - NO AUTO-LOADING
        if (route === '/dashboard') {
            this.loadDashboardView();
        } else if (route === '/projects') {
            this.loadProjectsView();
        } else if (route === '/resources') {
            this.loadResourcesView();
        } else if (route === '/risks') {
            this.loadRisksView();
        } else {
            this.loadHomeView();
        }
    }
    
    loadHomeView() {
        this.logger.log('INFO', 'Loading home view - NO AUTO-LOADING');
        this.currentView = 'home';
        
        // Navigate to home page
        window.location.href = '/';
    }
    
    loadDashboardView() {
        this.logger.log('INFO', 'Loading dashboard view - NO AUTO-LOADING');
        this.currentView = 'dashboard';
        
        // Navigate to dashboard page
        window.location.href = '/dashboard';
    }
    
    loadProjectsView() {
        this.logger.log('INFO', 'Loading projects view - NO AUTO-LOADING');
        this.currentView = 'projects';
        
        // Navigate to projects page
        window.location.href = '/projects';
    }
    
    loadResourcesView() {
        this.logger.log('INFO', 'Loading resources view - NO AUTO-LOADING');
        this.currentView = 'resources';
        
        // Navigate to resources page
        window.location.href = '/resources';
    }
    
    loadRisksView() {
        this.logger.log('INFO', 'Loading risks view - NO AUTO-LOADING');
        this.currentView = 'risks';
        
        // Navigate to risks page
        window.location.href = '/risks';
    }
}

// Global function for manual dashboard data loading
function loadDashboardData() {
    console.log('Manual dashboard data loading triggered');
    // This will be implemented when needed
}

// Create global instance - NO AUTO-INITIALIZATION
window.navigationManager = new NavigationManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationManager;
}
