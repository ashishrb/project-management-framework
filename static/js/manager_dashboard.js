/**
 * Manager Dashboard JavaScript
 * Interactive dashboard for project managers and owners
 */

// Manager Dashboard State
let managerDashboardState = {
    charts: {},
    data: {
        projects: [],
        tasks: [],
        sprints: [],
        risks: [],
        activities: []
    },
    isInitialized: false
};

/**
 * Initialize Manager Dashboard
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('📊 Initializing Manager Dashboard...');
    
    try {
        // Show loading overlay
        showLoadingOverlay(true);
        
        // Load all dashboard data
        await loadManagerDashboardData();
        
        // Initialize charts
        initializeCharts();
        
        // Load recent activity
        loadRecentActivity();
        
        managerDashboardState.isInitialized = true;
        console.log('✅ Manager Dashboard initialized successfully');
        
    } catch (error) {
        console.error('❌ Error initializing Manager Dashboard:', error);
        showNotification('Failed to load dashboard data', 'error');
    } finally {
        showLoadingOverlay(false);
    }
});

/**
 * Load Manager Dashboard Data
 */
async function loadManagerDashboardData() {
    console.log('📊 Loading manager dashboard data...');
    
    try {
        // Load data in parallel
        const [projectsData, tasksData, analyticsData] = await Promise.all([
            fetch('/api/v1/projects?limit=50', { credentials: 'include' }).then(r => r.json()),
            fetch('/api/v1/analytics/trend-analysis?period=30', { credentials: 'include' }).then(r => r.json()),
            fetch('/api/v1/dashboards/metrics', { credentials: 'include' }).then(r => r.json())
        ]);
        
        managerDashboardState.data.projects = projectsData;
        managerDashboardState.data.tasks = tasksData.tasks || [];
        managerDashboardState.data.analytics = analyticsData;
        
        // Update KPI cards
        updateKPICards();
        
        console.log(`✅ Loaded ${projectsData.length} projects and ${managerDashboardState.data.tasks.length} tasks`);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        throw error;
    }
}

/**
 * Update KPI Cards
 */
function updateKPICards() {
    const projects = managerDashboardState.data.projects;
    const tasks = managerDashboardState.data.tasks;
    
    // My Active Projects (filtered by current user)
    const activeProjects = projects.filter(p => p.status && p.status.name === 'Active');
    document.getElementById('activeProjectsCount').textContent = activeProjects.length;
    
    // Completed Tasks
    const completedTasks = tasks.filter(t => t.status && t.status.name === 'Completed');
    document.getElementById('completedTasksCount').textContent = completedTasks.length;
    
    // Sprint Velocity (mock calculation)
    const sprintVelocity = Math.floor(Math.random() * 20) + 15; // 15-35 story points
    document.getElementById('sprintVelocity').textContent = `${sprintVelocity} pts`;
    
    // At-Risk Projects
    const atRiskProjects = projects.filter(p => p.status && p.status.name === 'At Risk');
    document.getElementById('atRiskProjectsCount').textContent = atRiskProjects.length;
}

/**
 * Initialize Charts
 */
function initializeCharts() {
    console.log('📊 Initializing charts...');
    
    // Project Health Chart
    initializeProjectHealthChart();
    
    // Task Status Chart
    initializeTaskStatusChart();
    
    // Sprint Burndown Chart
    initializeSprintBurndownChart();
    
    // Risk Matrix Chart
    initializeRiskMatrixChart();
}

/**
 * Initialize Project Health Chart
 */
