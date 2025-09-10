// GenAI Metrics Dashboard - Main JavaScript

// Global variables
let apiBaseUrl = '/api/v1';
let currentUser = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize charts if present
    initializeCharts();
    
    // Load user data
    loadUserData();
}

// Set up event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
    
    // Form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Modal events
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
        trigger.addEventListener('click', handleModalOpen);
    });
    
    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', handleSearch);
    });
    
    // Filter functionality
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', handleFilter);
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize charts
function initializeCharts() {
    // Initialize any charts on the page
    const chartElements = document.querySelectorAll('canvas[data-chart]');
    chartElements.forEach(canvas => {
        const chartType = canvas.dataset.chart;
        const chartData = JSON.parse(canvas.dataset.data || '{}');
        createChart(canvas, chartType, chartData);
    });
}

// Create chart
function createChart(canvas, type, data) {
    const ctx = canvas.getContext('2d');
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: data.title || 'Chart'
            }
        }
    };
    
    switch (type) {
        case 'bar':
            return new Chart(ctx, {
                type: 'bar',
                data: data,
                options: { ...defaultOptions, ...data.options }
            });
        case 'line':
            return new Chart(ctx, {
                type: 'line',
                data: data,
                options: { ...defaultOptions, ...data.options }
            });
        case 'pie':
            return new Chart(ctx, {
                type: 'pie',
                data: data,
                options: { ...defaultOptions, ...data.options }
            });
        case 'doughnut':
            return new Chart(ctx, {
                type: 'doughnut',
                data: data,
                options: { ...defaultOptions, ...data.options }
            });
        default:
            console.warn('Unknown chart type:', type);
    }
}

// Load user data
async function loadUserData() {
    try {
        const response = await fetch(`${apiBaseUrl}/user/profile`);
        if (response.ok) {
            currentUser = await response.json();
            updateUserInterface();
        }
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

// Update user interface based on user data
function updateUserInterface() {
    if (currentUser) {
        // Update user name in navigation
        const userElements = document.querySelectorAll('.user-name');
        userElements.forEach(el => {
            el.textContent = currentUser.name || 'User';
        });
        
        // Update user avatar
        const avatarElements = document.querySelectorAll('.user-avatar');
        avatarElements.forEach(el => {
            el.textContent = (currentUser.name || 'U').charAt(0).toUpperCase();
        });
    }
}

// Handle navigation
function handleNavigation(event) {
    const link = event.currentTarget;
    const href = link.getAttribute('href');
    
    if (href && href.startsWith('/')) {
        event.preventDefault();
        navigateToPage(href);
    }
}

// Navigate to page
function navigateToPage(url) {
    // Add loading state
    document.body.classList.add('loading');
    
    // Simulate navigation (in a real app, this would use a router)
    setTimeout(() => {
        window.location.href = url;
    }, 300);
}

// Handle form submission
function handleFormSubmit(event) {
    const form = event.currentTarget;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Add loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
    }
    
    // Handle form submission
    const action = form.getAttribute('action');
    const method = form.getAttribute('method') || 'POST';
    
    if (action) {
        event.preventDefault();
        submitForm(action, method, data);
    }
}

// Submit form data
async function submitForm(url, method, data) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            showSuccess('Form submitted successfully!');
            
            // Reset form
            const form = document.querySelector(`form[action="${url}"]`);
            if (form) {
                form.reset();
            }
            
            // Refresh data if needed
            if (typeof refreshData === 'function') {
                refreshData();
            }
        } else {
            const error = await response.json();
            showError(error.message || 'An error occurred');
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        showError('Network error occurred');
    } finally {
        // Remove loading state
        const submitBtn = document.querySelector('button[type="submit"]:disabled');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit';
        }
    }
}

// Handle modal open
function handleModalOpen(event) {
    const trigger = event.currentTarget;
    const modalId = trigger.getAttribute('data-bs-target');
    const modal = document.querySelector(modalId);
    
    if (modal) {
        // Load modal content if needed
        const dataUrl = trigger.getAttribute('data-url');
        if (dataUrl) {
            loadModalContent(modal, dataUrl);
        }
    }
}

