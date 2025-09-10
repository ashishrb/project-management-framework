// GenAI Metrics Dashboard - Advanced Dashboard JavaScript

// Global dashboard variables
let dashboardCharts = {};
let dashboardData = {};
let refreshInterval = null;

// Dashboard logger is initialized in logging.js
var isRealTimeEnabled = true; // Use var to avoid temporal dead zone issues

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupRealTimeUpdates();
    setupDashboardCustomization();
});

// Initialize dashboard
function initializeDashboard() {
    console.log('🚀 Initializing GenAI Metrics Dashboard...');
    console.log('🔍 GenAIDashboard object available:', typeof GenAIDashboard);
    console.log('🔍 GenAIDashboard.apiCall available:', typeof GenAIDashboard?.apiCall);
    
    // Load initial data
    console.log('📊 Starting loadDashboardData...');
    loadDashboardData();
    
    // Initialize all charts
    console.log('📈 Starting initializeAllCharts...');
    initializeAllCharts();
    
    // Setup event listeners
    console.log('🎧 Setting up event listeners...');
    setupEventListeners();
    
    // Setup dashboard interactions
    console.log('⚙️ Setting up dashboard interactions...');
    setupDashboardInteractions();
    
    console.log('✅ Dashboard initialized successfully');
}

// Load dashboard data with improved error handling
async function loadDashboardData() {
    dashboardLogger.logFunctionEntry('loadDashboardData');
    const startTime = performance.now();
    
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
            { key: 'aiInsights', url: '/ai/insights', fallback: { insights: [] } }
        ];
        
        // Load data with individual error handling and retry logic
        const loadPromises = apiEndpoints.map(async (endpoint) => {
            try {
                console.log(`🔄 Calling API: ${endpoint.url}`);
                console.log(`🔍 GenAIDashboard.apiCall available:`, typeof GenAIDashboard.apiCall);
                
                const data = await GenAIDashboard.apiCall(endpoint.url, 'GET', null, 2); // 2 retries
                console.log(`✅ API call successful for ${endpoint.key}:`, data);
                return { key: endpoint.key, data, success: true };
            } catch (error) {
                console.warn(`⚠️ Failed to load ${endpoint.key}:`, error.message);
                console.error(`❌ Full error for ${endpoint.key}:`, error);
                return { key: endpoint.key, data: endpoint.fallback, success: false, error: error.message };
            }
        });
        
        const results = await Promise.all(loadPromises);
        
        console.log('📊 Dashboard API results:', results);
        
        // Build dashboard data object
        dashboardData = {};
        let successCount = 0;
        
        results.forEach(result => {
            dashboardData[result.key] = result.data;
            if (result.success) successCount++;
            console.log(`📈 ${result.key}:`, result.success ? 'SUCCESS' : 'FAILED', result.data);
        });
        
        // Update UI components
        updateDashboardOverview();
        updateGenAIMetrics();
        updateAllCharts();
        updateRecentActivity();
        updateAIInsights();
        
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
        
        } catch (error) {
            const executionTime = performance.now() - startTime;
            dashboardLogger.logError('loadDashboardData', error, { executionTime });
            console.error('❌ Critical error loading dashboard data:', error);
            hideLoadingState();
            GenAIDashboard.showError('Failed to load dashboard data. Please refresh the page.');
        }
        
        const executionTime = performance.now() - startTime;
        dashboardLogger.logFunctionExit('loadDashboardData', null, executionTime);
}

// Initialize all charts
function initializeAllCharts() {
    initializeFeaturesByFunctionChart();
    initializeBacklogsByFunctionChart();
    initializeFeaturesByPlatformChart();
    initializeBacklogsByPlatformChart();
    initializeProjectStatusChart();
    initializeResourceUtilizationChart();
    initializeRiskOverviewChart();
    initializeTrendCharts();
}

