/**
 * Portfolio Dashboard JavaScript
 * Executive dashboard for portfolio managers and administrators
 */

console.log('🚀 Portfolio Dashboard JavaScript file loaded successfully!');
console.log('🔍 External JS test - this should appear in console');

// Test if JavaScript is executing
setTimeout(() => {
    console.log('🔍 JavaScript execution test - this should appear in console');
    const testElement = document.getElementById('totalProjectsCount');
    if (testElement) {
        console.log('🔍 Found totalProjectsCount element:', testElement);
        testElement.textContent = 'TEST';
    } else {
        console.error('❌ totalProjectsCount element not found!');
    }
}, 1000);

// Portfolio Dashboard State
let portfolioDashboardState = {
    charts: {},
    data: {
        projects: [],
        managers: [],
        risks: [],
        analytics: {}
    },
    isInitialized: false
};

/**
 * Initialize Portfolio Dashboard
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('📊 Initializing Portfolio Dashboard...');
    
    try {
        // Show loading overlay
        showLoadingOverlay(true);
        
        // Load all dashboard data
        await loadPortfolioDashboardData();
        
        // Initialize charts
        console.log('🔧 About to call initializeCharts...');
        initializeCharts();
        console.log('🔧 initializeCharts completed');
        
        // Load at-risk projects
        console.log('🔧 About to call loadAtRiskProjects...');
        loadAtRiskProjects();
        console.log('🔧 loadAtRiskProjects completed');
        
        portfolioDashboardState.isInitialized = true;
        console.log('✅ Portfolio Dashboard initialized successfully');
        
    } catch (error) {
        console.error('❌ Error initializing Portfolio Dashboard:', error);
        showNotification('Failed to load dashboard data', 'error');
    } finally {
        showLoadingOverlay(false);
    }
});

/**
 * Load Portfolio Dashboard Data
 */
async function loadPortfolioDashboardData() {
    console.log('📊 Loading portfolio dashboard data...');
    
    try {
        // Load data in parallel with error handling
        const [projectsResponse, analyticsResponse, dashboardResponse] = await Promise.all([
            fetch('/api/v1/projects?limit=100', { credentials: 'include' }),
            fetch('/api/v1/analytics/comparative-analysis', { credentials: 'include' }),
            fetch('/api/v1/dashboards/metrics', { credentials: 'include' })
        ]);
        
        // Parse responses with error handling
        const projectsData = projectsResponse.ok ? await projectsResponse.json() : [];
        const analyticsData = analyticsResponse.ok ? await analyticsResponse.json() : {};
        const dashboardData = dashboardResponse.ok ? await dashboardResponse.json() : {};
        
        console.log('📊 API Response Status:', {
            projects: projectsResponse.status,
            analytics: analyticsResponse.status,
            dashboard: dashboardResponse.status
        });
        
        console.log('📊 API Response Data:', {
            projectsData: projectsData,
            analyticsData: analyticsData,
            dashboardData: dashboardData
        });
        
        // Handle API response structure - projects API returns {projects: [...]}
        portfolioDashboardState.data.projects = projectsData.projects || projectsData;
        portfolioDashboardState.data.analytics = analyticsData;
        portfolioDashboardState.data.dashboard = dashboardData;
        
        // Extract unique managers
        const projects = portfolioDashboardState.data.projects;
        portfolioDashboardState.data.managers = [...new Set(
            projects.map(p => p.project_manager || p.owner || 'Unassigned')
        )].filter(Boolean);
        
        // Update KPI cards
        console.log('🔧 About to call updateKPICards...');
        updateKPICards();
        console.log('🔧 updateKPICards completed');
        
        console.log(`✅ Loaded ${projects.length} projects and ${portfolioDashboardState.data.managers.length} managers`);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        throw error;
    }
}

/**
 * Update KPI Cards
 */
