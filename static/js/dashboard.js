// GenAI Metrics Dashboard - Advanced Dashboard JavaScript

// Global dashboard variables
let dashboardCharts = {};
let dashboardData = {};
let refreshInterval = null;
let dashboardInitialized = false; // Guard to prevent double initialization
let loadDashboardDataCallCount = 0; // Track function calls to identify loops

// Global initialization flag to prevent multiple initializations across modules
window.dashboardInitialized = false;
// DISABLED AUTO-LOADING - Dashboard will only load when manually triggered
window.autoLoadingDisabled = true;

// Dashboard logger is initialized in logging.js
let isRealTimeEnabled = false; // DISABLED BY DEFAULT - Manual loading only

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    if (window.dashboardRefreshInterval) {
        clearInterval(window.dashboardRefreshInterval);
        window.dashboardRefreshInterval = null;
    }
    window.dashboardInitialized = false;
});

// Initialize dashboard - COMPLETELY DISABLED AUTO-LOADING
document.addEventListener('DOMContentLoaded', function() {
    // Check global initialization flag first
    if (window.dashboardInitialized) {
        console.log('⏸️ Dashboard already initialized globally, skipping');
        return;
    }
    
    try {
        console.log('🚀 DOMContentLoaded - Dashboard setup completed (AUTO-LOADING DISABLED)');
        // COMPLETELY DISABLED AUTO-LOADING - Dashboard will only load when manually triggered
        // initializeDashboard(); // DISABLED
        // setupRealTimeUpdates(); // DISABLED
        setupDashboardCustomization();
        console.log('✅ DOMContentLoaded - Dashboard setup completed - click Dashboard link to load manually');
    } catch (error) {
        console.error('❌ DOMContentLoaded - Dashboard setup failed:', error);
        window.dashboardInitialized = false; // Reset on error
        // Prevent infinite loops by not retrying on error
    }
});