// Initialize features by function chart
function initializeFeaturesByFunctionChart() {
    const ctx = document.getElementById('featuresByFunctionChart').getContext('2d');
    
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
    const ctx = document.getElementById('backlogsByFunctionChart').getContext('2d');
    
    dashboardCharts.backlogsByFunction = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Highest Priority',
                data: [],
                backgroundColor: '#dc3545',
                borderColor: '#bd2130',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'High Priority',
                data: [],
                backgroundColor: '#fd7e14',
                borderColor: '#e55a00',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'Medium Priority',
                data: [],
                backgroundColor: '#ffc107',
                borderColor: '#e0a800',
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
    const ctx = document.getElementById('featuresByPlatformChart').getContext('2d');
    
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
    const ctx = document.getElementById('backlogsByPlatformChart').getContext('2d');
    
    dashboardCharts.backlogsByPlatform = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Highest Priority',
                data: [],
                backgroundColor: '#dc3545',
                borderColor: '#bd2130',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'High Priority',
                data: [],
                backgroundColor: '#fd7e14',
                borderColor: '#e55a00',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: 'Medium Priority',
                data: [],
                backgroundColor: '#ffc107',
                borderColor: '#e0a800',
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
    const ctx = document.getElementById('projectStatusChart').getContext('2d');
    
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
    const ctx = document.getElementById('resourceUtilizationChart').getContext('2d');
    
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
    const ctx = document.getElementById('riskOverviewChart').getContext('2d');
    
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
    console.log('🔄 Updating dashboard overview...');
    if (!dashboardData.overview) {
        console.log('❌ No overview data available');
        return;
    }
    
    const data = dashboardData.overview;
    console.log('📊 Overview data:', data);
    
    const currentEl = document.getElementById('current-projects');
    const approvedEl = document.getElementById('approved-projects');
    const backlogEl = document.getElementById('backlog-projects');
    const totalEl = document.getElementById('total-projects');
    
    if (currentEl) currentEl.textContent = data.current_projects || 0;
    if (approvedEl) approvedEl.textContent = data.approved_projects || 0;
    if (backlogEl) backlogEl.textContent = data.backlog_projects || 0;
    if (totalEl) totalEl.textContent = data.total_projects || 0;
    
    console.log('✅ Dashboard overview updated');
}

// Update GenAI metrics
function updateGenAIMetrics() {
    if (!dashboardData.genai) return;
    
    updateFeaturesByFunctionChart(dashboardData.genai.active_features_by_function);
    updateBacklogsByFunctionChart(dashboardData.genai.backlogs_by_function);
    updateFeaturesByPlatformChart(dashboardData.genai.active_features_by_platform);
    updateBacklogsByPlatformChart(dashboardData.genai.backlogs_by_platform);
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
    const highest = data.map(item => item.highest_priority || 0);
    const high = data.map(item => item.high_priority || 0);
    const medium = data.map(item => item.medium_priority || 0);
    
    dashboardCharts.backlogsByFunction.data.labels = labels;
    dashboardCharts.backlogsByFunction.data.datasets[0].data = highest;
    dashboardCharts.backlogsByFunction.data.datasets[1].data = high;
    dashboardCharts.backlogsByFunction.data.datasets[2].data = medium;
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
    const highest = data.map(item => item.highest_priority || 0);
    const high = data.map(item => item.high_priority || 0);
    const medium = data.map(item => item.medium_priority || 0);
    
    dashboardCharts.backlogsByPlatform.data.labels = labels;
    dashboardCharts.backlogsByPlatform.data.datasets[0].data = highest;
    dashboardCharts.backlogsByPlatform.data.datasets[1].data = high;
    dashboardCharts.backlogsByPlatform.data.datasets[2].data = medium;
    dashboardCharts.backlogsByPlatform.update('active');
}

// Update all charts
function updateAllCharts() {
    if (dashboardData.projectStatus) {
        updateProjectStatusChart(dashboardData.projectStatus);
    }
    if (dashboardData.resourceUtil) {
        updateResourceUtilizationChart(dashboardData.resourceUtil);
    }
    if (dashboardData.riskOverview) {
        updateRiskOverviewChart(dashboardData.riskOverview);
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
    if (!dashboardData.recentActivity) return;
    
    const container = document.getElementById('recent-activity');
    if (!container) return;
    
    const activities = dashboardData.recentActivity.slice(0, 10);
    
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
    if (!dashboardData.aiInsights) return;
    
    const container = document.getElementById('ai-insights');
    if (!container) return;
    
    const insights = dashboardData.aiInsights.insights || [];
    
    if (insights.length === 0) {
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
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDashboard);
    }
    
    // Export button
    const exportBtn = document.querySelector('[onclick="exportDashboard()"]');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportDashboard);
    }
    
    // Customize button
    const customizeBtn = document.querySelector('[onclick="customizeDashboard()"]');
    if (customizeBtn) {
        customizeBtn.addEventListener('click', customizeDashboard);
    }
    
    // Real-time toggle
    const realTimeToggle = document.getElementById('realTimeToggle');
    if (realTimeToggle) {
        realTimeToggle.addEventListener('change', toggleRealTime);
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

// Setup real-time updates
function setupRealTimeUpdates() {
    // Safety check to prevent initialization errors
    if (typeof isRealTimeEnabled === 'undefined') {
        isRealTimeEnabled = true;
    }
    
    if (isRealTimeEnabled) {
        refreshInterval = setInterval(() => {
            loadDashboardData();
        }, 30000); // Refresh every 30 seconds
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
    console.log('🔄 Refreshing dashboard...');
    loadDashboardData();
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
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
    
    // Disable refresh button during loading
    const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    }
}

// Hide loading state
function hideLoadingState() {
    console.log('🔄 Hiding loading state...');
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
        console.log('✅ Loading overlay hidden');
    } else {
        console.log('❌ Loading overlay element not found');
    }
    
    // Re-enable refresh button
    const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
    if (refreshBtn) {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Refresh';
        console.log('✅ Refresh button re-enabled');
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
    hideLoadingState
};
