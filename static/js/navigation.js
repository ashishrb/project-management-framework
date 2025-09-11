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
        console.log('🔍 DEBUG: Setting up navigation event listeners...');
        
        // Find all navigation links
        const navLinks = document.querySelectorAll('.nav-link');
        console.log('🔍 DEBUG: Found', navLinks.length, 'navigation links');
        
        navLinks.forEach((link, index) => {
            const href = link.getAttribute('href');
            console.log(`🔍 DEBUG: Link ${index}: href="${href}", text="${link.textContent.trim()}"`);
            
            // Add click listener for debugging only - don't interfere with navigation
            link.addEventListener('click', (e) => {
                console.log('🔍 DEBUG: Navigation click detected!');
                console.log('🔍 DEBUG: Link href:', href);
                console.log('🔍 DEBUG: Link text:', link.textContent.trim());
                
                // Just log - don't prevent default or interfere
                this.logger.log('INFO', `Navigation clicked: ${href}`);
            });
        });
        
        console.log('🔍 DEBUG: Navigation event listeners setup complete - NO INTERFERENCE');
        this.logger.log('INFO', 'Navigation event listeners setup - NO INTERFERENCE MODE');
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
        } else if (route === '/backlog') {
            this.loadBacklogView();
        } else if (route === '/ai-copilot') {
            this.loadAICopilotView();
        } else if (route === '/features') {
            this.loadFeaturesView();
        } else if (route === '/gantt') {
            this.loadGanttView();
        } else if (route === '/reports') {
            this.loadReportsView();
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
    
    loadBacklogView() {
        this.logger.log('INFO', 'Loading backlog view - NO AUTO-LOADING');
        this.currentView = 'backlog';
        
        // Navigate to backlog page
        window.location.href = '/backlog';
    }
    
    loadAICopilotView() {
        this.logger.log('INFO', 'Loading AI Copilot view - NO AUTO-LOADING');
        this.currentView = 'ai-copilot';
        
        // Navigate to AI Copilot page
        window.location.href = '/ai-copilot';
    }
    
    loadFeaturesView() {
        this.logger.log('INFO', 'Loading features view - NO AUTO-LOADING');
        this.currentView = 'features';
        
        // Navigate to features page
        window.location.href = '/features';
    }
    
    loadGanttView() {
        this.logger.log('INFO', 'Loading Gantt chart view - NO AUTO-LOADING');
        this.currentView = 'gantt';
        
        // Navigate to Gantt chart page
        window.location.href = '/gantt';
    }
    
    loadReportsView() {
        this.logger.log('INFO', 'Loading reports view - NO AUTO-LOADING');
        this.currentView = 'reports';
        
        // Navigate to reports page
        window.location.href = '/reports';
    }
}

// Global function for manual dashboard data loading
function loadDashboardData() {
    console.log('Manual dashboard data loading triggered');
    // This will be implemented when needed
}

// Create global instance - NO AUTO-INITIALIZATION
window.navigationManager = new NavigationManager();

// Test function for debugging
window.testNavigation = function() {
    console.log('🧪 TEST: Testing navigation...');
    console.log('🧪 TEST: Current URL:', window.location.href);
    
    const navLinks = document.querySelectorAll('.nav-link');
    console.log('🧪 TEST: Found', navLinks.length, 'navigation links');
    
    navLinks.forEach((link, index) => {
        const href = link.getAttribute('href');
        console.log(`🧪 TEST: Link ${index}: href="${href}", text="${link.textContent.trim()}"`);
        
        // Test clicking the link
        if (href === '/backlog') {
            console.log('🧪 TEST: Testing backlog link click...');
            link.click();
        }
    });
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationManager;
}