// Initialize dashboard
function initializeDashboard() {
    dashboardLogger.logFunctionEntry('initializeDashboard', [], {
        'documentReadyState': document.readyState,
        'dashboardInitialized': dashboardInitialized,
        'GenAIDashboardType': typeof GenAIDashboard,
        'GenAIDashboardApiCallType': typeof GenAIDashboard?.apiCall
    });
    
    // Prevent double initialization
    if (dashboardInitialized) {
        dashboardLogger.log('WARN', 'Dashboard already initialized, skipping...', {
            'reason': 'double_initialization_prevented',
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    dashboardLogger.log('INFO', '🚀 Initializing GenAI Metrics Dashboard...', {
        'GenAIDashboard_available': typeof GenAIDashboard,
        'GenAIDashboard_apiCall_available': typeof GenAIDashboard?.apiCall,
        'document_ready_state': document.readyState
    });
    
    // Wait for DOM to be fully ready
    if (document.readyState === 'loading') {
        dashboardLogger.log('INFO', 'DOM still loading, waiting for DOMContentLoaded event');
        // Note: DOMContentLoaded listener is already set up at the top of the file
        // No need to add another one here
    } else {
        dashboardLogger.log('INFO', 'DOM already ready, proceeding with initialization');
        initializeDashboardComponents();
    }
}

// Initialize dashboard components
function initializeDashboardComponents() {
    dashboardLogger.logFunctionEntry('initializeDashboardComponents');
    
    // Prevent double initialization
    if (dashboardInitialized) {
        dashboardLogger.log('WARN', '⏸️ Dashboard components already initialized, skipping...', {
            'reason': 'double_initialization_prevented',
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    // Mark as initialized BEFORE calling loadDashboardData to prevent race conditions
    dashboardInitialized = true;
    
    dashboardLogger.log('INFO', '📊 Starting loadDashboardData...', {
        'step': 'data_loading',
        'timestamp': new Date().toISOString()
    });
    loadDashboardData();
    
    // Initialize charts immediately - no delay needed with proper DOM checks
    dashboardLogger.log('INFO', '📈 Starting initializeAllCharts...', {
        'step': 'chart_initialization',
        'timestamp': new Date().toISOString()
    });
    initializeAllCharts();
    
    // Setup event listeners
    dashboardLogger.log('INFO', '🎧 Setting up event listeners...', {
        'step': 'event_listeners',
        'timestamp': new Date().toISOString()
    });
    setupEventListeners();
    
    // Setup dashboard interactions
    dashboardLogger.log('INFO', '⚙️ Setting up dashboard interactions...', {
        'step': 'dashboard_interactions',
        'timestamp': new Date().toISOString()
    });
    setupDashboardInteractions();
    dashboardLogger.log('SUCCESS', '✅ Dashboard initialized successfully', {
        'step': 'initialization_complete',
        'dashboardInitialized': dashboardInitialized,
        'timestamp': new Date().toISOString()
    });
    
    dashboardLogger.logFunctionExit('initializeDashboardComponents', {
        'dashboardInitialized': dashboardInitialized,
        'initialization_time': new Date().toISOString()
    });
}

// Load dashboard data with improved error handling
async function loadDashboardData() {
    // Prevent recursive calls
    if (dashboardData.loading) {
        dashboardLogger.log('WARN', '⏸️ loadDashboardData already in progress, skipping', {
            'call_count': loadDashboardDataCallCount,
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    dashboardData.loading = true;
    dashboardLogger.logFunctionEntry('loadDashboardData');
    const startTime = performance.now();
    
    // Increment call counter and log call stack to identify what's triggering the loop
    loadDashboardDataCallCount++;
    const callStack = new Error().stack?.split('\n').slice(1, 6) || ['stack unavailable'];
    dashboardLogger.log('INFO', `🔄 loadDashboardData called (call #${loadDashboardDataCallCount})`, {
        'call_count': loadDashboardDataCallCount,
        'call_stack': callStack,
        'timestamp': new Date().toISOString()
    });
    
    try {
        dashboardLogger.log('INFO', 'Starting dashboard data load');
        console.log('📊 Loading dashboard data...');
        showLoadingState();
        
        // Define API endpoints with fallback data (apiBaseUrl already includes /api/v1)
        const apiEndpoints = [
            { key: 'overview', url: '/dashboards/all-projects', fallback: { current_projects: 0, approved_projects: 0, backlog_projects: 0, total_projects: 0 } },
            { key: 'genai', url: '/dashboards/genai-metrics', fallback: { active_features_by_function: [], backlogs_by_function: [], active_features_by_platform: [], backlogs_by_platform: [] } },
            { key: 'projectStatus', url: '/dashboards/summary-metrics', fallback: { active_projects: 0, completed_projects: 0, at_risk_projects: 0, off_track_projects: 0 } },
            { key: 'resourceUtil', url: '/resources/analytics/workload', fallback: [] },
            { key: 'riskOverview', url: '/reports/risks', fallback: [] },
            { key: 'recentActivity', url: '/reports/project-summary', fallback: [] },
            { key: 'aiInsights', url: '/ai-insights/insights', fallback: { insights: [] } }
        ];
        
        // Load data with individual error handling and retry logic
        const loadPromises = apiEndpoints.map(async (endpoint) => {
            const apiCallStartTime = performance.now();
            try {
                dashboardLogger.log('INFO', `🔄 Calling API: ${endpoint.url}`, {
                    'endpoint': endpoint.key,
                    'url': endpoint.url,
                    'method': 'GET',
                    'retries': 2,
                    'timestamp': new Date().toISOString(),
                    'GenAIDashboard_apiCall_type': typeof GenAIDashboard?.apiCall
                });
                
                const data = await GenAIDashboard.apiCall(endpoint.url, 'GET', null, 2); // 2 retries
                const apiCallEndTime = performance.now();
                const responseTime = apiCallEndTime - apiCallStartTime;
                
                dashboardLogger.log('SUCCESS', `✅ API call successful for ${endpoint.key}`, {
                    'endpoint': endpoint.key,
                    'url': endpoint.url,
                    'response_time_ms': responseTime,
                    'response_data_keys': Object.keys(data || {}),
                    'response_size_bytes': JSON.stringify(data).length,
                    'timestamp': new Date().toISOString()
                });
                
                return { key: endpoint.key, data, success: true, responseTime: responseTime };
            } catch (error) {
                const apiCallEndTime = performance.now();
                const responseTime = apiCallEndTime - apiCallStartTime;
                
                dashboardLogger.log('ERROR', `❌ API call failed for ${endpoint.key}`, {
                    'error_message': error.message,
                    'error_stack': error.stack,
                    'endpoint': endpoint.key,
                    'url': endpoint.url,
                    'response_time_ms': responseTime,
                    'fallback_used': true,
                    'fallback_data': endpoint.fallback,
                    'timestamp': new Date().toISOString()
                });
                
                return { 
                    key: endpoint.key, 
                    data: endpoint.fallback, 
                    success: false, 
                    error: error.message,
                    responseTime: responseTime
                };
            }
        });
        
        const results = await Promise.all(loadPromises);
        
        dashboardLogger.log('INFO', '📊 Dashboard API results received', {
            'total_endpoints': results.length,
            'results_summary': results.map(r => ({
                key: r.key,
                success: r.success,
                responseTime: r.responseTime,
                hasData: !!r.data,
                dataKeys: Object.keys(r.data || {}),
                error: r.error || null
            })),
            'timestamp': new Date().toISOString()
        });
        
        // Build dashboard data object
        dashboardData = {};
        let successCount = 0;
        let failedEndpoints = [];
        
        results.forEach(result => {
            dashboardLogger.log('INFO', `Processing result for ${result.key}`, {
                'endpoint': result.key,
                'success': result.success,
                'response_time_ms': result.responseTime,
                'data_type': typeof result.data,
                'data_keys': Object.keys(result.data || {}),
                'error': result.error || null,
                'timestamp': new Date().toISOString()
            });
            
            dashboardData[result.key] = result.data;
            if (result.success) {
                successCount++;
                dashboardLogger.log('SUCCESS', `📈 ${result.key}: SUCCESS`, {
                    'endpoint': result.key,
                    'data': result.data,
                    'timestamp': new Date().toISOString()
                });
            } else {
                failedEndpoints.push({
                    endpoint: result.key,
                    error: result.error,
                    fallback_used: true
                });
                dashboardLogger.log('ERROR', `📈 ${result.key}: FAILED`, {
                    'endpoint': result.key,
                    'error': result.error,
                    'fallback_data': result.data,
                    'timestamp': new Date().toISOString()
                });
            }
        });
        
        dashboardLogger.log('SUCCESS', `📈 Dashboard loaded: ${successCount}/${results.length} endpoints successful`, {
            'success_count': successCount,
            'total_endpoints': results.length,
            'success_rate': `${(successCount/results.length*100).toFixed(1)}%`,
            'failed_endpoints': failedEndpoints,
            'dashboard_data_keys': Object.keys(dashboardData),
            'timestamp': new Date().toISOString()
        });
        
        // Update UI components
        dashboardLogger.log('INFO', '🎨 Starting UI component updates', {
            'components_to_update': [
                'updateDashboardOverview',
                'updateGenAIMetrics', 
                'updateAllCharts',
                'updateRecentActivity',
                'updateAIInsights'
            ],
            'timestamp': new Date().toISOString()
        });
        
        updateDashboardOverview();
        updateGenAIMetrics();
        updateAllCharts();
        updateRecentActivity();
        updateAIInsights();
        
        dashboardLogger.log('INFO', '🎨 UI component updates completed, hiding loading state', {
            'timestamp': new Date().toISOString()
        });
        
        hideLoadingState();
        
        if (successCount === apiEndpoints.length) {
            console.log('✅ All dashboard data loaded successfully');
            GenAIDashboard.showSuccess('Dashboard data loaded successfully');
            // Hide retry button if all components loaded successfully
            const retryBtn = document.getElementById('retryBtn');
            if (retryBtn) retryBtn.style.display = 'none';
        } else {
            const failedEndpoints = results.filter(r => !r.success);
            console.log(`⚠️ Dashboard loaded with ${failedEndpoints.length} failed endpoints:`, failedEndpoints.map(r => r.key));
            
            const failedNames = failedEndpoints.map(r => r.key.replace(/([A-Z])/g, ' $1').trim()).join(', ');
            GenAIDashboard.showWarning(`Dashboard loaded with ${failedEndpoints.length} components using fallback data: ${failedNames}`);
            
            // Show retry button if there are failed components
            const retryBtn = document.getElementById('retryBtn');
            if (retryBtn) retryBtn.style.display = 'inline-block';
        }
        
        const executionTime = performance.now() - startTime;
        dashboardLogger.logFunctionExit('loadDashboardData', null, executionTime);
        
    } catch (error) {
        const executionTime = performance.now() - startTime;
        dashboardLogger.logError('loadDashboardData', error, { executionTime });
        console.error('❌ Critical error loading dashboard data:', error);
        hideLoadingState();
        GenAIDashboard.showError('Failed to load dashboard data. Please refresh the page.');
    } finally {
        // Always clear the loading flag
        dashboardData.loading = false;
    }
}

// Initialize all charts
function initializeAllCharts() {
    dashboardLogger.logFunctionEntry('initializeAllCharts', [], {
        'charts_to_initialize': [
            'featuresByFunctionChart',
            'backlogsByFunctionChart', 
            'featuresByPlatformChart',
            'backlogsByPlatformChart',
            'projectStatusChart',
            'resourceUtilizationChart',
            'riskOverviewChart',
            'trendCharts'
        ],
        'timestamp': new Date().toISOString()
    });
    
    const chartInitStartTime = performance.now();
    
    try {
        dashboardLogger.log('INFO', 'Initializing Features by Function Chart', {
            'chart': 'featuresByFunctionChart',
            'timestamp': new Date().toISOString()
        });
        initializeFeaturesByFunctionChart();
        
        dashboardLogger.log('INFO', 'Initializing Backlogs by Function Chart', {
            'chart': 'backlogsByFunctionChart',
            'timestamp': new Date().toISOString()
        });
        initializeBacklogsByFunctionChart();
        
        dashboardLogger.log('INFO', 'Initializing Features by Platform Chart', {
            'chart': 'featuresByPlatformChart',
            'timestamp': new Date().toISOString()
        });
        initializeFeaturesByPlatformChart();
        
        dashboardLogger.log('INFO', 'Initializing Backlogs by Platform Chart', {
            'chart': 'backlogsByPlatformChart',
            'timestamp': new Date().toISOString()
        });
        initializeBacklogsByPlatformChart();
        
        dashboardLogger.log('INFO', 'Initializing Project Status Chart', {
            'chart': 'projectStatusChart',
            'timestamp': new Date().toISOString()
        });
        initializeProjectStatusChart();
        
        dashboardLogger.log('INFO', 'Initializing Resource Utilization Chart', {
            'chart': 'resourceUtilizationChart',
            'timestamp': new Date().toISOString()
        });
        initializeResourceUtilizationChart();
        
        dashboardLogger.log('INFO', 'Initializing Risk Overview Chart', {
            'chart': 'riskOverviewChart',
            'timestamp': new Date().toISOString()
        });
        initializeRiskOverviewChart();
        
        dashboardLogger.log('INFO', 'Initializing Trend Charts', {
            'chart': 'trendCharts',
            'timestamp': new Date().toISOString()
        });
        initializeTrendCharts();
        
        const chartInitEndTime = performance.now();
        const totalInitTime = chartInitEndTime - chartInitStartTime;
        
        dashboardLogger.log('SUCCESS', 'All charts initialized successfully', {
            'total_init_time_ms': totalInitTime,
            'charts_initialized': Object.keys(dashboardCharts).length,
            'timestamp': new Date().toISOString()
        });
        
    } catch (error) {
        dashboardLogger.log('ERROR', 'Error during chart initialization', {
            'error_message': error.message,
            'error_stack': error.stack,
            'timestamp': new Date().toISOString()
        });
    }
    
    dashboardLogger.logFunctionExit('initializeAllCharts', {
        'charts_initialized': Object.keys(dashboardCharts).length,
        'total_init_time_ms': performance.now() - chartInitStartTime
    });
}

// Initialize features by function chart
function initializeFeaturesByFunctionChart() {
    const canvas = document.getElementById('featuresByFunctionChart');
    if (!canvas) {
        console.warn('⚠️ Canvas element featuresByFunctionChart not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (dashboardCharts.featuresByFunction) {
        dashboardCharts.featuresByFunction.destroy();
        dashboardCharts.featuresByFunction = null;
    }
    
    const ctx = canvas.getContext('2d');
    
    dashboardCharts.featuresByFunction = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Completed',
                data: [],
                backgroundColor: '#28a745',
                borderColor: '#1e7e34',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'On Track',
                data: [],
                backgroundColor: '#17a2b8',
                borderColor: '#138496',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'At Risk',
                data: [],
                backgroundColor: '#ffc107',
                borderColor: '#e0a800',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'Off Track',
                data: [],
                backgroundColor: '#dc3545',
                borderColor: '#bd2130',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Active Features by Function & Status',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#dee2e6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y} features`;
                        },
                        afterLabel: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed.y / total) * 100).toFixed(1);
                            return `Percentage: ${percentage}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        precision: 0
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Initialize backlogs by function chart
function initializeBacklogsByFunctionChart() {
    const canvas = document.getElementById('backlogsByFunctionChart');
    if (!canvas) {
        console.warn('⚠️ Canvas element backlogsByFunctionChart not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (dashboardCharts.backlogsByFunction) {
        dashboardCharts.backlogsByFunction.destroy();
        dashboardCharts.backlogsByFunction = null;
    }
    
    const ctx = canvas.getContext('2d');
    
    dashboardCharts.backlogsByFunction = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Completed',
                data: [],
                backgroundColor: '#28a745',
                borderColor: '#1e7e34',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'On Track',
                data: [],
                backgroundColor: '#17a2b8',
                borderColor: '#117a8b',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'At Risk',
                data: [],
                backgroundColor: '#ffc107',
                borderColor: '#e0a800',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'Off Track',
                data: [],
                backgroundColor: '#dc3545',
                borderColor: '#bd2130',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Backlogs by Function & Priority',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#dee2e6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        precision: 0
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Initialize features by platform chart
function initializeFeaturesByPlatformChart() {
    const canvas = document.getElementById('featuresByPlatformChart');
    if (!canvas) {
        console.warn('⚠️ Canvas element featuresByPlatformChart not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (dashboardCharts.featuresByPlatform) {
        dashboardCharts.featuresByPlatform.destroy();
        dashboardCharts.featuresByPlatform = null;
    }
    
    const ctx = canvas.getContext('2d');
    
    dashboardCharts.featuresByPlatform = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Completed',
                data: [],
                backgroundColor: '#28a745',
                borderColor: '#1e7e34',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'On Track',
                data: [],
                backgroundColor: '#17a2b8',
                borderColor: '#138496',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'At Risk',
                data: [],
                backgroundColor: '#ffc107',
                borderColor: '#e0a800',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'Off Track',
                data: [],
                backgroundColor: '#dc3545',
                borderColor: '#bd2130',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Active Features by Platform & Status',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#dee2e6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        precision: 0
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Initialize backlogs by platform chart
function initializeBacklogsByPlatformChart() {
    const canvas = document.getElementById('backlogsByPlatformChart');
    if (!canvas) {
        console.warn('⚠️ Canvas element backlogsByPlatformChart not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (dashboardCharts.backlogsByPlatform) {
        dashboardCharts.backlogsByPlatform.destroy();
        dashboardCharts.backlogsByPlatform = null;
    }
    
    const ctx = canvas.getContext('2d');
    
    dashboardCharts.backlogsByPlatform = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Completed',
                data: [],
                backgroundColor: '#28a745',
                borderColor: '#1e7e34',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'On Track',
                data: [],
                backgroundColor: '#17a2b8',
                borderColor: '#117a8b',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'At Risk',
                data: [],
                backgroundColor: '#ffc107',
                borderColor: '#e0a800',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'Off Track',
                data: [],
                backgroundColor: '#dc3545',
                borderColor: '#bd2130',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Backlogs by Platform & Priority',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#dee2e6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        precision: 0
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Initialize project status chart
function initializeProjectStatusChart() {
    const canvas = document.getElementById('projectStatusChart');
    if (!canvas) {
        console.warn('⚠️ Canvas element projectStatusChart not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (dashboardCharts.projectStatus) {
        dashboardCharts.projectStatus.destroy();
        dashboardCharts.projectStatus = null;
    }
    
    const ctx = canvas.getContext('2d');
    
    dashboardCharts.projectStatus = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Active', 'Completed', 'At Risk', 'Off Track'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: ['#17a2b8', '#28a745', '#ffc107', '#dc3545'],
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Project Status Distribution',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const meta = chart.getDatasetMeta(0);
                                    const style = meta.controller.getStyle(i);
                                    const value = data.datasets[0].data[i];
                                    return {
                                        text: `${label}: ${value}`,
                                        fillStyle: style.backgroundColor,
                                        strokeStyle: style.borderColor,
                                        lineWidth: style.borderWidth,
                                        pointStyle: 'circle',
                                        hidden: isNaN(value) || meta.data[i].hidden,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#dee2e6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Initialize resource utilization chart
function initializeResourceUtilizationChart() {
    const canvas = document.getElementById('resourceUtilizationChart');
    if (!canvas) {
        console.warn('⚠️ Canvas element resourceUtilizationChart not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (dashboardCharts.resourceUtilization) {
        dashboardCharts.resourceUtilization.destroy();
        dashboardCharts.resourceUtilization = null;
    }
    
    const ctx = canvas.getContext('2d');
    
    dashboardCharts.resourceUtilization = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Utilization %',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Resource Utilization Trend',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#dee2e6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `Utilization: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Initialize risk overview chart
function initializeRiskOverviewChart() {
    const canvas = document.getElementById('riskOverviewChart');
    if (!canvas) {
        console.warn('⚠️ Canvas element riskOverviewChart not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (dashboardCharts.riskOverview) {
        dashboardCharts.riskOverview.destroy();
        dashboardCharts.riskOverview = null;
    }
    
    const ctx = canvas.getContext('2d');
    
    dashboardCharts.riskOverview = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Low', 'Medium', 'High', 'Critical'],
            datasets: [{
                label: 'Risks',
                data: [0, 0, 0, 0],
                backgroundColor: ['#28a745', '#ffc107', '#fd7e14', '#dc3545'],
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Risk Distribution',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#dee2e6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.y} risks`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        precision: 0
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Initialize trend charts
function initializeTrendCharts() {
    // Add trend charts for additional analytics
    console.log('📈 Trend charts initialized');
}

// Update dashboard overview
function updateDashboardOverview() {
    dashboardLogger.logFunctionEntry('updateDashboardOverview', [], {
        'has_overview_data': !!dashboardData.overview,
        'overview_data_keys': dashboardData.overview ? Object.keys(dashboardData.overview) : [],
        'timestamp': new Date().toISOString()
    });
    
    dashboardLogger.log('INFO', '🔄 Updating dashboard overview...', {
        'timestamp': new Date().toISOString()
    });
    
    if (!dashboardData.overview) {
        dashboardLogger.log('WARN', '❌ No overview data available', {
            'dashboard_data_keys': Object.keys(dashboardData),
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    const data = dashboardData.overview;
    dashboardLogger.log('INFO', '📊 Overview data received', {
        'overview_data': data,
        'data_keys': Object.keys(data),
        'timestamp': new Date().toISOString()
    });
    
    const currentEl = document.getElementById('current-projects');
    const approvedEl = document.getElementById('approved-projects');
    const backlogEl = document.getElementById('backlog-projects');
    const totalEl = document.getElementById('total-projects');
    
    dashboardLogger.log('INFO', 'Checking DOM elements for overview update', {
        'current_projects_element': !!currentEl,
        'approved_projects_element': !!approvedEl,
        'backlog_projects_element': !!backlogEl,
        'total_projects_element': !!totalEl,
        'timestamp': new Date().toISOString()
    });
    
    try {
        if (currentEl) {
            currentEl.textContent = data.current_projects || 0;
            dashboardLogger.log('SUCCESS', 'Updated current-projects element', {
                'element_id': 'current-projects',
                'value': data.current_projects || 0,
                'timestamp': new Date().toISOString()
            });
        } else {
            dashboardLogger.log('ERROR', 'current-projects element not found', {
                'element_id': 'current-projects',
                'timestamp': new Date().toISOString()
            });
        }
        
        if (approvedEl) {
            approvedEl.textContent = data.approved_projects || 0;
            dashboardLogger.log('SUCCESS', 'Updated approved-projects element', {
                'element_id': 'approved-projects',
                'value': data.approved_projects || 0,
                'timestamp': new Date().toISOString()
            });
        } else {
            dashboardLogger.log('ERROR', 'approved-projects element not found', {
                'element_id': 'approved-projects',
                'timestamp': new Date().toISOString()
            });
        }
        
        if (backlogEl) {
            backlogEl.textContent = data.backlog_projects || 0;
            dashboardLogger.log('SUCCESS', 'Updated backlog-projects element', {
                'element_id': 'backlog-projects',
                'value': data.backlog_projects || 0,
                'timestamp': new Date().toISOString()
            });
        } else {
            dashboardLogger.log('ERROR', 'backlog-projects element not found', {
                'element_id': 'backlog-projects',
                'timestamp': new Date().toISOString()
            });
        }
        
        if (totalEl) {
            totalEl.textContent = data.total_projects || 0;
            dashboardLogger.log('SUCCESS', 'Updated total-projects element', {
                'element_id': 'total-projects',
                'value': data.total_projects || 0,
                'timestamp': new Date().toISOString()
            });
        } else {
            dashboardLogger.log('ERROR', 'total-projects element not found', {
                'element_id': 'total-projects',
                'timestamp': new Date().toISOString()
            });
        }
        
        dashboardLogger.logFunctionExit('updateDashboardOverview', {
            'overview_updated': true,
            'timestamp': new Date().toISOString()
        });
        
    } catch (error) {
        dashboardLogger.log('ERROR', 'Error updating dashboard overview', {
            'error_message': error.message,
            'error_stack': error.stack,
            'overview_data': data,
            'timestamp': new Date().toISOString()
        });
    }
    
    console.log('✅ Dashboard overview updated');
}

// Update GenAI metrics
function updateGenAIMetrics() {
    dashboardLogger.logFunctionEntry('updateGenAIMetrics', [], {
        'has_genai_data': !!dashboardData.genai,
        'genai_data_keys': dashboardData.genai ? Object.keys(dashboardData.genai) : [],
        'timestamp': new Date().toISOString()
    });
    
    dashboardLogger.log('INFO', '🔄 Updating GenAI metrics...', {
        'timestamp': new Date().toISOString()
    });
    
    if (!dashboardData.genai) {
        dashboardLogger.log('WARN', '❌ No GenAI data available', {
            'dashboard_data_keys': Object.keys(dashboardData),
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    const genaiData = dashboardData.genai;
    dashboardLogger.log('INFO', '📊 GenAI data received', {
        'genai_data': genaiData,
        'data_keys': Object.keys(genaiData),
        'active_features_by_function_count': genaiData.active_features_by_function?.length || 0,
        'backlogs_by_function_count': genaiData.backlogs_by_function?.length || 0,
        'active_features_by_platform_count': genaiData.active_features_by_platform?.length || 0,
        'backlogs_by_platform_count': genaiData.backlogs_by_platform?.length || 0,
        'timestamp': new Date().toISOString()
    });
    
    try {
        dashboardLogger.log('INFO', 'Updating features by function chart', {
            'data_count': genaiData.active_features_by_function?.length || 0,
            'timestamp': new Date().toISOString()
        });
        updateFeaturesByFunctionChart(genaiData.active_features_by_function);
        
        dashboardLogger.log('INFO', 'Updating backlogs by function chart', {
            'data_count': genaiData.backlogs_by_function?.length || 0,
            'timestamp': new Date().toISOString()
        });
        updateBacklogsByFunctionChart(genaiData.backlogs_by_function);
        
        dashboardLogger.log('INFO', 'Updating features by platform chart', {
            'data_count': genaiData.active_features_by_platform?.length || 0,
            'timestamp': new Date().toISOString()
        });
        updateFeaturesByPlatformChart(genaiData.active_features_by_platform);
        
        dashboardLogger.log('INFO', 'Updating backlogs by platform chart', {
            'data_count': genaiData.backlogs_by_platform?.length || 0,
            'timestamp': new Date().toISOString()
        });
        updateBacklogsByPlatformChart(genaiData.backlogs_by_platform);
        
        dashboardLogger.log('SUCCESS', '✅ GenAI metrics updated successfully', {
            'charts_updated': 4,
            'timestamp': new Date().toISOString()
        });
        
        dashboardLogger.logFunctionExit('updateGenAIMetrics', {
            'genai_metrics_updated': true,
            'timestamp': new Date().toISOString()
        });
        
    } catch (error) {
        dashboardLogger.log('ERROR', 'Error updating GenAI metrics', {
            'error_message': error.message,
            'error_stack': error.stack,
            'genai_data': genaiData,
            'timestamp': new Date().toISOString()
        });
    }
}

// Update features by function chart
function updateFeaturesByFunctionChart(data) {
    if (!dashboardCharts.featuresByFunction || !data) return;
    
    const labels = data.map(item => item.function_name);
    const completed = data.map(item => item.completed || 0);
    const onTrack = data.map(item => item.on_track || 0);
    const atRisk = data.map(item => item.at_risk || 0);
    const offTrack = data.map(item => item.off_track || 0);
    
    dashboardCharts.featuresByFunction.data.labels = labels;
    dashboardCharts.featuresByFunction.data.datasets[0].data = completed;
    dashboardCharts.featuresByFunction.data.datasets[1].data = onTrack;
    dashboardCharts.featuresByFunction.data.datasets[2].data = atRisk;
    dashboardCharts.featuresByFunction.data.datasets[3].data = offTrack;
    dashboardCharts.featuresByFunction.update('active');
}

// Update backlogs by function chart
function updateBacklogsByFunctionChart(data) {
    if (!dashboardCharts.backlogsByFunction || !data) return;
    
    const labels = data.map(item => item.function_name);
    const completed = data.map(item => item.completed || 0);
    const onTrack = data.map(item => item.on_track || 0);
    const atRisk = data.map(item => item.at_risk || 0);
    const offTrack = data.map(item => item.off_track || 0);
    
    dashboardCharts.backlogsByFunction.data.labels = labels;
    dashboardCharts.backlogsByFunction.data.datasets[0].data = completed;
    dashboardCharts.backlogsByFunction.data.datasets[1].data = onTrack;
    dashboardCharts.backlogsByFunction.data.datasets[2].data = atRisk;
    dashboardCharts.backlogsByFunction.data.datasets[3].data = offTrack;
    dashboardCharts.backlogsByFunction.update('active');
}

// Update features by platform chart
function updateFeaturesByPlatformChart(data) {
    if (!dashboardCharts.featuresByPlatform || !data) return;
    
    const labels = data.map(item => item.platform_name);
    const completed = data.map(item => item.completed || 0);
    const onTrack = data.map(item => item.on_track || 0);
    const atRisk = data.map(item => item.at_risk || 0);
    const offTrack = data.map(item => item.off_track || 0);
    
    dashboardCharts.featuresByPlatform.data.labels = labels;
    dashboardCharts.featuresByPlatform.data.datasets[0].data = completed;
    dashboardCharts.featuresByPlatform.data.datasets[1].data = onTrack;
    dashboardCharts.featuresByPlatform.data.datasets[2].data = atRisk;
    dashboardCharts.featuresByPlatform.data.datasets[3].data = offTrack;
    dashboardCharts.featuresByPlatform.update('active');
}

// Update backlogs by platform chart
function updateBacklogsByPlatformChart(data) {
    if (!dashboardCharts.backlogsByPlatform || !data) return;
    
    const labels = data.map(item => item.platform_name);
    const completed = data.map(item => item.completed || 0);
    const onTrack = data.map(item => item.on_track || 0);
    const atRisk = data.map(item => item.at_risk || 0);
    const offTrack = data.map(item => item.off_track || 0);
    
    dashboardCharts.backlogsByPlatform.data.labels = labels;
    dashboardCharts.backlogsByPlatform.data.datasets[0].data = completed;
    dashboardCharts.backlogsByPlatform.data.datasets[1].data = onTrack;
    dashboardCharts.backlogsByPlatform.data.datasets[2].data = atRisk;
    dashboardCharts.backlogsByPlatform.data.datasets[3].data = offTrack;
    dashboardCharts.backlogsByPlatform.update('active');
}

// Update all charts
function updateAllCharts() {
    dashboardLogger.logFunctionEntry('updateAllCharts', [], {
        'has_project_status_data': !!dashboardData.projectStatus,
        'has_resource_util_data': !!dashboardData.resourceUtil,
        'has_risk_overview_data': !!dashboardData.riskOverview,
        'timestamp': new Date().toISOString()
    });
    
    dashboardLogger.log('INFO', '🔄 Updating all charts...', {
        'timestamp': new Date().toISOString()
    });
    
    let chartsUpdated = 0;
    
    try {
        if (dashboardData.projectStatus) {
            dashboardLogger.log('INFO', 'Updating project status chart', {
                'data_keys': Object.keys(dashboardData.projectStatus),
                'timestamp': new Date().toISOString()
            });
            updateProjectStatusChart(dashboardData.projectStatus);
            chartsUpdated++;
        } else {
            dashboardLogger.log('WARN', 'No project status data available', {
                'timestamp': new Date().toISOString()
            });
        }
        
        if (dashboardData.resourceUtil) {
            dashboardLogger.log('INFO', 'Updating resource utilization chart', {
                'data_type': Array.isArray(dashboardData.resourceUtil) ? 'array' : typeof dashboardData.resourceUtil,
                'data_length': Array.isArray(dashboardData.resourceUtil) ? dashboardData.resourceUtil.length : 'N/A',
                'timestamp': new Date().toISOString()
            });
            updateResourceUtilizationChart(dashboardData.resourceUtil);
            chartsUpdated++;
        } else {
            dashboardLogger.log('WARN', 'No resource utilization data available', {
                'timestamp': new Date().toISOString()
            });
        }
        
        if (dashboardData.riskOverview) {
            dashboardLogger.log('INFO', 'Updating risk overview chart', {
                'data_type': Array.isArray(dashboardData.riskOverview) ? 'array' : typeof dashboardData.riskOverview,
                'data_length': Array.isArray(dashboardData.riskOverview) ? dashboardData.riskOverview.length : 'N/A',
                'timestamp': new Date().toISOString()
            });
            updateRiskOverviewChart(dashboardData.riskOverview);
            chartsUpdated++;
        } else {
            dashboardLogger.log('WARN', 'No risk overview data available', {
                'timestamp': new Date().toISOString()
            });
        }
        
        dashboardLogger.log('SUCCESS', `✅ All charts updated successfully`, {
            'charts_updated': chartsUpdated,
            'total_possible_charts': 3,
            'timestamp': new Date().toISOString()
        });
        
        dashboardLogger.logFunctionExit('updateAllCharts', {
            'charts_updated': chartsUpdated,
            'timestamp': new Date().toISOString()
        });
        
    } catch (error) {
        dashboardLogger.log('ERROR', 'Error updating all charts', {
            'error_message': error.message,
            'error_stack': error.stack,
            'charts_updated': chartsUpdated,
            'timestamp': new Date().toISOString()
        });
    }
}

// Update project status chart
function updateProjectStatusChart(data) {
    if (!dashboardCharts.projectStatus) return;
    
    const statusCounts = {
        'Active': data.active_projects || 0,
        'Completed': data.completed_projects || 0,
        'At Risk': data.at_risk_projects || 0,
        'Off Track': data.off_track_projects || 0
    };
    
    dashboardCharts.projectStatus.data.datasets[0].data = [
        statusCounts.Active,
        statusCounts.Completed,
        statusCounts['At Risk'],
        statusCounts['Off Track']
    ];
    dashboardCharts.projectStatus.update('active');
}

// Update resource utilization chart
function updateResourceUtilizationChart(data) {
    if (!dashboardCharts.resourceUtilization) return;
    
    const labels = data.map(item => item.resource_name);
    const utilization = data.map(item => Math.round(item.utilization_rate || 0));
    
    dashboardCharts.resourceUtilization.data.labels = labels;
    dashboardCharts.resourceUtilization.data.datasets[0].data = utilization;
    dashboardCharts.resourceUtilization.update('active');
}

// Update risk overview chart
function updateRiskOverviewChart(data) {
    if (!dashboardCharts.riskOverview) return;
    
    const riskCounts = {
        'Low': data.filter(r => r.risk_level === 'Low').length,
        'Medium': data.filter(r => r.risk_level === 'Medium').length,
        'High': data.filter(r => r.risk_level === 'High').length,
        'Critical': data.filter(r => r.risk_level === 'Critical').length
    };
    
    dashboardCharts.riskOverview.data.datasets[0].data = [
        riskCounts.Low,
        riskCounts.Medium,
        riskCounts.High,
        riskCounts.Critical
    ];
    dashboardCharts.riskOverview.update('active');
}

// Update recent activity
function updateRecentActivity() {
    dashboardLogger.logFunctionEntry('updateRecentActivity', [], {
        'has_recent_activity_data': !!dashboardData.recentActivity,
        'recent_activity_type': typeof dashboardData.recentActivity,
        'recent_activity_keys': dashboardData.recentActivity ? Object.keys(dashboardData.recentActivity) : [],
        'timestamp': new Date().toISOString()
    });
    
    dashboardLogger.log('INFO', '🔄 Updating recent activity...', {
        'timestamp': new Date().toISOString()
    });
    
    if (!dashboardData.recentActivity) {
        dashboardLogger.log('WARN', '❌ No recent activity data available', {
            'dashboard_data_keys': Object.keys(dashboardData),
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    const container = document.getElementById('recent-activity');
    dashboardLogger.log('INFO', 'Checking recent activity container', {
        'container_found': !!container,
        'container_id': 'recent-activity',
        'timestamp': new Date().toISOString()
    });
    
    if (!container) {
        dashboardLogger.log('ERROR', '❌ Recent activity container not found', {
            'container_id': 'recent-activity',
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    // Handle both array and object formats
    let activities = [];
    if (Array.isArray(dashboardData.recentActivity)) {
        activities = dashboardData.recentActivity.slice(0, 10);
    } else if (dashboardData.recentActivity.activities && Array.isArray(dashboardData.recentActivity.activities)) {
        activities = dashboardData.recentActivity.activities.slice(0, 10);
    } else {
        // Convert object to array format for display
        activities = [{
            title: "Project Summary",
            description: `Total Projects: ${dashboardData.recentActivity.total_projects || 0}, Active: ${dashboardData.recentActivity.active_projects || 0}`,
            timestamp: "Just now"
        }];
    }
    
    if (activities.length === 0) {
        container.innerHTML = '<p class="text-muted">No recent activity</p>';
        return;
    }
    
    const html = activities.map(activity => `
        <div class="d-flex align-items-start mb-3">
            <div class="flex-shrink-0">
                <i class="fas fa-circle text-primary" style="font-size: 8px;"></i>
            </div>
            <div class="flex-grow-1 ms-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1 small">${activity.title || 'Activity'}</h6>
                        <p class="mb-1 small text-muted">${activity.description || 'No description'}</p>
                    </div>
                    <small class="text-muted">${activity.timestamp || 'Just now'}</small>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Update AI insights
function updateAIInsights() {
    dashboardLogger.logFunctionEntry('updateAIInsights', [], {
        'has_ai_insights_data': !!dashboardData.aiInsights,
        'ai_insights_type': typeof dashboardData.aiInsights,
        'ai_insights_keys': dashboardData.aiInsights ? Object.keys(dashboardData.aiInsights) : [],
        'timestamp': new Date().toISOString()
    });
    
    dashboardLogger.log('INFO', '🔄 Updating AI insights...', {
        'timestamp': new Date().toISOString()
    });
    
    if (!dashboardData.aiInsights) {
        dashboardLogger.log('WARN', '❌ No AI insights data available', {
            'dashboard_data_keys': Object.keys(dashboardData),
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    const container = document.getElementById('ai-insights');
    dashboardLogger.log('INFO', 'Checking AI insights container', {
        'container_found': !!container,
        'container_id': 'ai-insights',
        'timestamp': new Date().toISOString()
    });
    
    if (!container) {
        dashboardLogger.log('ERROR', '❌ AI insights container not found', {
            'container_id': 'ai-insights',
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    const insights = dashboardData.aiInsights.insights || [];
    dashboardLogger.log('INFO', 'Processing AI insights data', {
        'insights_count': insights.length,
        'insights_data': insights,
        'timestamp': new Date().toISOString()
    });
    
    if (insights.length === 0) {
        dashboardLogger.log('WARN', 'No AI insights available, showing placeholder', {
            'timestamp': new Date().toISOString()
        });
        container.innerHTML = '<p class="text-muted">No AI insights available</p>';
        return;
    }
    
    const html = insights.slice(0, 5).map(insight => `
        <div class="alert alert-${getInsightAlertClass(insight.type)} alert-sm">
            <h6 class="alert-heading">${insight.title || 'AI Insight'}</h6>
            <p class="mb-0 small">${insight.description || 'No description available'}</p>
            <small class="text-muted">Confidence: ${Math.round((insight.confidence || 0.8) * 100)}%</small>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Find element with multiple selectors and retries
function findElementWithRetry(elementName, selectors, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                dashboardLogger.log('SUCCESS', `Found ${elementName} element`, {
                    'selector': selector,
                    'attempt': attempt,
                    'element_tag': element.tagName,
                    'timestamp': new Date().toISOString()
                });
                return element;
            }
        }
        
        if (attempt < maxRetries) {
            dashboardLogger.log('WARN', `Retrying ${elementName} element search`, {
                'attempt': attempt,
                'max_retries': maxRetries,
                'selectors_tried': selectors,
                'timestamp': new Date().toISOString()
            });
            // Wait 50ms before retry
            const start = performance.now();
            while (performance.now() - start < 50) {
                // Busy wait
            }
        }
    }
    
    dashboardLogger.log('ERROR', `Could not find ${elementName} element after ${maxRetries} attempts`, {
        'selectors_tried': selectors,
        'available_elements': Array.from(document.querySelectorAll('*')).slice(0, 10).map(el => ({
            id: el.id,
            className: el.className,
            tagName: el.tagName
        })),
        'timestamp': new Date().toISOString()
    });
    
    return null;
}

// Get insight alert class
function getInsightAlertClass(type) {
    const typeMap = {
        'anomaly': 'warning',
        'trend': 'info',
        'recommendation': 'success',
        'alert': 'danger'
    };
    return typeMap[type] || 'info';
}

// Setup event listeners
function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
    if (refreshBtn && !refreshBtn.hasAttribute('data-listener-attached')) {
        refreshBtn.addEventListener('click', refreshDashboard);
        refreshBtn.setAttribute('data-listener-attached', 'true');
    }
    
    // Export button
    const exportBtn = document.querySelector('[onclick="exportDashboard()"]');
    if (exportBtn && !exportBtn.hasAttribute('data-listener-attached')) {
        exportBtn.addEventListener('click', exportDashboard);
        exportBtn.setAttribute('data-listener-attached', 'true');
    }
    
    // Customize button
    const customizeBtn = document.querySelector('[onclick="customizeDashboard()"]');
    if (customizeBtn && !customizeBtn.hasAttribute('data-listener-attached')) {
        customizeBtn.addEventListener('click', customizeDashboard);
        customizeBtn.setAttribute('data-listener-attached', 'true');
    }
    
    // Real-time toggle
    const realTimeToggle = document.getElementById('realTimeToggle');
    if (realTimeToggle && !realTimeToggle.hasAttribute('data-listener-attached')) {
        realTimeToggle.addEventListener('change', toggleRealTime);
        realTimeToggle.setAttribute('data-listener-attached', 'true');
    }
}

// Setup dashboard interactions
function setupDashboardInteractions() {
    // Chart click handlers
    Object.values(dashboardCharts).forEach(chart => {
        if (chart && chart.canvas) {
            chart.canvas.addEventListener('click', handleChartClick);
        }
    });
    
    // Dashboard customization
    setupDashboardCustomization();
}

// Handle chart clicks
function handleChartClick(event) {
    const chart = event.target.chart;
    const activePoints = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
    
    if (activePoints.length > 0) {
        const dataIndex = activePoints[0].index;
        const datasetIndex = activePoints[0].datasetIndex;
        const data = chart.data;
        
        // Handle drill-down based on chart type
        if (chart.id === 'featuresByFunctionChart') {
            drillDownToFeatures(data.labels[dataIndex], data.datasets[datasetIndex].label);
        } else if (chart.id === 'backlogsByFunctionChart') {
            drillDownToBacklogs(data.labels[dataIndex], data.datasets[datasetIndex].label);
        }
    }
}

// Drill down to features
function drillDownToFeatures(functionName, status) {
    console.log(`Drilling down to features: ${functionName} - ${status}`);
    // Implement drill-down functionality
    GenAIDashboard.showInfo(`Viewing ${status} features for ${functionName}`);
}

// Drill down to backlogs
function drillDownToBacklogs(functionName, priority) {
    console.log(`Drilling down to backlogs: ${functionName} - ${priority}`);
    // Implement drill-down functionality
    GenAIDashboard.showInfo(`Viewing ${priority} priority backlogs for ${functionName}`);
}

// Setup real-time updates - DISABLED BY DEFAULT
function setupRealTimeUpdates() {
    // Safety check to prevent initialization errors
    if (typeof isRealTimeEnabled === 'undefined') {
        isRealTimeEnabled = false; // DISABLED BY DEFAULT
    }
    
    // Clear ALL existing intervals to prevent conflicts
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    
    // Clear global dashboard interval
    if (window.dashboardRefreshInterval) {
        clearInterval(window.dashboardRefreshInterval);
        window.dashboardRefreshInterval = null;
    }
    
    // Clear state manager interval
    if (window.stateManager?.syncInterval) {
        clearInterval(window.stateManager.syncInterval);
        window.stateManager.syncInterval = null;
    }
    
    // Clear sync manager interval
    if (window.syncManager?.syncInterval) {
        clearInterval(window.syncManager.syncInterval);
        window.syncManager.syncInterval = null;
    }
    
    // DISABLED BY DEFAULT - Only enable if explicitly requested
    if (isRealTimeEnabled) {
        refreshInterval = setInterval(() => {
            dashboardLogger.log('INFO', '🔄 Real-time refresh triggered', {
                'interval_id': refreshInterval,
                'timestamp': new Date().toISOString()
            });
            loadDashboardData();
        }, 30000); // Refresh every 30 seconds
        
        // Store globally to prevent conflicts
        window.dashboardRefreshInterval = refreshInterval;
        
        dashboardLogger.log('SUCCESS', '✅ Real-time updates enabled', {
            'interval_id': refreshInterval,
            'refresh_interval_ms': 30000,
            'timestamp': new Date().toISOString()
        });
    } else {
        console.log('⏸️ Real-time updates disabled by default - manual loading only');
    }
}

// Toggle real-time updates
function toggleRealTime(event) {
    isRealTimeEnabled = event.target.checked;
    
    if (isRealTimeEnabled) {
        setupRealTimeUpdates();
        GenAIDashboard.showSuccess('Real-time updates enabled');
    } else {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
        GenAIDashboard.showInfo('Real-time updates disabled');
    }
}

// Setup dashboard customization
function setupDashboardCustomization() {
    // Add customization controls
    const customizePanel = document.getElementById('customizePanel');
    if (customizePanel) {
        customizePanel.style.display = 'none';
    }
}

// Refresh dashboard
function refreshDashboard() {
    // Prevent multiple simultaneous refreshes
    if (dashboardData.refreshing) {
        dashboardLogger.log('WARN', '⏸️ Refresh already in progress, skipping', {
            'timestamp': new Date().toISOString()
        });
        return;
    }
    
    dashboardData.refreshing = true;
    dashboardLogger.log('INFO', '🔄 Manual refresh triggered', {
        'call_count': loadDashboardDataCallCount,
        'timestamp': new Date().toISOString()
    });
    
    console.log('🔄 Refreshing dashboard...');
    loadDashboardData().finally(() => {
        dashboardData.refreshing = false;
    });
}

// Retry failed components
function retryFailedComponents() {
    console.log('🔄 Retrying failed components...');
    showLoadingState();
    
    // Find failed components and retry them
    const failedComponents = Object.keys(dashboardData).filter(key => {
        const data = dashboardData[key];
        return Array.isArray(data) ? data.length === 0 : 
               typeof data === 'object' && data !== null ? Object.keys(data).length === 0 : false;
    });
    
    if (failedComponents.length === 0) {
        hideLoadingState();
        GenAIDashboard.showInfo('No failed components to retry');
        return;
    }
    
    // Retry failed components
    const retryPromises = failedComponents.map(async (component) => {
        const endpointMap = {
            'overview': '/dashboards/all-projects',
            'genai': '/dashboards/genai-metrics',
            'projectStatus': '/dashboards/summary-metrics',
            'resourceUtil': '/resources/analytics/workload',
            'riskOverview': '/reports/risks',
            'recentActivity': '/reports/executive-summary',
            'aiInsights': '/ai/insights'
        };
        
        try {
            const data = await GenAIDashboard.apiCall(endpointMap[component], 'GET', null, 2);
            dashboardData[component] = data;
            return { component, success: true };
        } catch (error) {
            console.warn(`⚠️ Retry failed for ${component}:`, error.message);
            return { component, success: false };
        }
    });
    
    Promise.all(retryPromises).then(results => {
        const successCount = results.filter(r => r.success).length;
        hideLoadingState();
        
        if (successCount > 0) {
            // Update UI with retried data
            updateDashboardOverview();
            updateGenAIMetrics();
            updateAllCharts();
            updateRecentActivity();
            updateAIInsights();
            
            GenAIDashboard.showSuccess(`Successfully retried ${successCount} components`);
            
            // Check if all components are now working
            const allComponentsWorking = Object.keys(dashboardData).every(key => {
                const data = dashboardData[key];
                return Array.isArray(data) ? data.length > 0 : 
                       typeof data === 'object' && data !== null ? Object.keys(data).length > 0 : true;
            });
            
            // Hide retry button if all components are now working
            if (allComponentsWorking) {
                const retryBtn = document.getElementById('retryBtn');
                if (retryBtn) retryBtn.style.display = 'none';
            }
        } else {
            GenAIDashboard.showError('Failed to retry components. Please check your connection.');
        }
    });
}

// Export dashboard
function exportDashboard() {
    console.log('📊 Exporting dashboard...');
    
    // Create export options modal
    const exportModal = document.createElement('div');
    exportModal.className = 'modal fade';
    exportModal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Export Dashboard</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Export Format</label>
                        <select class="form-select" id="exportFormat">
                            <option value="pdf">PDF Report</option>
                            <option value="excel">Excel Spreadsheet</option>
                            <option value="csv">CSV Data</option>
                            <option value="image">PNG Image</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Include Charts</label>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="includeCharts" checked>
                            <label class="form-check-label" for="includeCharts">
                                Include all charts
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="performExport()">Export</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(exportModal);
    const modal = new bootstrap.Modal(exportModal);
    modal.show();
    
    // Clean up modal after hiding
    exportModal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(exportModal);
    });
}

// Perform export
function performExport() {
    const format = document.getElementById('exportFormat').value;
    const includeCharts = document.getElementById('includeCharts').checked;
    
    console.log(`Exporting dashboard as ${format}, include charts: ${includeCharts}`);
    
    // Implement export functionality based on format
    switch (format) {
        case 'pdf':
            exportToPDF(includeCharts);
            break;
        case 'excel':
            exportToExcel(includeCharts);
            break;
        case 'csv':
            exportToCSV();
            break;
        case 'image':
            exportToImage(includeCharts);
            break;
    }
    
    GenAIDashboard.showSuccess(`Dashboard exported as ${format.toUpperCase()}`);
}

// Export to PDF
function exportToPDF(includeCharts) {
    // Implement PDF export
    console.log('Exporting to PDF...');
}

// Export to Excel
function exportToExcel(includeCharts) {
    // Implement Excel export
    console.log('Exporting to Excel...');
}

// Export to CSV
function exportToCSV() {
    // Implement CSV export
    console.log('Exporting to CSV...');
}

// Export to Image
function exportToImage(includeCharts) {
    // Implement image export
    console.log('Exporting to Image...');
}

// Customize dashboard
function customizeDashboard() {
    console.log('🎨 Customizing dashboard...');
    
    // Toggle customization panel
    const customizePanel = document.getElementById('customizePanel');
    if (customizePanel) {
        customizePanel.style.display = customizePanel.style.display === 'none' ? 'block' : 'none';
    }
    
    GenAIDashboard.showInfo('Dashboard customization panel opened');
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// Show loading state
function showLoadingState() {
    dashboardLogger.logFunctionEntry('showLoadingState', [], {
        'timestamp': new Date().toISOString()
    });
    
    // Wait for DOM to be ready if needed
    if (document.readyState === 'loading') {
        dashboardLogger.log('INFO', 'DOM still loading, waiting for DOMContentLoaded', {
            'ready_state': document.readyState,
            'timestamp': new Date().toISOString()
        });
        // Note: DOMContentLoaded listener is already set up at the top of the file
        // Just wait a bit and retry
        setTimeout(showLoadingState, 100);
        return;
    }
    
    // Try multiple ways to find the loading overlay with retries
    let loadingOverlay = findElementWithRetry('loading-overlay', ['#loading-overlay', '.loading-overlay', '[id*="loading"]']);
    
    dashboardLogger.log('INFO', 'Showing loading state', {
        'loading_overlay_found': !!loadingOverlay,
        'loading_overlay_element': loadingOverlay ? loadingOverlay.tagName : 'not found',
        'timestamp': new Date().toISOString()
    });
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
        dashboardLogger.log('SUCCESS', 'Loading overlay displayed', {
            'element_id': 'loading-overlay',
            'display_style': 'flex',
            'timestamp': new Date().toISOString()
        });
    } else {
        dashboardLogger.log('ERROR', 'Loading overlay element not found', {
            'element_id': 'loading-overlay',
            'available_elements': Array.from(document.querySelectorAll('[id*="loading"], [class*="loading"]')).map(el => ({
                id: el.id,
                className: el.className,
                tagName: el.tagName
            })),
            'timestamp': new Date().toISOString()
        });
    }
    
    // Try multiple ways to find the refresh button with retries
    let refreshBtn = findElementWithRetry('refresh button', [
        '[onclick="refreshDashboard()"]',
        'button[onclick*="refreshDashboard"]',
        '.btn[onclick*="refresh"]',
        'button[onclick*="refresh"]'
    ]);
    
    dashboardLogger.log('INFO', 'Updating refresh button for loading state', {
        'refresh_button_found': !!refreshBtn,
        'refresh_button_element': refreshBtn ? refreshBtn.tagName : 'not found',
        'timestamp': new Date().toISOString()
    });
    
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        dashboardLogger.log('SUCCESS', 'Refresh button disabled and updated', {
            'button_disabled': true,
            'button_text': 'Loading...',
            'timestamp': new Date().toISOString()
        });
    } else {
        dashboardLogger.log('ERROR', 'Refresh button not found', {
            'selector': '[onclick="refreshDashboard()"]',
            'available_buttons': Array.from(document.querySelectorAll('button')).map(btn => ({
                id: btn.id,
                className: btn.className,
                onclick: btn.onclick ? btn.onclick.toString() : 'none',
                textContent: btn.textContent?.trim()
            })),
            'timestamp': new Date().toISOString()
        });
    }
    
    dashboardLogger.logFunctionExit('showLoadingState', {
        'loading_state_shown': true,
        'timestamp': new Date().toISOString()
    });
}

// Hide loading state
function hideLoadingState() {
    dashboardLogger.logFunctionEntry('hideLoadingState', [], {
        'timestamp': new Date().toISOString()
    });
    
    dashboardLogger.log('INFO', '🔄 Hiding loading state...', {
        'timestamp': new Date().toISOString()
    });
    
    const loadingOverlay = findElementWithRetry('loading overlay', ['#loading-overlay', '.loading-overlay', '[id*="loading"]']);
    dashboardLogger.log('INFO', 'Checking loading overlay element', {
        'loading_overlay_found': !!loadingOverlay,
        'timestamp': new Date().toISOString()
    });
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
        dashboardLogger.log('SUCCESS', '✅ Loading overlay hidden', {
            'element_id': 'loading-overlay',
            'display_style': 'none',
            'timestamp': new Date().toISOString()
        });
    } else {
        dashboardLogger.log('ERROR', '❌ Loading overlay element not found', {
            'element_id': 'loading-overlay',
            'timestamp': new Date().toISOString()
        });
    }
    
    // Re-enable refresh button
    const refreshBtn = findElementWithRetry('refresh button', [
        '[onclick="refreshDashboard()"]',
        'button[onclick*="refreshDashboard"]',
        '.btn[onclick*="refresh"]',
        'button[onclick*="refresh"]'
    ]);
    dashboardLogger.log('INFO', 'Re-enabling refresh button', {
        'refresh_button_found': !!refreshBtn,
        'timestamp': new Date().toISOString()
    });
    
    if (refreshBtn) {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Refresh';
        dashboardLogger.log('SUCCESS', '✅ Refresh button re-enabled', {
            'button_disabled': false,
            'button_text': 'Refresh',
            'timestamp': new Date().toISOString()
        });
    } else {
        dashboardLogger.log('ERROR', '❌ Refresh button not found', {
            'selector': '[onclick="refreshDashboard()"]',
            'timestamp': new Date().toISOString()
        });
    }
    
    dashboardLogger.logFunctionExit('hideLoadingState', {
        'loading_state_hidden': true,
        'timestamp': new Date().toISOString()
    });
}

// Manual dashboard loading function
function loadDashboardManually() {
    console.log('🚀 Manual dashboard loading triggered');
    
    // Check if already initialized
    if (window.dashboardInitialized) {
        console.log('⏸️ Dashboard already initialized, refreshing data instead');
        refreshDashboard();
        return;
    }
    
    try {
        console.log('🚀 Starting manual dashboard initialization');
        window.dashboardInitialized = true; // Set immediately
        initializeDashboard();
        setupRealTimeUpdates();
        console.log('✅ Manual dashboard initialization completed');
    } catch (error) {
        console.error('❌ Manual dashboard initialization failed:', error);
        window.dashboardInitialized = false; // Reset on error
    }
}

// Export functions for global use
window.DashboardManager = {
    refreshDashboard,
    retryFailedComponents,
    exportDashboard,
    customizeDashboard,
    toggleRealTime,
    loadDashboardData,
    updateAllCharts,
    showLoadingState,
    hideLoadingState,
    loadDashboardManually
};

// Make loadDashboardManually globally available
window.loadDashboardManually = loadDashboardManually;