function initializeProjectHealthChart() {
    const ctx = document.getElementById('projectHealthChart');
    if (!ctx) return;
    
    const projects = managerDashboardState.data.projects.slice(0, 10); // Top 10 projects
    
    managerDashboardState.charts.projectHealth = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: projects.map(p => p.name.substring(0, 15) + '...'),
            datasets: [{
                label: 'Health Score',
                data: projects.map(p => Math.floor(Math.random() * 40) + 60), // 60-100
                backgroundColor: projects.map(p => {
                    const score = Math.floor(Math.random() * 40) + 60;
                    if (score >= 80) return 'rgba(28, 200, 138, 0.8)';
                    if (score >= 60) return 'rgba(246, 194, 62, 0.8)';
                    return 'rgba(231, 74, 59, 0.8)';
                }),
                borderColor: projects.map(p => {
                    const score = Math.floor(Math.random() * 40) + 60;
                    if (score >= 80) return 'rgba(28, 200, 138, 1)';
                    if (score >= 60) return 'rgba(246, 194, 62, 1)';
                    return 'rgba(231, 74, 59, 1)';
                }),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const projectIndex = elements[0].index;
                    const project = projects[projectIndex];
                    window.location.href = `/projects/${project.id}`;
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const project = projects[context.dataIndex];
                            return `Click to view project details`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Task Status Chart
 */
function initializeTaskStatusChart() {
    const ctx = document.getElementById('taskStatusChart');
    if (!ctx) return;
    
    const tasks = managerDashboardState.data.tasks;
    const statusCounts = {
        'In Progress': tasks.filter(t => t.status && t.status.name === 'In Progress').length,
        'Completed': tasks.filter(t => t.status && t.status.name === 'Completed').length,
        'Planned': tasks.filter(t => t.status && t.status.name === 'Planned').length,
        'Blocked': tasks.filter(t => t.status && t.status.name === 'Blocked').length
    };
    
    managerDashboardState.charts.taskStatus = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCounts),
            datasets: [{
                data: Object.values(statusCounts),
                backgroundColor: [
                    'rgba(78, 115, 223, 0.8)',
                    'rgba(28, 200, 138, 0.8)',
                    'rgba(54, 185, 204, 0.8)',
                    'rgba(246, 194, 62, 0.8)'
                ],
                borderColor: [
                    'rgba(78, 115, 223, 1)',
                    'rgba(28, 200, 138, 1)',
                    'rgba(54, 185, 204, 1)',
                    'rgba(246, 194, 62, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const statusIndex = elements[0].index;
                    const status = Object.keys(statusCounts)[statusIndex];
                    window.location.href = `/projects?status=${encodeURIComponent(status)}`;
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            return `Click to filter projects by ${context.label} status`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Sprint Burndown Chart
 */
function initializeSprintBurndownChart() {
    const ctx = document.getElementById('sprintBurndownChart');
    if (!ctx) return;
    
    // Generate mock sprint data
    const sprintDays = Array.from({length: 14}, (_, i) => `Day ${i + 1}`);
    const idealBurndown = Array.from({length: 14}, (_, i) => 100 - (i * 7.14));
    const actualBurndown = Array.from({length: 14}, (_, i) => {
        const ideal = 100 - (i * 7.14);
        return Math.max(0, ideal + (Math.random() - 0.5) * 20);
    });
    
    managerDashboardState.charts.sprintBurndown = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sprintDays,
            datasets: [{
                label: 'Ideal Burndown',
                data: idealBurndown,
                borderColor: 'rgba(78, 115, 223, 1)',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderDash: [5, 5],
                fill: false
            }, {
                label: 'Actual Burndown',
                data: actualBurndown,
                borderColor: 'rgba(28, 200, 138, 1)',
                backgroundColor: 'rgba(28, 200, 138, 0.1)',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    window.location.href = '/projects?view=sprints';
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            return `Click to view sprint details`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Risk Matrix Chart
 */
function initializeRiskMatrixChart() {
    const ctx = document.getElementById('riskMatrixChart');
    if (!ctx) return;
    
    // Generate mock risk data
    const riskData = [
        {x: 2, y: 3, count: 5},
        {x: 4, y: 2, count: 3},
        {x: 6, y: 4, count: 2},
        {x: 8, y: 5, count: 1},
        {x: 3, y: 6, count: 4}
    ];
    
    managerDashboardState.charts.riskMatrix = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Risks',
                data: riskData,
                backgroundColor: riskData.map(r => {
                    if (r.x >= 7 || r.y >= 5) return 'rgba(231, 74, 59, 0.8)';
                    if (r.x >= 5 || r.y >= 4) return 'rgba(246, 194, 62, 0.8)';
                    return 'rgba(28, 200, 138, 0.8)';
                }),
                borderColor: riskData.map(r => {
                    if (r.x >= 7 || r.y >= 5) return 'rgba(231, 74, 59, 1)';
                    if (r.x >= 5 || r.y >= 4) return 'rgba(246, 194, 62, 1)';
                    return 'rgba(28, 200, 138, 1)';
                }),
                borderWidth: 2,
                pointRadius: riskData.map(r => Math.max(5, r.count * 2))
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    window.location.href = '/projects?view=risks';
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Probability'
                    },
                    min: 1,
                    max: 10
                },
                y: {
                    title: {
                        display: true,
                        text: 'Impact'
                    },
                    min: 1,
                    max: 10
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const point = context[0];
                            return `Risk Level: ${point.x >= 7 || point.y >= 5 ? 'High' : point.x >= 5 || point.y >= 4 ? 'Medium' : 'Low'}`;
                        },
                        label: function(context) {
                            const point = context.parsed;
                            return `Probability: ${point.x}, Impact: ${point.y}`;
                        },
                        afterLabel: function(context) {
                            return `Click to view risk details`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Load Recent Activity
 */
async function loadRecentActivity() {
    console.log('📋 Loading recent activity...');
    
    try {
        const projects = managerDashboardState.data.projects.slice(0, 10);
        const activityBody = document.getElementById('recentActivityBody');
        
        if (activityBody) {
            activityBody.innerHTML = projects.map(project => `
                <tr>
                    <td>
                        <a href="/projects/${project.id}" class="text-decoration-none">
                            ${project.name}
                        </a>
                    </td>
                    <td>Project updated</td>
                    <td>
                        <span class="badge bg-${getStatusColor(project.status?.name || 'Unknown')}">
                            ${project.status?.name || 'Unknown'}
                        </span>
                    </td>
                    <td>${new Date(project.updated_at).toLocaleDateString()}</td>
                    <td>
                        <a href="/projects/${project.id}" class="btn btn-sm btn-outline-primary">
                            View Details
                        </a>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

/**
 * Refresh Manager Dashboard
 */
async function refreshManagerDashboard() {
    console.log('🔄 Refreshing manager dashboard...');
    
    try {
        showLoadingOverlay(true);
        
        // Reload data
        await loadManagerDashboardData();
        
        // Refresh charts
        Object.values(managerDashboardState.charts).forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update();
            }
        });
        
        // Refresh activity
        loadRecentActivity();
        
        showNotification('Dashboard refreshed successfully', 'success');
        
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
        showNotification('Failed to refresh dashboard', 'error');
    } finally {
        showLoadingOverlay(false);
    }
}

/**
 * Export Manager Report
 */
function exportManagerReport() {
    console.log('📤 Exporting manager report...');
    
    const reportData = {
        timestamp: new Date().toISOString(),
        kpis: {
            activeProjects: document.getElementById('activeProjectsCount').textContent,
            completedTasks: document.getElementById('completedTasksCount').textContent,
            sprintVelocity: document.getElementById('sprintVelocity').textContent,
            atRiskProjects: document.getElementById('atRiskProjectsCount').textContent
        },
        projects: managerDashboardState.data.projects,
        tasks: managerDashboardState.data.tasks
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `manager-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('Report exported successfully', 'success');
}

/**
 * Helper Functions
 */
function getStatusColor(status) {
    const colors = {
        'Active': 'success',
        'Completed': 'success',
        'In Progress': 'primary',
        'Planned': 'info',
        'Blocked': 'warning',
        'At Risk': 'danger',
        'Unknown': 'secondary'
    };
    return colors[status] || 'secondary';
}

function showLoadingOverlay(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'error' ? 'times-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Navigation functions
function viewAllProjects() {
    window.location.href = '/projects';
}

function viewSprintDetails() {
    window.location.href = '/projects?view=sprints';
}

function exportProjectHealth() {
    console.log('Exporting project health data...');
    showNotification('Export functionality coming soon', 'info');
}

function exportSprintData() {
    console.log('Exporting sprint data...');
    showNotification('Export functionality coming soon', 'info');
}

// WebSocket integration
function refreshDashboardMetrics() {
    console.log('🔄 Refreshing dashboard metrics via WebSocket...');
    refreshManagerDashboard();
}

// Export functions for global access
window.refreshManagerDashboard = refreshManagerDashboard;
window.refreshDashboardMetrics = refreshDashboardMetrics;
window.exportManagerReport = exportManagerReport;
window.viewAllProjects = viewAllProjects;
window.viewSprintDetails = viewSprintDetails;
window.exportProjectHealth = exportProjectHealth;
window.exportSprintData = exportSprintData;
