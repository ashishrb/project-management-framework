/**
 * Enhanced Manager Dashboard JavaScript
 * Handles Overview, Backlog Management, Work Plan, and Risk Management
 */

// Global variables
let currentUser = null;
let managerProjects = [];
let backlogItems = [];
let riskItems = [];

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeManagerDashboard();
});

/**
 * Initialize the manager dashboard
 */
async function initializeManagerDashboard() {
    try {
        // Get current user from session
        const userData = sessionStorage.getItem('user');
        if (userData) {
            currentUser = JSON.parse(userData);
        }

        // Load initial data
        await loadManagerData();
        
        // Initialize charts
        initializeCharts();
        
        // Set up event listeners
        setupEventListeners();
        
        console.log('Manager dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing manager dashboard:', error);
        showError('Failed to initialize dashboard');
    }
}

/**
 * Load manager-specific data
 */
async function loadManagerData() {
    try {
        // Load projects for current manager
        await loadManagerProjects();
        
        // Load backlog items for manager's projects
        await loadManagerBacklog();
        
        // Load risk data
        await loadRiskData();
        
        // Load dashboard stats
        await loadDashboardStats();
        
        // Update recent activity
        updateRecentActivity();
        
    } catch (error) {
        console.error('Error loading manager data:', error);
    }
}

/**
 * Load projects assigned to current manager
 */
async function loadManagerProjects() {
    try {
        const response = await fetch('/api/v1/projects', {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            managerProjects = data.projects || [];
            console.log('Projects API response:', data);
            console.log(`Loaded ${managerProjects.length} projects for manager`);
        } else {
            console.error('Failed to load projects:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error response:', errorText);
        }
    } catch (error) {
        console.error('Error loading manager projects:', error);
    }
}

/**
 * Load backlog items for manager's projects
 */
async function loadManagerBacklog() {
    try {
        const response = await fetch('/api/v1/backlogs', {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            const backlogs = data.backlogs || [];
            // Filter backlog items for manager's projects
            const managerProjectIds = managerProjects.map(p => p.id);
            backlogItems = backlogs.filter(backlog => {
                // Check if backlog is assigned to manager's projects
                return backlog.description && 
                       managerProjectIds.some(id => 
                           backlog.description.includes(`Project ${id}`)
                       );
            });
            console.log(`Loaded ${backlogItems.length} backlog items for manager`);
            updateBacklogTable();
            updateBacklogStats();
        }
    } catch (error) {
        console.error('Error loading manager backlog:', error);
    }
}

/**
 * Load risk data
 */
async function loadRiskData() {
    try {
        // For demo purposes, create sample risk data
        riskItems = [
            {
                id: 1,
                risk: 'Resource Shortage',
                project: 'AI-Powered Analytics Platform',
                level: 'High',
                probability: 70,
                impact: 80,
                score: 75,
                status: 'Open'
            },
            {
                id: 2,
                risk: 'Technical Complexity',
                project: 'Digital Transformation Initiative',
                level: 'Medium',
                probability: 50,
                impact: 60,
                score: 55,
                status: 'In Progress'
            },
            {
                id: 3,
                risk: 'Budget Overrun',
                project: 'Customer Experience Enhancement',
                level: 'Low',
                probability: 30,
                impact: 40,
                score: 35,
                status: 'Mitigated'
            }
        ];
        
        updateRiskTable();
        updateRiskStats();
    } catch (error) {
        console.error('Error loading risk data:', error);
    }
}

/**
 * Load dashboard statistics from API
 */
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/v1/dashboard/stats', {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            dashboardStats = data;
            
            console.log('Dashboard stats API response:', data);
            
            // Update KPI cards with real data
            updateKPICards();
            
            console.log('Dashboard stats loaded:', dashboardStats);
        } else {
            console.error('Failed to load dashboard stats:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error response:', errorText);
            // Fallback to empty stats
            dashboardStats = {
                projects: { total: 0, on_track: 0, at_risk: 0, completed: 0 },
                backlog: { total: 0, high_priority: 0, in_progress: 0, completed: 0 },
                overdue_tasks: 0
            };
            updateKPICards();
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Fallback to empty stats
        dashboardStats = {
            projects: { total: 0, on_track: 0, at_risk: 0, completed: 0 },
            backlog: { total: 0, high_priority: 0, in_progress: 0, completed: 0 },
            overdue_tasks: 0
        };
        updateKPICards();
    }
}