// Load modal content
async function loadModalContent(modal, url) {
    try {
        const response = await fetch(url);
        if (response.ok) {
            const content = await response.text();
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
                modalBody.innerHTML = content;
            }
        }
    } catch (error) {
        console.error('Error loading modal content:', error);
    }
}

// Handle search
function handleSearch(event) {
    const input = event.currentTarget;
    const searchTerm = input.value.toLowerCase();
    const searchContainer = input.closest('.search-container');
    
    if (searchContainer) {
        const items = searchContainer.querySelectorAll('.searchable-item');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
}

// Handle filter
function handleFilter(event) {
    const select = event.currentTarget;
    const filterValue = select.value;
    const filterContainer = select.closest('.filter-container');
    
    if (filterContainer) {
        const items = filterContainer.querySelectorAll('.filterable-item');
        items.forEach(item => {
            const itemValue = item.getAttribute('data-filter-value');
            if (filterValue === 'all' || itemValue === filterValue) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
}

// API Helper Functions
async function apiCall(endpoint, method = 'GET', data = null, retries = 3) {
    const apiLogger = new FrontendLogger('api', 'DEBUG');
    apiLogger.logFunctionEntry('apiCall', [endpoint, method, data, retries]);
    const startTime = performance.now();
    
    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                // Add timeout
                signal: AbortSignal.timeout(10000) // 10 second timeout
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            apiLogger.log('INFO', `🔄 Making API call (attempt ${attempt}/${retries})`, {
                'endpoint': endpoint,
                'method': method,
                'full_url': `${apiBaseUrl}${endpoint}`,
                'has_data': !!data,
                'data_size': data ? JSON.stringify(data).length : 0,
                'attempt': attempt,
                'max_retries': retries,
                'timestamp': new Date().toISOString()
            });
            
            const response = await fetch(`${apiBaseUrl}${endpoint}`, options);
            const responseTime = performance.now() - startTime;
            
            apiLogger.log('INFO', `📡 API response received`, {
                'endpoint': endpoint,
                'status': response.status,
                'status_text': response.statusText,
                'response_time_ms': responseTime,
                'response_ok': response.ok,
                'attempt': attempt,
                'timestamp': new Date().toISOString()
            });
            
            if (response.ok) {
                const result = await response.json();
                apiLogger.log('SUCCESS', `✅ API call successful`, {
                    'endpoint': endpoint,
                    'method': method,
                    'status': response.status,
                    'response_time_ms': responseTime,
                    'result_keys': Object.keys(result || {}),
                    'result_size_bytes': JSON.stringify(result).length,
                    'attempt': attempt,
                    'timestamp': new Date().toISOString()
                });
                
                apiLogger.logApiCall(method, endpoint, response.status, responseTime, data, result);
                apiLogger.logFunctionExit('apiCall', result, responseTime);
                return result;
            } else {
                const errorText = await response.text();
                let errorMessage = `API call failed with status ${response.status}`;
                
                apiLogger.log('ERROR', `❌ API call failed`, {
                    'endpoint': endpoint,
                    'method': method,
                    'status': response.status,
                    'status_text': response.statusText,
                    'response_time_ms': responseTime,
                    'error_text': errorText,
                    'attempt': attempt,
                    'timestamp': new Date().toISOString()
                });
                
                try {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.message || errorData.detail || errorMessage;
                    apiLogger.log('INFO', `📝 Parsed error data`, {
                        'error_data': errorData,
                        'error_message': errorMessage,
                        'timestamp': new Date().toISOString()
                    });
                } catch {
                    errorMessage = errorText || errorMessage;
                    apiLogger.log('INFO', `📝 Using raw error text`, {
                        'error_text': errorText,
                        'error_message': errorMessage,
                        'timestamp': new Date().toISOString()
                    });
                }
                
                // Don't retry on client errors (4xx)
                if (response.status >= 400 && response.status < 500) {
                    throw new Error(errorMessage);
                }
                
                // Retry on server errors (5xx) or network issues
                if (attempt === retries) {
                    throw new Error(errorMessage);
                }
                
                console.warn(`API call failed (attempt ${attempt}/${retries}):`, errorMessage);
                await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoff
            }
                } catch (error) {
                    const responseTime = performance.now() - startTime;
                    apiLogger.logError('apiCall', error, { 
                        attempt, 
                        retries, 
                        endpoint, 
                        method, 
                        responseTime 
                    });
                    
                    if (attempt === retries) {
                        console.error('API call error:', error);
                        throw error;
                    }
            
            console.warn(`API call failed (attempt ${attempt}/${retries}):`, error.message);
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // Exponential backoff
        }
    }
}

// Load data from API
async function loadData(endpoint, containerId, templateFunction) {
    try {
        const data = await apiCall(endpoint);
        const container = document.getElementById(containerId);
        
        if (container && templateFunction) {
            container.innerHTML = templateFunction(data);
        }
        
        return data;
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load data');
    }
}

// Show success message
function showSuccess(message) {
    showFlashMessage(message, 'success');
}

// Show error message
function showError(message) {
    showFlashMessage(message, 'danger');
}

// Show warning message
function showWarning(message) {
    showFlashMessage(message, 'warning');
}

// Show info message
function showInfo(message) {
    showFlashMessage(message, 'info');
}

// Show flash message
function showFlashMessage(message, type = 'info') {
    const flashContainer = document.getElementById('flash-messages');
    if (!flashContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    flashContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format percentage
function formatPercentage(value) {
    return `${Math.round(value * 100)}%`;
}

// Get status badge class
function getStatusBadgeClass(status) {
    const statusMap = {
        'active': 'status-active',
        'completed': 'status-completed',
        'at-risk': 'status-at-risk',
        'off-track': 'status-off-track'
    };
    return statusMap[status.toLowerCase()] || 'status-active';
}

// Get priority badge class
function getPriorityBadgeClass(priority) {
    const priorityMap = {
        'critical': 'priority-critical',
        'high': 'priority-high',
        'medium': 'priority-medium',
        'low': 'priority-low'
    };
    return priorityMap[priority.toLowerCase()] || 'priority-medium';
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Global retry functions for all navigation and dashboard components
window.retryAllLinks = async function() {
    if (window.navigationManager) {
        return await window.navigationManager.retryAllLinks();
    } else {
        console.error('Navigation manager not available');
        return { success: false, message: 'Navigation manager not available' };
    }
};

window.retryCurrentView = async function() {
    if (window.navigationManager) {
        return await window.navigationManager.retryCurrentView();
    } else {
        console.error('Navigation manager not available');
        return { success: false, message: 'Navigation manager not available' };
    }
};

window.retryDashboard = async function() {
    if (window.DashboardManager) {
        return await window.DashboardManager.retryFailedComponents();
    } else {
        console.error('Dashboard manager not available');
        return { success: false, message: 'Dashboard manager not available' };
    }
};

// Export functions for global use
window.GenAIDashboard = {
    apiCall,
    loadData,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    formatDate,
    formatCurrency,
    formatPercentage,
    getStatusBadgeClass,
    getPriorityBadgeClass,
    debounce,
    throttle,
    init: function() {
        console.log('🚀 GenAIDashboard.init() called - AUTO-LOADING COMPLETELY DISABLED');
        // COMPLETELY DISABLED AUTO-LOADING - Dashboard will only load when manually triggered
        // if (typeof loadDashboardManually === 'function') {
        //     loadDashboardManually(); // DISABLED
        // } else if (typeof initializeDashboard === 'function') {
        //     initializeDashboard(); // DISABLED
        // }
        // if (typeof setupRealTimeUpdates === 'function') {
        //     setupRealTimeUpdates(); // DISABLED
        // }
        if (typeof setupDashboardCustomization === 'function') {
            setupDashboardCustomization();
        }
        console.log('✅ GenAIDashboard.init() completed - Manual loading only');
    }
};
