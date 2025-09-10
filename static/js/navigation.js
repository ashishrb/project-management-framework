/**
 * Navigation System for Cross-View Integration
 * Handles breadcrumbs, deep linking, and context preservation
 */

class NavigationManager {
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.breadcrumbs = [];
        this.context = {};
        this.keyboardShortcuts = new Map();
        
        this.init();
    }
    
    init() {
        this.setupBreadcrumbs();
        this.setupDeepLinking();
        this.setupKeyboardShortcuts();
        this.setupContextPreservation();
        this.setupQuickNavigation();
    }
    
    // ==================== BREADCRUMB NAVIGATION ====================
    
    setupBreadcrumbs() {
        this.updateBreadcrumbContainer();
        
        // Listen for navigation changes
        this.stateManager.subscribe('navigation', (newNav, oldNav) => {
            this.updateBreadcrumbs(newNav);
        });
    }
    
    updateBreadcrumbs(navigation) {
        const { view, params } = navigation;
        
        // Add to breadcrumb trail
        this.breadcrumbs.push({
            view,
            params,
            timestamp: new Date(),
            title: this.getViewTitle(view, params)
        });
        
        // Keep only last 10 breadcrumbs
        if (this.breadcrumbs.length > 10) {
            this.breadcrumbs = this.breadcrumbs.slice(-10);
        }
        
        this.renderBreadcrumbs();
    }
    
    getViewTitle(view, params) {
        const titles = {
            'dashboard': 'Dashboard',
            'projects': 'Projects',
            'project-detail': `Project: ${params.projectName || params.id || 'Unknown'}`,
            'resources': 'Resources',
            'resource-detail': `Resource: ${params.resourceName || params.id || 'Unknown'}`,
            'risks': 'Risk Management',
            'risk-detail': `Risk: ${params.riskName || params.id || 'Unknown'}`,
            'gantt': 'Gantt Chart',
            'reports': 'Reports',
            'settings': 'Settings'
        };
        
        return titles[view] || view.charAt(0).toUpperCase() + view.slice(1);
    }
    
    renderBreadcrumbs() {
        const container = document.getElementById('breadcrumb-container');
        if (!container) return;
        
        container.innerHTML = this.breadcrumbs.map((crumb, index) => {
            const isLast = index === this.breadcrumbs.length - 1;
            const separator = isLast ? '' : '<span class="breadcrumb-separator">/</span>';
            
            return `
                <span class="breadcrumb-item ${isLast ? 'active' : ''}" 
                      data-view="${crumb.view}" 
                      data-params='${JSON.stringify(crumb.params)}'>
                    ${crumb.title}
                </span>
                ${separator}
            `;
        }).join('');
        
        // Add click handlers
        container.querySelectorAll('.breadcrumb-item:not(.active)').forEach(item => {
            item.addEventListener('click', () => {
                const view = item.dataset.view;
                const params = JSON.parse(item.dataset.params);
                this.navigateTo(view, params);
            });
        });
    }
    
    updateBreadcrumbContainer() {
        // Create breadcrumb container if it doesn't exist
        let container = document.getElementById('breadcrumb-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'breadcrumb-container';
            container.className = 'breadcrumb-container';
            
            // Insert after navigation
            const nav = document.querySelector('.navbar');
            if (nav) {
                nav.insertAdjacentElement('afterend', container);
            }
        }
    }
    
    // ==================== DEEP LINKING ====================
    
    setupDeepLinking() {
        // Handle browser back/forward
        window.addEventListener('popstate', (event) => {
            if (event.state) {
                this.navigateTo(event.state.view, event.state.params, false);
            }
        });
        
        // Handle initial page load
        this.handleInitialRoute();
    }
    
    handleInitialRoute() {
        const path = window.location.pathname;
        const params = this.parseUrlParams();
        
        // Map URL paths to views
        const routeMap = {
            '/': 'dashboard',
            '/dashboard': 'dashboard',
            '/projects': 'projects',
            '/resources': 'resources',
            '/risks': 'risks',
            '/gantt': 'gantt',
            '/reports': 'reports',
            '/settings': 'settings'
        };
        
        const view = routeMap[path] || 'dashboard';
        this.navigateTo(view, params, false);
    }
    
    parseUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const params = {};
        
        for (const [key, value] of urlParams) {
            // Try to parse as JSON, fallback to string
            try {
                params[key] = JSON.parse(value);
            } catch {
                params[key] = value;
            }
        }
        
        return params;
    }
    
    navigateTo(view, params = {}, updateHistory = true) {
        // Update state manager
        this.stateManager.navigateTo(view, params);
        
        // Update URL
        if (updateHistory) {
            const url = this.buildUrl(view, params);
            window.history.pushState({ view, params }, '', url);
        }
        
        // Update page title
        document.title = `${this.getViewTitle(view, params)} - GenAI Metrics Dashboard`;
        
        // Load view content
        this.loadViewContent(view, params);
    }
    
    buildUrl(view, params) {
        const baseUrl = window.location.origin;
        const pathMap = {
            'dashboard': '/',
            'projects': '/projects',
            'resources': '/resources',
            'risks': '/risks',
            'gantt': '/gantt',
            'reports': '/reports',
            'settings': '/settings'
        };
        
        let path = pathMap[view] || '/';
        
        // Add query parameters
        const queryParams = new URLSearchParams();
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                queryParams.set(key, JSON.stringify(params[key]));
            }
        });
        
        if (queryParams.toString()) {
            path += '?' + queryParams.toString();
        }
        
        return baseUrl + path;
    }
    
    // ==================== VIEW LOADING ====================
    
    async fetchWithRetry(url, options = {}, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const response = await fetch(url, {
                    ...options,
                    signal: AbortSignal.timeout(10000) // 10 second timeout
                });
                
                if (response.ok) {
                    return response;
                }
                
                // Don't retry on client errors (4xx)
                if (response.status >= 400 && response.status < 500) {
                    throw new Error(`Client error: ${response.status}`);
                }
                
                // Retry on server errors (5xx) or network issues
                if (attempt === maxRetries) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                console.warn(`Fetch failed (attempt ${attempt}/${maxRetries}):`, response.status);
                await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoff
                
            } catch (error) {
                if (attempt === maxRetries) {
                    throw error;
                }
                
                console.warn(`Fetch error (attempt ${attempt}/${maxRetries}):`, error.message);
                await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoff
            }
        }
    }
    
    setErrorState(view, error, retryCount) {
        this.stateManager.setState('lastError', {
            view,
            error: error.message,
            retryCount,
            timestamp: new Date()
        });
    }
    
    clearErrorState() {
        this.stateManager.setState('lastError', null);
    }
    
    async loadViewContent(view, params, retryCount = 0) {
        const contentContainer = document.getElementById('main-content');
        if (!contentContainer) return;
        
        // Show loading state
        contentContainer.innerHTML = `
            <div class="loading-spinner d-flex align-items-center justify-content-center" style="height: 400px;">
                <div class="text-center">
                    <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <h4>Loading ${view}...</h4>
                    <p class="text-muted">Please wait while we fetch the latest data</p>
                </div>
            </div>
        `;
        
        try {
            // Map view names to actual routes
            const routeMap = {
                'dashboard': '/dashboard',
                'projects': '/projects',
                'resources': '/resources',
                'reports': '/reports',
                'analytics': '/analytics',
                'settings': '/settings'
            };
            
            const route = routeMap[view] || `/${view}`;
            
            // Load view with retry logic
            const response = await this.fetchWithRetry(route, {
                method: 'GET',
                headers: {
                    'Content-Type': 'text/html',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            }, 3);
            
            if (!response.ok) {
                throw new Error(`Failed to load ${view} (HTTP ${response.status})`);
            }
            
            let html = await response.text();
            
            // Replace placeholders with actual data
            html = await this.replacePlaceholders(html, params);
            
            contentContainer.innerHTML = html;
            
            // Initialize view-specific JavaScript
            this.initializeView(view, params);
            
            // Clear any previous error states
            this.clearErrorState();
            
        } catch (error) {
            console.error(`Error loading view ${view} (attempt ${retryCount + 1}):`, error);
            
            // Show error with retry options
            contentContainer.innerHTML = `
                <div class="error-message text-center" style="padding: 2rem;">
                    <div class="alert alert-danger" role="alert">
                        <h3><i class="fas fa-exclamation-triangle me-2"></i>Error Loading View</h3>
                        <p class="mb-3">Failed to load ${view}: ${error.message}</p>
                        <div class="btn-group" role="group">
                            <button class="btn btn-primary" onclick="navigationManager.loadViewContent('${view}', ${JSON.stringify(params || {}).replace(/"/g, '&quot;')}, ${retryCount + 1})">
                                <i class="fas fa-redo me-1"></i>Retry (${retryCount + 1}/3)
                            </button>
                            <button class="btn btn-outline-secondary" onclick="location.reload()">
                                <i class="fas fa-refresh me-1"></i>Reload Page
                            </button>
                            <button class="btn btn-outline-info" onclick="navigationManager.loadViewContent('dashboard', {}, 0)">
                                <i class="fas fa-home me-1"></i>Go to Dashboard
                            </button>
                        </div>
                        ${retryCount >= 2 ? `
                            <div class="mt-3">
                                <small class="text-muted">
                                    Multiple retry attempts failed. Please check your connection or contact support.
                                </small>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            // Set error state for tracking
            this.setErrorState(view, error, retryCount);
        }
    }
    
    async replacePlaceholders(html, params) {
        // Replace common placeholders
        html = html.replace(/\{\{user\.name\}\}/g, this.stateManager.getState('user')?.name || 'User');
        html = html.replace(/\{\{currentView\}\}/g, this.stateManager.getState('currentView'));
        
        // Replace parameter placeholders
        Object.keys(params).forEach(key => {
            const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
            html = html.replace(regex, params[key] || '');
        });
        
        return html;
    }
    
    initializeView(view, params) {
        // Initialize view-specific functionality
        switch (view) {
            case 'dashboard':
                console.log('🔍 Checking GenAIDashboard availability...');
                console.log('window.GenAIDashboard:', window.GenAIDashboard);
                if (window.GenAIDashboard && typeof window.GenAIDashboard.init === 'function') {
                    console.log('✅ Calling GenAIDashboard.init()');
                    window.GenAIDashboard.init();
                } else {
                    console.error('❌ GenAIDashboard.init is not available');
                    console.log('Available methods:', window.GenAIDashboard ? Object.keys(window.GenAIDashboard) : 'GenAIDashboard not defined');
                    
                    // Retry after a short delay
                    setTimeout(() => {
                        console.log('🔄 Retrying GenAIDashboard.init()...');
                        if (window.GenAIDashboard && typeof window.GenAIDashboard.init === 'function') {
                            console.log('✅ Retry successful - calling GenAIDashboard.init()');
                            window.GenAIDashboard.init();
                        } else {
                            console.error('❌ Retry failed - GenAIDashboard.init still not available');
                        }
                    }, 100);
                }
                break;
                
            case 'projects':
                this.initializeProjectView(params);
                break;
                
            case 'resources':
                this.initializeResourceView(params);
                break;
                
            case 'risks':
                this.initializeRiskView(params);
                break;
                
            default:
                console.log(`No specific initialization for view: ${view}`);
        }
    }
    
    initializeProjectView(params) {
        // Load project data and initialize charts
        this.stateManager.loadData('projects').then(() => {
            // Initialize project-specific components
            console.log('Project view initialized');
        });
    }
    
    initializeResourceView(params) {
        // Load resource data and initialize components
        this.stateManager.loadData('resources').then(() => {
            console.log('Resource view initialized');
        });
    }
    
    initializeRiskView(params) {
        // Load risk data and initialize components
        this.stateManager.loadData('risks').then(() => {
            console.log('Risk view initialized');
        });
    }
    
    // ==================== KEYBOARD SHORTCUTS ====================
    
    setupKeyboardShortcuts() {
        this.keyboardShortcuts.set('ctrl+d', () => this.navigateTo('dashboard'));
        this.keyboardShortcuts.set('ctrl+p', () => this.navigateTo('projects'));
        this.keyboardShortcuts.set('ctrl+r', () => this.navigateTo('resources'));
        this.keyboardShortcuts.set('ctrl+k', () => this.navigateTo('risks'));
        this.keyboardShortcuts.set('ctrl+g', () => this.navigateTo('gantt'));
        this.keyboardShortcuts.set('ctrl+shift+r', () => this.navigateTo('reports'));
        this.keyboardShortcuts.set('ctrl+,', () => this.navigateTo('settings'));
        this.keyboardShortcuts.set('alt+left', () => this.goBack());
        this.keyboardShortcuts.set('alt+right', () => this.goForward());
        this.keyboardShortcuts.set('ctrl+shift+n', () => this.showQuickNavigation());
        
        document.addEventListener('keydown', (event) => {
            const shortcut = this.getShortcutKey(event);
            const handler = this.keyboardShortcuts.get(shortcut);
            
            if (handler) {
                event.preventDefault();
                handler();
            }
        });
    }
    
    getShortcutKey(event) {
        const parts = [];
        
        if (event.ctrlKey) parts.push('ctrl');
        if (event.altKey) parts.push('alt');
        if (event.shiftKey) parts.push('shift');
        if (event.metaKey) parts.push('meta');
        
        parts.push(event.key.toLowerCase());
        
        return parts.join('+');
    }
    
    // ==================== CONTEXT PRESERVATION ====================
    
    setupContextPreservation() {
        // Save context before navigation
        this.stateManager.subscribe('navigation', (newNav, oldNav) => {
            this.saveContext(oldNav);
        });
        
        // Restore context on page load
        this.restoreContext();
    }
    
    saveContext(navigation) {
        if (navigation) {
            const context = {
                view: navigation.view,
                params: navigation.params,
                timestamp: new Date(),
                scrollPosition: window.scrollY,
                formData: this.collectFormData()
            };
            
            sessionStorage.setItem('navigation-context', JSON.stringify(context));
        }
    }
    
    restoreContext() {
        const saved = sessionStorage.getItem('navigation-context');
        if (saved) {
            try {
                const context = JSON.parse(saved);
                this.context = context;
                
                // Restore scroll position
                if (context.scrollPosition) {
                    window.scrollTo(0, context.scrollPosition);
                }
                
                // Restore form data
                this.restoreFormData(context.formData);
                
            } catch (error) {
                console.error('Error restoring context:', error);
            }
        }
    }
    
    collectFormData() {
        const forms = document.querySelectorAll('form');
        const formData = {};
        
        forms.forEach((form, index) => {
            const data = new FormData(form);
            formData[`form_${index}`] = Object.fromEntries(data);
        });
        
        return formData;
    }
    
    restoreFormData(formData) {
        if (!formData) return;
        
        Object.keys(formData).forEach(formKey => {
            const form = document.querySelector(`form:nth-of-type(${formKey.split('_')[1]})`);
            if (form) {
                Object.keys(formData[formKey]).forEach(name => {
                    const input = form.querySelector(`[name="${name}"]`);
                    if (input) {
                        input.value = formData[formKey][name];
                    }
                });
            }
        });
    }
    
    // ==================== QUICK NAVIGATION ====================
    
    setupQuickNavigation() {
        // Create quick navigation overlay
        this.createQuickNavigationOverlay();
    }
    
    createQuickNavigationOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'quick-nav-overlay';
        overlay.className = 'quick-nav-overlay';
        overlay.innerHTML = `
            <div class="quick-nav-content">
                <div class="quick-nav-header">
                    <h3>Quick Navigation</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="quick-nav-items">
                    <div class="nav-item" data-view="dashboard">
                        <span class="nav-icon">📊</span>
                        <span class="nav-title">Dashboard</span>
                        <span class="nav-shortcut">Ctrl+D</span>
                    </div>
                    <div class="nav-item" data-view="projects">
                        <span class="nav-icon">📁</span>
                        <span class="nav-title">Projects</span>
                        <span class="nav-shortcut">Ctrl+P</span>
                    </div>
                    <div class="nav-item" data-view="resources">
                        <span class="nav-icon">👥</span>
                        <span class="nav-title">Resources</span>
                        <span class="nav-shortcut">Ctrl+R</span>
                    </div>
                    <div class="nav-item" data-view="risks">
                        <span class="nav-icon">⚠️</span>
                        <span class="nav-title">Risk Management</span>
                        <span class="nav-shortcut">Ctrl+K</span>
                    </div>
                    <div class="nav-item" data-view="gantt">
                        <span class="nav-icon">📅</span>
                        <span class="nav-title">Gantt Chart</span>
                        <span class="nav-shortcut">Ctrl+G</span>
                    </div>
                    <div class="nav-item" data-view="reports">
                        <span class="nav-icon">📈</span>
                        <span class="nav-title">Reports</span>
                        <span class="nav-shortcut">Ctrl+Shift+R</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Add event listeners
        overlay.querySelector('.close-btn').addEventListener('click', () => {
            this.hideQuickNavigation();
        });
        
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.hideQuickNavigation();
            }
        });
        
        overlay.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const view = item.dataset.view;
                this.navigateTo(view);
                this.hideQuickNavigation();
            });
        });
    }
    
    showQuickNavigation() {
        const overlay = document.getElementById('quick-nav-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
            overlay.querySelector('.quick-nav-content').focus();
        }
    }
    
    hideQuickNavigation() {
        const overlay = document.getElementById('quick-nav-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    // ==================== UTILITY METHODS ====================
    
    goBack() {
        this.stateManager.goBack();
    }
    
    goForward() {
        // Implement forward navigation if needed
        console.log('Forward navigation not implemented');
    }
    
    getCurrentView() {
        return this.stateManager.getState('currentView');
    }
    
    getCurrentParams() {
        return this.stateManager.getState('navigationParams');
    }
    
    // ==================== CLEANUP ====================
    
    destroy() {
        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeydown);
        window.removeEventListener('popstate', this.handlePopState);
        
        // Remove quick navigation overlay
        const overlay = document.getElementById('quick-nav-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    // ==================== RETRY MECHANISMS ====================
    
    async retryAllFailedViews() {
        console.log('🔄 Retrying all failed views...');
        
        const lastError = this.stateManager.getState('lastError');
        if (!lastError) {
            console.log('No failed views to retry');
            return;
        }
        
        const { view, params } = lastError;
        await this.loadViewContent(view, params, 0);
    }
    
    async retryCurrentView() {
        const currentView = this.stateManager.getState('currentView');
        const currentParams = this.stateManager.getState('currentParams') || {};
        
        if (currentView) {
            console.log(`🔄 Retrying current view: ${currentView}`);
            await this.loadViewContent(currentView, currentParams, 0);
        }
    }
    
    // Global retry function for all navigation
    async retryAllLinks() {
        console.log('🔄 Retrying all navigation links...');
        
        // Get all navigation links
        const navLinks = document.querySelectorAll('a[data-view], .nav-link[data-view]');
        const failedLinks = [];
        
        // Test each link
        for (const link of navLinks) {
            const view = link.getAttribute('data-view');
            if (view) {
                try {
                    const routeMap = {
                        'dashboard': '/dashboard',
                        'projects': '/projects',
                        'resources': '/resources',
                        'reports': '/reports',
                        'analytics': '/analytics',
                        'settings': '/settings'
                    };
                    
                    const route = routeMap[view] || `/${view}`;
                    const response = await fetch(route, { method: 'GET' });
                    
                    if (!response.ok) {
                        failedLinks.push({ view, route, status: response.status });
                    }
                } catch (error) {
                    failedLinks.push({ view, route: `/${view}`, error: error.message });
                }
            }
        }
        
        if (failedLinks.length === 0) {
            console.log('✅ All navigation links are working');
            return { success: true, message: 'All navigation links are working' };
        } else {
            console.warn(`⚠️ Found ${failedLinks.length} failed links:`, failedLinks);
            return { success: false, failedLinks, message: `Found ${failedLinks.length} failed navigation links` };
        }
    }
}

// Initialize navigation manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (window.stateManager) {
        window.navigationManager = new NavigationManager(window.stateManager);
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationManager;
}