/**
 * Update KPI cards with current data
 */
function updateKPICards() {
    // My Active Projects
    const activeProjectsEl = document.getElementById('myActiveProjectsCount');
    if (activeProjectsEl) {
        activeProjectsEl.textContent = dashboardStats.projects?.total || managerProjects.length;
    }
    
    // Projects On Track
    const onTrackEl = document.getElementById('projectsOnTrackCount');
    if (onTrackEl) {
        onTrackEl.textContent = dashboardStats.projects?.on_track || 0;
    }
    
    // Projects At Risk
    const atRiskEl = document.getElementById('projectsAtRiskCount');
    if (atRiskEl) {
        atRiskEl.textContent = dashboardStats.projects?.at_risk || 0;
    }
    
    // Overdue Tasks
    const overdueEl = document.getElementById('overdueTasksCount');
    if (overdueEl) {
        overdueEl.textContent = dashboardStats.overdue_tasks || 0;
    }
    
    console.log('KPI cards updated with real data');
}

/**
 * Update recent activity table with real data
 */
function updateRecentActivity() {
    const tableBody = document.getElementById('recentActivityBody');
    if (!tableBody) return;
    
    // Clear existing content
    tableBody.innerHTML = '';
    
    // Generate recent activities from project data
    const activities = [];
    
    managerProjects.forEach(project => {
        // Add project creation activity
        activities.push({
            project: project.name,
            project_id: project.id,
            activity: 'Project Created',
            status: 'Completed',
            date: new Date(project.created_at).toLocaleDateString(),
            action: 'View Details'
        });
        
        // Add project update activity
        if (project.updated_at && project.updated_at !== project.created_at) {
            activities.push({
                project: project.name,
                project_id: project.id,
                activity: 'Project Updated',
                status: 'Completed',
                date: new Date(project.updated_at).toLocaleDateString(),
                action: 'View Details'
            });
        }
        
        // Add progress update activity
        if (project.percent_complete > 0) {
            activities.push({
                project: project.name,
                project_id: project.id,
                activity: `Progress Update (${project.percent_complete}%)`,
                status: 'In Progress',
                date: new Date().toLocaleDateString(),
                action: 'View Details'
            });
        }
    });
    
    // Sort by date (most recent first) and limit to 10
    activities.sort((a, b) => new Date(b.date) - new Date(a.date));
    const recentActivities = activities.slice(0, 10);
    
    // Populate table
    recentActivities.forEach(activity => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${activity.project}</td>
            <td>${activity.activity}</td>
            <td><span class="badge bg-${activity.status === 'Completed' ? 'success' : 'primary'}">${activity.status}</span></td>
            <td>${activity.date}</td>
            <td><button class="btn btn-sm btn-outline-primary" onclick="viewProjectDetails(${activity.project_id})">${activity.action}</button></td>
        `;
        tableBody.appendChild(row);
    });
    
    console.log(`Updated recent activity table with ${recentActivities.length} activities`);
}

/**
 * View project details - navigate to project detail page
 */
function viewProjectDetails(projectId) {
    console.log(`Viewing details for project ID: ${projectId}`);
    // Navigate to the project detail page
    window.location.href = `/project/${projectId}`;
}

/**
 * Update backlog statistics
 */
function updateBacklogStats() {
    const total = backlogItems.length;
    const highPriority = backlogItems.filter(b => b.priority_id >= 3).length;
    const inProgress = backlogItems.filter(b => b.status_id === 2).length;
    const completed = backlogItems.filter(b => b.status_id === 3).length;
    
    document.getElementById('total-backlog').textContent = total;
    document.getElementById('high-priority').textContent = highPriority;
    document.getElementById('in-progress').textContent = inProgress;
    document.getElementById('completed').textContent = completed;
}

/**
 * Update backlog table
 */
function updateBacklogTable() {
    const tbody = document.getElementById('backlogTableBody');
    tbody.innerHTML = '';
    
    if (backlogItems.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fas fa-inbox fa-2x mb-2"></i>
                    <p>No backlog items found for your projects</p>
                </td>
            </tr>
        `;
        return;
    }
    
    backlogItems.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${item.name}</strong>
                <br><small class="text-muted">${item.description?.substring(0, 50)}...</small>
            </td>
            <td>
                <span class="badge ${getPriorityBadgeClass(item.priority_id)}">
                    ${getPriorityText(item.priority_id)}
                </span>
            </td>
            <td>
                <span class="badge ${getStatusBadgeClass(item.status_id)}">
                    ${getStatusText(item.status_id)}
                </span>
            </td>
            <td>${item.complexity || 'Medium'}</td>
            <td>${item.effort_estimate || 'N/A'}</td>
            <td>${item.target_quarter || 'Q1 2025'}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editBacklogItem(${item.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteBacklogItem(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Update risk statistics
 */
function updateRiskStats() {
    const total = riskItems.length;
    const high = riskItems.filter(r => r.level === 'High').length;
    const medium = riskItems.filter(r => r.level === 'Medium').length;
    const low = riskItems.filter(r => r.level === 'Low').length;
    
    document.getElementById('total-risk-count').textContent = total;
    document.getElementById('high-risk-count').textContent = high;
    document.getElementById('medium-risk-count').textContent = medium;
    document.getElementById('low-risk-count').textContent = low;
}

/**
 * Update risk table
 */
function updateRiskTable() {
    const tbody = document.getElementById('risks-table');
    tbody.innerHTML = '';
    
    riskItems.forEach(risk => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${risk.risk}</strong></td>
            <td>${risk.project}</td>
            <td>
                <span class="badge ${getRiskLevelBadgeClass(risk.level)}">
                    ${risk.level}
                </span>
            </td>
            <td>${risk.probability}%</td>
            <td>${risk.impact}%</td>
            <td><strong>${risk.score}</strong></td>
            <td>
                <span class="badge ${getRiskStatusBadgeClass(risk.status)}">
                    ${risk.status}
                </span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editRisk(${risk.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteRisk(${risk.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Initialize charts
 */
function initializeCharts() {
    // Project Health Chart
    const projectHealthCtx = document.getElementById('projectHealthChart');
    if (projectHealthCtx) {
        // Calculate actual health scores based on project data
        const healthScores = managerProjects.map(p => {
            // Calculate health score based on project status and completion
            let baseScore = 50; // Base score
            
            // Adjust based on status
            if (p.status_id === 1) baseScore += 30; // Active projects
            else if (p.status_id === 2) baseScore += 40; // Completed projects
            else if (p.status_id === 3) baseScore -= 20; // At risk projects
            else if (p.status_id === 4) baseScore -= 30; // Off track projects
            
            // Adjust based on completion percentage
            if (p.percent_complete) {
                baseScore += (p.percent_complete * 0.3); // Up to 30 points for completion
            }
            
            return Math.max(0, Math.min(100, Math.floor(baseScore)));
        });
        
        new Chart(projectHealthCtx, {
        type: 'bar',
        data: {
                labels: managerProjects.map(p => p.name),
            datasets: [{
                label: 'Health Score',
                    data: healthScores,
                    backgroundColor: healthScores.map(score => 
                        score >= 80 ? 'rgba(75, 192, 192, 0.8)' : // Green for healthy
                        score >= 60 ? 'rgba(255, 206, 86, 0.8)' : // Yellow for moderate
                        'rgba(255, 99, 132, 0.8)' // Red for unhealthy
                    ),
                    borderColor: healthScores.map(score => 
                        score >= 80 ? 'rgba(75, 192, 192, 1)' :
                        score >= 60 ? 'rgba(255, 206, 86, 1)' :
                        'rgba(255, 99, 132, 1)'
                    ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

    // Task Status Chart
    const taskStatusCtx = document.getElementById('taskStatusChart');
    if (taskStatusCtx) {
        // Calculate actual task status distribution from backlog items
        const inProgress = backlogItems.filter(b => b.status_id === 2).length;
        const completed = backlogItems.filter(b => b.status_id === 3).length;
        const planned = backlogItems.filter(b => b.status_id === 1).length;
        const blocked = backlogItems.filter(b => b.status_id === 4).length;
        
        new Chart(taskStatusCtx, {
        type: 'doughnut',
        data: {
                labels: ['In Progress', 'Completed', 'Planned', 'Blocked'],
            datasets: [{
                    data: [inProgress, completed, planned, blocked],
                backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ]
            }]
        },
        options: {
            responsive: true,
                maintainAspectRatio: false
        }
    });
}

    // Sprint Burndown Chart
    const sprintBurndownCtx = document.getElementById('sprintBurndownChart');
    if (sprintBurndownCtx) {
        // Generate sample sprint burndown data
        const sprintDays = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'];
        const idealBurndown = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10];
        const actualBurndown = [100, 95, 85, 75, 70, 65, 55, 45, 35, 25];
        
        new Chart(sprintBurndownCtx, {
        type: 'line',
        data: {
            labels: sprintDays,
            datasets: [{
                label: 'Ideal Burndown',
                data: idealBurndown,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
            }, {
                label: 'Actual Burndown',
                data: actualBurndown,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

    // Risk Matrix Chart
    const riskMatrixCtx = document.getElementById('riskMatrixChart');
    if (riskMatrixCtx) {
        // Generate risk matrix data based on project risks
    const riskData = [
            { x: 2, y: 3, label: 'Technical Risk', count: 1 },
            { x: 4, y: 2, label: 'Resource Risk', count: 1 },
            { x: 3, y: 4, label: 'Schedule Risk', count: 1 },
            { x: 1, y: 2, label: 'Budget Risk', count: 1 }
        ];
        
        new Chart(riskMatrixCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                    label: 'Project Risks',
                    data: riskData.map(risk => ({ x: risk.x, y: risk.y })),
                    backgroundColor: riskData.map(risk => 
                        risk.x * risk.y >= 12 ? 'rgba(255, 99, 132, 0.8)' : // High risk
                        risk.x * risk.y >= 8 ? 'rgba(255, 206, 86, 0.8)' : // Medium risk
                        'rgba(75, 192, 192, 0.8)' // Low risk
                    ),
                    borderColor: riskData.map(risk => 
                        risk.x * risk.y >= 12 ? 'rgba(255, 99, 132, 1)' :
                        risk.x * risk.y >= 8 ? 'rgba(255, 206, 86, 1)' :
                        'rgba(75, 192, 192, 1)'
                    ),
                borderWidth: 2,
                    pointRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Probability'
                    },
                        min: 0,
                        max: 5
                },
                y: {
                    title: {
                        display: true,
                        text: 'Impact'
                    },
                        min: 0,
                        max: 5
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                                const risk = riskData[context.dataIndex];
                                return `${risk.label}: P${risk.x} I${risk.y}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Initialize mini Gantt chart
    initializeMiniGantt();
}

/**
 * Initialize mini Gantt chart
 */
function initializeMiniGantt() {
    const timeline = document.getElementById('ganttTimelineMini');
    const tasks = document.getElementById('ganttTasksMini');
    
    if (!timeline || !tasks) return;
    
    // Generate timeline
    timeline.innerHTML = '';
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    months.forEach(month => {
        const period = document.createElement('div');
        period.className = 'gantt-period-mini';
        period.textContent = month;
        timeline.appendChild(period);
    });
    
    // Generate task bars
    tasks.innerHTML = '';
    managerProjects.forEach((project, index) => {
        const task = document.createElement('div');
        task.className = 'gantt-task-mini';
        task.style.marginTop = `${index * 30}px`;
        task.style.width = `${Math.random() * 200 + 100}px`;
        task.textContent = project.name;
        
        // Random status
        const statuses = ['completed', 'in-progress', 'planned', 'overdue'];
        task.classList.add(statuses[Math.floor(Math.random() * statuses.length)]);
        
        tasks.appendChild(task);
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Backlog search
    const searchInput = document.getElementById('searchBacklog');
    if (searchInput) {
        searchInput.addEventListener('input', filterBacklogItems);
    }
    
    // Backlog filters
    const priorityFilter = document.getElementById('priorityFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (priorityFilter) {
        priorityFilter.addEventListener('change', filterBacklogItems);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterBacklogItems);
    }
}

/**
 * Filter backlog items
 */
function filterBacklogItems() {
    const searchTerm = document.getElementById('searchBacklog')?.value.toLowerCase() || '';
    const priorityFilter = document.getElementById('priorityFilter')?.value || '';
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    
    const filteredItems = backlogItems.filter(item => {
        const matchesSearch = item.name.toLowerCase().includes(searchTerm) ||
                             item.description?.toLowerCase().includes(searchTerm);
        const matchesPriority = !priorityFilter || item.priority_id == priorityFilter;
        const matchesStatus = !statusFilter || item.status_id == statusFilter;
        
        return matchesSearch && matchesPriority && matchesStatus;
    });
    
    // Update table with filtered items
    updateBacklogTableWithItems(filteredItems);
}

/**
 * Update backlog table with specific items
 */
function updateBacklogTableWithItems(items) {
    const tbody = document.getElementById('backlogTableBody');
    tbody.innerHTML = '';
    
    items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${item.name}</strong>
                <br><small class="text-muted">${item.description?.substring(0, 50)}...</small>
            </td>
            <td>
                <span class="badge ${getPriorityBadgeClass(item.priority_id)}">
                    ${getPriorityText(item.priority_id)}
                </span>
            </td>
            <td>
                <span class="badge ${getStatusBadgeClass(item.status_id)}">
                    ${getStatusText(item.status_id)}
                </span>
            </td>
            <td>${item.complexity || 'Medium'}</td>
            <td>${item.effort_estimate || 'N/A'}</td>
            <td>${item.target_quarter || 'Q1 2025'}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editBacklogItem(${item.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteBacklogItem(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Utility functions
function getPriorityBadgeClass(priorityId) {
    const classes = {
        1: 'bg-secondary',
        2: 'bg-info',
        3: 'bg-warning',
        4: 'bg-danger'
    };
    return classes[priorityId] || 'bg-secondary';
}

function getPriorityText(priorityId) {
    const texts = {
        1: 'Low',
        2: 'Medium',
        3: 'High',
        4: 'Critical'
    };
    return texts[priorityId] || 'Unknown';
}

function getStatusBadgeClass(statusId) {
    const classes = {
        1: 'bg-secondary',
        2: 'bg-primary',
        3: 'bg-success',
        4: 'bg-warning'
    };
    return classes[statusId] || 'bg-secondary';
}

function getStatusText(statusId) {
    const texts = {
        1: 'Not Started',
        2: 'In Progress',
        3: 'Completed',
        4: 'On Hold'
    };
    return texts[statusId] || 'Unknown';
}

function getRiskLevelBadgeClass(level) {
    const classes = {
        'High': 'bg-danger',
        'Medium': 'bg-warning',
        'Low': 'bg-success'
    };
    return classes[level] || 'bg-secondary';
}

function getRiskStatusBadgeClass(status) {
    const classes = {
        'Open': 'bg-danger',
        'In Progress': 'bg-warning',
        'Mitigated': 'bg-success',
        'Closed': 'bg-secondary'
    };
    return classes[status] || 'bg-secondary';
}

// Action functions
function refreshManagerDashboard() {
    location.reload();
}

function exportManagerReport() {
    alert('Export functionality would be implemented here');
}

function showCreateBacklogModal() {
    alert('Create backlog modal would be implemented here');
}

function showSprintPlanningModal() {
    alert('Sprint planning modal would be implemented here');
}

function exportBacklog() {
    alert('Export backlog functionality would be implemented here');
}

function clearBacklogFilters() {
    document.getElementById('searchBacklog').value = '';
    document.getElementById('priorityFilter').value = '';
    document.getElementById('statusFilter').value = '';
    updateBacklogTable();
}

function editBacklogItem(id) {
    alert(`Edit backlog item ${id} functionality would be implemented here`);
}

function deleteBacklogItem(id) {
    if (confirm('Are you sure you want to delete this backlog item?')) {
        alert(`Delete backlog item ${id} functionality would be implemented here`);
    }
}

function exportWorkPlan() {
    alert('Export work plan functionality would be implemented here');
}

function refreshWorkPlan() {
    initializeMiniGantt();
}

function addRisk() {
    alert('Add risk functionality would be implemented here');
}

function editRisk(id) {
    alert(`Edit risk ${id} functionality would be implemented here`);
}

function deleteRisk(id) {
    if (confirm('Are you sure you want to delete this risk?')) {
        alert(`Delete risk ${id} functionality would be implemented here`);
    }
}

function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    errorDiv.style.top = '20px';
    errorDiv.style.right = '20px';
    errorDiv.style.zIndex = '9999';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}