function updateKPICards() {
    const projects = portfolioDashboardState.data.projects;
    const dashboardData = portfolioDashboardState.data.dashboard;
    
    console.log('🔧 updateKPICards called with:', {
        projects: projects,
        dashboardData: dashboardData,
        projectsLength: projects ? projects.length : 'undefined'
    });
    
    // Use real data from dashboard metrics if available
    if (dashboardData && dashboardData.kpis) {
        const kpis = dashboardData.kpis;
        
        // Total Projects
        const totalProjectsEl = document.getElementById('totalProjectsCount');
        if (totalProjectsEl) {
            totalProjectsEl.textContent = kpis.total_projects || projects.length;
            console.log('✅ Updated totalProjectsCount:', kpis.total_projects);
        } else {
            console.error('❌ Element totalProjectsCount not found');
        }
        
        // Active Projects
        const activeProjectsEl = document.getElementById('activeProjectsCount');
        if (activeProjectsEl) {
            activeProjectsEl.textContent = kpis.active_projects || projects.filter(p => p.status_id === 1).length;
            console.log('✅ Updated activeProjectsCount:', kpis.active_projects);
        } else {
            console.error('❌ Element activeProjectsCount not found');
        }
        
        // Average Portfolio Health (real calculation)
        const avgHealthEl = document.getElementById('avgPortfolioHealth');
        if (avgHealthEl) {
            avgHealthEl.textContent = `${kpis.avg_portfolio_health || 0}%`;
            console.log('✅ Updated avgPortfolioHealth:', kpis.avg_portfolio_health);
        } else {
            console.error('❌ Element avgPortfolioHealth not found');
        }
        
        // Budget Utilization (real calculation)
        const budgetUtilEl = document.getElementById('budgetUtilization');
        if (budgetUtilEl) {
            budgetUtilEl.textContent = `${kpis.budget_utilization || 0}%`;
            console.log('✅ Updated budgetUtilization:', kpis.budget_utilization);
        } else {
            console.error('❌ Element budgetUtilization not found');
        }
        
        console.log('✅ KPI Cards updated with real data:', kpis);
    } else {
        // Fallback to project-based calculations
        const projects = portfolioDashboardState.data.projects;
        
        // Total Projects
        document.getElementById('totalProjectsCount').textContent = projects.length;
        
        // Active Projects
        const activeProjects = projects.filter(p => p.status_id === 1);
        document.getElementById('activeProjectsCount').textContent = activeProjects.length;
        
        // Calculate average portfolio health from project data
        let avgHealth = 0;
        if (projects.length > 0) {
            const healthScores = projects.map(p => {
                let baseHealth = 75;
                if (p.status_id === 1) baseHealth = 85;      // Active
                else if (p.status_id === 2) baseHealth = 95; // Completed
                else if (p.status_id === 4) baseHealth = 45; // At Risk
                
                const completionFactor = (p.percent_complete || 0) * 0.2;
                return Math.min(100, baseHealth + completionFactor);
            });
            avgHealth = Math.round(sum(healthScores) / healthScores.length);
        }
        document.getElementById('avgPortfolioHealth').textContent = `${avgHealth}%`;
        
        // Calculate budget utilization from project data
        const totalBudget = projects.reduce((sum, p) => sum + (parseFloat(p.budget_amount) || 0), 0);
        const totalActualCost = projects.reduce((sum, p) => sum + (parseFloat(p.actual_cost) || 0), 0);
        const budgetUtilization = totalBudget > 0 ? Math.round((totalActualCost / totalBudget) * 100) : 0;
        document.getElementById('budgetUtilization').textContent = `${budgetUtilization}%`;
        
        console.log('✅ KPI Cards updated with calculated data');
    }
}

// Helper function for sum calculation
function sum(arr) {
    return arr.reduce((a, b) => a + b, 0);
}

/**
 * Initialize Charts
 */
function initializeCharts() {
    console.log('📊 Initializing charts...');
    
    // Manager Health Chart
    initializeManagerHealthChart();
    
    // Status Distribution Chart
    initializeStatusDistributionChart();
    
    // Timeline Gantt Chart
    initializeTimelineGanttChart();
    
    // Portfolio Risks Chart
    initializePortfolioRisksChart();
}

/**
 * Initialize Manager Health Chart
 */
