/**
 * Main JavaScript - COMPLETELY REWRITTEN FROM SCRATCH
 * NO AUTO-LOADING - MANUAL LOADING ONLY
 */

// Global GenAIDashboard object - COMPLETELY DISABLED
window.GenAIDashboard = {
    init: function() {
        console.log('🚀 GenAIDashboard.init() called - COMPLETELY DISABLED');
        // COMPLETELY DISABLED - No dashboard initialization
        console.log('✅ GenAIDashboard.init() completed - No auto-loading');
    }
};

// Global functions - NO AUTO-LOADING
window.loadDashboardManually = function() {
    console.log('Manual dashboard loading triggered');
    // This will be implemented when needed
};

window.initializeDashboard = function() {
    console.log('Manual dashboard initialization triggered');
    // This will be implemented when needed
};

window.setupRealTimeUpdates = function() {
    console.log('Manual real-time updates setup triggered');
    // This will be implemented when needed
};

window.setupDashboardCustomization = function() {
    console.log('Manual dashboard customization setup triggered');
    // This will be implemented when needed
};

// DOM Content Loaded - NO AUTO-LOADING
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOMContentLoaded - NO AUTO-LOADING');
    console.log('🔍 DEBUG: Current URL:', window.location.href);
    console.log('🔍 DEBUG: Navigation manager exists:', !!window.navigationManager);
    
    // Only initialize navigation manager manually
    if (window.navigationManager) {
        console.log('🔍 DEBUG: Initializing navigation manager...');
        window.navigationManager.init();
        console.log('🔍 DEBUG: Navigation manager initialized');
    } else {
        console.log('❌ DEBUG: Navigation manager not found!');
    }
    
    // Debug all navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    console.log('🔍 DEBUG: Found', navLinks.length, 'navigation links on page load');
    navLinks.forEach((link, index) => {
        console.log(`🔍 DEBUG: Link ${index}: href="${link.getAttribute('href')}", text="${link.textContent.trim()}"`);
    });
    
    console.log('✅ DOMContentLoaded - Manual loading only');
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        GenAIDashboard: window.GenAIDashboard,
        loadDashboardManually: window.loadDashboardManually,
        initializeDashboard: window.initializeDashboard,
        setupRealTimeUpdates: window.setupRealTimeUpdates,
        setupDashboardCustomization: window.setupDashboardCustomization
    };
}