function initializeManagerHealthChart() {
    const ctx = document.getElementById('managerHealthChart');
    if (!ctx) return;
    
    const managers = portfolioDashboardState.data.managers.slice(0, 8); // Top 8 managers
    const analyticsData = portfolioDashboardState.data.analytics;
    
    // Use real manager performance data if available
    let healthScores = [];
    if (analyticsData && analyticsData.manager_performance) {
        healthScores = managers.map(manager => {
            const performance = analyticsData.manager_performance[manager];
            return performance ? performance.health_score : 75; // Default fallback
        });
        console.log('✅ Manager Health Chart using real data:', healthScores);
    } else {
        // Fallback: Calculate health scores from project data
        healthScores = managers.map(manager => {
            const managerProjects = portfolioDashboardState.data.projects.filter(p => p.project_manager === manager);
            if (managerProjects.length === 0) return 75;
            
            const avgHealth = managerProjects.reduce((sum, p) => {
                let baseHealth = 75;
                if (p.status_id === 1) baseHealth = 85;      // Active
                else if (p.status_id === 2) baseHealth = 95; // Completed
                else if (p.status_id === 4) baseHealth = 45; // At Risk
                
                const completionFactor = (p.percent_complete || 0) * 0.2;
                return sum + Math.min(100, baseHealth + completionFactor);
            }, 0);
            
            return Math.round(avgHealth / managerProjects.length);
        });
        console.log('✅ Manager Health Chart using calculated data:', healthScores);
    }
    
    portfolioDashboardState.charts.managerHealth = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: managers.map(m => m.substring(0, 12) + '...'),
            datasets: [{
                label: 'Average Health Score',
                data: healthScores,
                backgroundColor: healthScores.map(score => {
                    if (score >= 85) return 'rgba(28, 200, 138, 0.8)';
                    if (score >= 75) return 'rgba(246, 194, 62, 0.8)';
                    return 'rgba(231, 74, 59, 0.8)';
                }),
                borderColor: healthScores.map(score => {
                    if (score >= 85) return 'rgba(28, 200, 138, 1)';
                    if (score >= 75) return 'rgba(246, 194, 62, 1)';
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
                    const managerIndex = elements[0].index;
                    const manager = managers[managerIndex];
                    window.location.href = `/projects?manager=${encodeURIComponent(manager)}`;
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
                            return `Click to filter projects by this manager`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Status Distribution Chart
 */
function initializeStatusDistributionChart() {
    const ctx = document.getElementById('statusDistributionChart');
    if (!ctx) return;
    
    const projects = portfolioDashboardState.data.projects;
    const analyticsData = portfolioDashboardState.data.analytics;
    
    // Use real status distribution data if available
    let statusCounts = {};
    if (analyticsData && analyticsData.status_distribution) {
        statusCounts = analyticsData.status_distribution;
        console.log('✅ Status Distribution Chart using real data:', statusCounts);
    } else {
        // Fallback: Calculate from project data using status_id
        statusCounts = {
            'Active': projects.filter(p => p.status_id === 1).length,
            'Completed': projects.filter(p => p.status_id === 2).length,
            'Planning': projects.filter(p => p.status_id === 3).length,
            'At Risk': projects.filter(p => p.status_id === 4).length
        };
        console.log('✅ Status Distribution Chart using calculated data:', statusCounts);
    }
    
    portfolioDashboardState.charts.statusDistribution = new Chart(ctx, {
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
 * Initialize Timeline Gantt Chart
 */
function initializeTimelineGanttChart() {
    const ctx = document.getElementById('timelineGanttChart');
    if (!ctx) return;
    
    // Get top 10 projects by nearest end date
    const topProjects = portfolioDashboardState.data.projects
        .filter(p => p.due_date)
        .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
        .slice(0, 10);
    
    const projectNames = topProjects.map(p => p.name.substring(0, 20) + '...');
    const startDates = topProjects.map(p => new Date(p.start_date || p.created_at));
    const endDates = topProjects.map(p => new Date(p.due_date));
    
    // Create timeline data
    const timelineData = topProjects.map((project, index) => ({
        x: startDates[index],
        y: index,
        width: endDates[index] - startDates[index],
        project: project
    }));
    
    portfolioDashboardState.charts.timelineGantt = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Project Timeline',
                data: timelineData.map(t => ({
                    x: t.x,
                    y: t.y,
                    project: t.project
                })),
                backgroundColor: topProjects.map(p => {
                    const status = p.status?.name || 'Unknown';
                    if (status === 'Completed') return 'rgba(28, 200, 138, 0.8)';
                    if (status === 'Active') return 'rgba(78, 115, 223, 0.8)';
                    if (status === 'At Risk') return 'rgba(231, 74, 59, 0.8)';
                    return 'rgba(54, 185, 204, 0.8)';
                }),
                borderColor: topProjects.map(p => {
                    const status = p.status?.name || 'Unknown';
                    if (status === 'Completed') return 'rgba(28, 200, 138, 1)';
                    if (status === 'Active') return 'rgba(78, 115, 223, 1)';
                    if (status === 'At Risk') return 'rgba(231, 74, 59, 1)';
                    return 'rgba(54, 185, 204, 1)';
                }),
                borderWidth: 2,
                pointRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const projectIndex = elements[0].index;
                    const project = topProjects[projectIndex];
                    window.location.href = `/projects/${project.id}`;
                }
            },
            scales: {
                x: {
                    type: 'time',
                    title: {
                        display: true,
                        text: 'Timeline'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Projects'
                    },
                    ticks: {
                        callback: function(value) {
                            return projectNames[value] || '';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const project = context[0].raw.project;
                            return project.name;
                        },
                        label: function(context) {
                            const project = context.raw.project;
                            return `Status: ${project.status?.name || 'Unknown'}`;
                        },
                        afterLabel: function(context) {
                            return `Click to view project details`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Portfolio Risks Chart
 */
function initializePortfolioRisksChart() {
    const ctx = document.getElementById('portfolioRisksChart');
    if (!ctx) return;
    
    // Generate mock risk data by project
    const projects = portfolioDashboardState.data.projects.slice(0, 15);
    const riskData = projects.map(project => ({
        x: Math.floor(Math.random() * 10) + 1,
        y: Math.floor(Math.random() * 10) + 1,
        project: project,
        count: Math.floor(Math.random() * 5) + 1
    }));
    
    portfolioDashboardState.charts.portfolioRisks = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Project Risks',
                data: riskData,
                backgroundColor: riskData.map(r => {
                    if (r.x >= 7 || r.y >= 7) return 'rgba(231, 74, 59, 0.8)';
                    if (r.x >= 5 || r.y >= 5) return 'rgba(246, 194, 62, 0.8)';
                    return 'rgba(28, 200, 138, 0.8)';
                }),
                borderColor: riskData.map(r => {
                    if (r.x >= 7 || r.y >= 7) return 'rgba(231, 74, 59, 1)';
                    if (r.x >= 5 || r.y >= 5) return 'rgba(246, 194, 62, 1)';
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
                    const projectIndex = elements[0].index;
                    const project = riskData[projectIndex].project;
                    window.location.href = `/projects/${project.id}?view=risks`;
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Risk Probability'
                    },
                    min: 1,
                    max: 10
                },
                y: {
                    title: {
                        display: true,
                        text: 'Risk Impact'
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
                            const project = context[0].raw.project;
                            return project.name;
                        },
                        label: function(context) {
                            const point = context.parsed;
                            return `Probability: ${point.x}, Impact: ${point.y}`;
                        },
                        afterLabel: function(context) {
                            return `Click to view project risks`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Load At-Risk Projects
 */
async function loadAtRiskProjects() {
    console.log('⚠️ Loading at-risk projects...');
    
    try {
        const projects = portfolioDashboardState.data.projects;
        const atRiskProjects = projects.filter(p => 
            p.status_id === 4  // At Risk status
        ).slice(0, 10); // Top 10 at-risk projects
        
        const atRiskBody = document.getElementById('atRiskProjectsBody');
        
        if (atRiskBody) {
            atRiskBody.innerHTML = atRiskProjects.map(project => {
                // Calculate real health score based on project data
                let healthScore = 45; // Base score for at-risk projects
                if (project.percent_complete) {
                    healthScore += (project.percent_complete * 0.3); // Adjust based on completion
                }
                healthScore = Math.round(Math.min(70, healthScore)); // Cap at 70 for at-risk projects
                
                const riskLevel = healthScore < 50 ? 'High' : healthScore < 60 ? 'Medium' : 'Low';
                
                return `
                    <tr>
                        <td>
                            <a href="/projects/${project.id}" class="text-decoration-none">
                                ${project.name}
                            </a>
                        </td>
                        <td>${project.project_manager || project.owner || 'Unassigned'}</td>
                        <td>
                            <span class="badge bg-${healthScore >= 60 ? 'success' : healthScore >= 50 ? 'warning' : 'danger'}">
                                ${healthScore}%
                            </span>
                        </td>
                        <td>
                            <span class="badge bg-${riskLevel === 'High' ? 'danger' : riskLevel === 'Medium' ? 'warning' : 'success'}">
                                ${riskLevel}
                            </span>
                        </td>
                        <td>${project.due_date ? new Date(project.due_date).toLocaleDateString() : 'N/A'}</td>
                        <td>
                            <a href="/projects/${project.id}" class="btn btn-sm btn-outline-primary">
                                View Details
                            </a>
                        </td>
                    </tr>
                `;
            }).join('');
        }
        
    } catch (error) {
        console.error('Error loading at-risk projects:', error);
    }
}

/**
 * Refresh Portfolio Dashboard
 */
async function refreshPortfolioDashboard() {
    console.log('🔄 Refreshing portfolio dashboard...');
    
    try {
        showLoadingOverlay(true);
        
        // Reload data
        await loadPortfolioDashboardData();
        
        // Refresh charts
        Object.values(portfolioDashboardState.charts).forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update();
            }
        });
        
        // Refresh at-risk projects
        loadAtRiskProjects();
        
        showNotification('Dashboard refreshed successfully', 'success');
        
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
        showNotification('Failed to refresh dashboard', 'error');
    } finally {
        showLoadingOverlay(false);
    }
}

/**
 * Export Portfolio Report
 */
function exportPortfolioReport() {
    console.log('📤 Exporting portfolio report...');
    
    const reportData = {
        timestamp: new Date().toISOString(),
        kpis: {
            totalProjects: document.getElementById('totalProjectsCount').textContent,
            activeProjects: document.getElementById('activeProjectsCount').textContent,
            avgPortfolioHealth: document.getElementById('avgPortfolioHealth').textContent,
            budgetUtilization: document.getElementById('budgetUtilization').textContent
        },
        projects: portfolioDashboardState.data.projects,
        managers: portfolioDashboardState.data.managers
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('Report exported successfully', 'success');
}

/**
 * Helper Functions
 */
function showLoadingOverlay(show) {
    const overlay = document.getElementById('loadingOverlay');
    console.log(`🔧 showLoadingOverlay(${show}) - overlay found:`, !!overlay);
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
        console.log(`🔧 Loading overlay display set to: ${overlay.style.display}`);
    } else {
        console.error('❌ Loading overlay element not found!');
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

function viewManagerDetails() {
    window.location.href = '/projects?view=managers';
}

function exportManagerHealth() {
    console.log('Exporting manager health data...');
    showNotification('Export functionality coming soon', 'info');
}

function exportTimelineData() {
    console.log('Exporting timeline data...');
    showNotification('Export functionality coming soon', 'info');
}

// WebSocket integration
function refreshDashboardMetrics() {
    console.log('🔄 Refreshing dashboard metrics via WebSocket...');
    refreshPortfolioDashboard();
}

// Export functions for global access
window.refreshPortfolioDashboard = refreshPortfolioDashboard;
window.refreshDashboardMetrics = refreshDashboardMetrics;
window.exportPortfolioReport = exportPortfolioReport;
window.viewAllProjects = viewAllProjects;
window.viewManagerDetails = viewManagerDetails;
window.exportManagerHealth = exportManagerHealth;
window.exportTimelineData = exportTimelineData;
