/**
 * Comprehensive Project Management JavaScript
 * GenAI Metrics Dashboard - Project Management Features
 */

// Global variables
let projectsData = [];
let filteredProjects = [];
let currentView = 'table';
let sortField = 'name';
let sortDirection = 'asc';
let selectedProjects = new Set();

// Status and Priority mappings
const STATUS_MAP = {
    1: 'Active',
    2: 'Completed', 
    3: 'At Risk',
    4: 'Off Track',
    5: 'On Hold',
    6: 'Cancelled'
};

const PRIORITY_MAP = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Critical',
    5: 'Very Low',
    6: 'Very High'
};

const STATUS_CLASSES = {
    'Active': 'bg-success',
    'Completed': 'bg-info',
    'At Risk': 'bg-warning',
    'Off Track': 'bg-danger'
};

const PRIORITY_CLASSES = {
    'Low': 'bg-success',
    'Medium': 'bg-info', 
    'High': 'bg-warning',
    'Critical': 'bg-danger'
};

/**
 * Initialize projects page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Project Management...');
    console.log('DOM Content Loaded - Projects page');
    
    // Test if we can find the table body
    const tbody = document.getElementById('projectsTableBody');
    console.log('Table body found:', !!tbody);
    
    loadProjects();
    loadLookupData();
    setupEventListeners();
});

// Also try immediate execution as fallback
console.log('📋 Projects.js loaded');

if (document.readyState === 'loading') {
    console.log('📋 Document still loading, waiting for DOMContentLoaded');
} else {
    console.log('📋 Document already loaded, initializing immediately');
    loadProjects();
    loadLookupData();
    setupEventListeners();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchProjects, 300));
    }
    
    // Select all checkbox
    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        selectAll.addEventListener('change', toggleSelectAll);
    }
}

/**
 * Load projects data from API
 */
async function loadProjects() {
    try {
        console.log('📊 Loading projects data...');
        showLoading(true);
        
        const response = await fetch('/api/v1/projects/');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        projectsData = await response.json();
        console.log('Projects data received:', projectsData.length, 'projects');
        console.log('Sample project:', projectsData[0]);
        
        filteredProjects = [...projectsData];
        
        updateStatistics();
        renderProjects();
        
        console.log(`✅ Loaded ${projectsData.length} projects`);
        
    } catch (error) {
        console.error('❌ Error loading projects:', error);
        showError('Failed to load projects: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Load lookup data for filters
 */
async function loadLookupData() {
    try {
        // Load portfolios for filter
        const response = await fetch('/api/v1/lookup/portfolios');
        if (response.ok) {
            const portfolios = await response.json();
            const portfolioFilter = document.getElementById('portfolioFilter');
            if (portfolioFilter) {
                portfolioFilter.innerHTML = '<option value="">All Portfolios</option>' +
                    portfolios.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
            }
        }
    } catch (error) {
        console.error('Error loading lookup data:', error);
    }
}

/**
 * Update statistics cards
 */
function updateStatistics() {
    const stats = {
        total: projectsData.length,
        active: projectsData.filter(p => STATUS_MAP[p.status_id] === 'Active').length,
        atRisk: projectsData.filter(p => STATUS_MAP[p.status_id] === 'At Risk').length,
        completed: projectsData.filter(p => STATUS_MAP[p.status_id] === 'Completed').length
    };
    
    document.getElementById('total-projects').textContent = stats.total;
    document.getElementById('active-projects').textContent = stats.active;
    document.getElementById('at-risk-projects').textContent = stats.atRisk;
    document.getElementById('completed-projects').textContent = stats.completed;
}

/**
 * Render projects based on current view
 */
function renderProjects() {
    if (currentView === 'table') {
        renderTableView();
    } else {
        renderCardsView();
    }
}

/**
 * Render table view
 */
function renderTableView() {
    console.log('🎨 Rendering table view with', filteredProjects.length, 'projects');
    const tbody = document.getElementById('projectsTableBody');
    
    if (!tbody) {
        console.error('❌ Table body element not found');
        return;
    }
    
    if (filteredProjects.length === 0) {
        console.log('📭 No projects to display');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="fas fa-search fa-2x mb-2"></i>
                    <p>No projects found matching your criteria</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filteredProjects.map(project => {
        const statusName = STATUS_MAP[project.status_id] || 'Unknown';
        const priorityName = PRIORITY_MAP[project.priority_id] || 'Unknown';
        const progressPercent = parseFloat(project.percent_complete) || 0;
        
        return `
        <tr>
            <td>
                <input type="checkbox" class="form-check-input project-checkbox" 
                       value="${project.project_id}" onchange="toggleProjectSelection('${project.project_id}')">
            </td>
            <td>
                <div class="project-name">
                    <strong>${project.name || 'Unnamed Project'}</strong>
                    ${project.description ? `<br><small class="text-muted">${truncateText(project.description, 60)}</small>` : ''}
                </div>
            </td>
            <td>
                <span class="badge ${STATUS_CLASSES[statusName] || 'bg-secondary'}">
                    ${statusName}
                </span>
            </td>
            <td>
                <span class="badge ${PRIORITY_CLASSES[priorityName] || 'bg-secondary'}">
                    ${priorityName}
                </span>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="progress flex-grow-1 me-2" style="height: 8px;">
                        <div class="progress-bar ${getProgressBarClass(progressPercent)}" 
                             style="width: ${progressPercent}%"></div>
                    </div>
                    <small class="text-muted">${progressPercent}%</small>
                </div>
            </td>
            <td>${project.project_manager || 'N/A'}</td>
            <td>
                ${project.due_date ? 
                    `<span class="${getDateClass(project.due_date)}">${formatDate(project.due_date)}</span>` : 
                    'N/A'
                }
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewProject('${project.project_id}')" 
                            title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-secondary" onclick="editProject('${project.project_id}')" 
                            title="Edit Project">
                        <i class="fas fa-edit"></i>
                    </button>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-secondary dropdown-toggle" 
                                data-bs-toggle="dropdown" title="More Actions">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="duplicateProject('${project.project_id}')">
                                <i class="fas fa-copy me-2"></i>Duplicate
                            </a></li>
                            <li><a class="dropdown-item" href="#" onclick="exportProject('${project.project_id}')">
                                <i class="fas fa-download me-2"></i>Export
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="deleteProject('${project.project_id}')">
                                <i class="fas fa-trash me-2"></i>Delete
                            </a></li>
                        </ul>
                    </div>
                </div>
            </td>
        </tr>
        `;
    }).join('');
}

/**
 * Render cards view
 */
function renderCardsView() {
    const container = document.getElementById('projectsCardsContainer');
    
    if (filteredProjects.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                <i class="fas fa-search fa-3x mb-3"></i>
                <h5>No projects found</h5>
                <p>No projects match your current filters</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filteredProjects.map(project => {
        const statusName = STATUS_MAP[project.status_id] || 'Unknown';
        const priorityName = PRIORITY_MAP[project.priority_id] || 'Unknown';
        const progressPercent = parseFloat(project.percent_complete) || 0;
        
        return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">${project.name || 'Unnamed Project'}</h6>
                    <span class="badge ${STATUS_CLASSES[statusName] || 'bg-secondary'}">
                        ${statusName}
                    </span>
                </div>
                <div class="card-body">
                    <p class="card-text text-muted small">
                        ${project.description ? truncateText(project.description, 100) : 'No description available'}
                    </p>
                    
                    <div class="mb-3">
                        <div class="d-flex justify-content-between mb-1">
                            <small>Progress</small>
                            <small>${progressPercent}%</small>
                        </div>
                        <div class="progress" style="height: 6px;">
                            <div class="progress-bar ${getProgressBarClass(progressPercent)}" 
                                 style="width: ${progressPercent}%"></div>
                        </div>
                    </div>
                    
                    <div class="row text-center">
                        <div class="col-6">
                            <small class="text-muted">Priority</small>
                            <div>
                                <span class="badge ${PRIORITY_CLASSES[priorityName] || 'bg-secondary'}">
                                    ${priorityName}
                                </span>
                            </div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Manager</small>
                            <div><strong>${project.project_manager || 'N/A'}</strong></div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            Due: ${project.due_date ? formatDate(project.due_date) : 'N/A'}
                        </small>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="viewProject(${project.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-secondary" onclick="editProject(${project.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

/**
 * Search projects
 */
function searchProjects() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    filteredProjects = projectsData.filter(project => {
        return (
            (project.name && project.name.toLowerCase().includes(searchTerm)) ||
            (project.project_id && project.project_id.toLowerCase().includes(searchTerm)) ||
            (project.project_manager && project.project_manager.toLowerCase().includes(searchTerm)) ||
            (project.description && project.description.toLowerCase().includes(searchTerm))
        );
    });
    
    applyFilters();
}

/**
 * Filter projects
 */
function filterProjects() {
    const statusFilter = document.getElementById('statusFilter').value;
    const priorityFilter = document.getElementById('priorityFilter').value;
    const portfolioFilter = document.getElementById('portfolioFilter').value;
    
    filteredProjects = projectsData.filter(project => {
        const statusMatch = !statusFilter || STATUS_MAP[project.status_id] === statusFilter;
        const priorityMatch = !priorityFilter || PRIORITY_MAP[project.priority_id] === priorityFilter;
        const portfolioMatch = !portfolioFilter || project.portfolio_id == portfolioFilter;
        
        return statusMatch && priorityMatch && portfolioMatch;
    });
    
    applyFilters();
}

/**
 * Apply all filters and render
 */
function applyFilters() {
    sortProjects();
    renderProjects();
    updateStatistics();
}

/**
 * Sort projects
 */
function sortProjects(field = null) {
    if (field) {
        if (sortField === field) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortField = field;
            sortDirection = 'asc';
        }
    }
    
    filteredProjects.sort((a, b) => {
        let aVal = a[sortField];
        let bVal = b[sortField];
        
        // Handle nested objects
        if (sortField === 'status') {
            aVal = STATUS_MAP[a.status_id] || '';
            bVal = STATUS_MAP[b.status_id] || '';
        } else if (sortField === 'priority') {
            aVal = PRIORITY_MAP[a.priority_id] || '';
            bVal = PRIORITY_MAP[b.priority_id] || '';
        }
        
        // Handle dates
        if (sortField === 'due_date') {
            aVal = new Date(aVal || '1900-01-01');
            bVal = new Date(bVal || '1900-01-01');
        }
        
        // Handle numeric fields
        if (sortField === 'percent_complete') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        }
        
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        if (sortDirection === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
    
    renderProjects();
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('priorityFilter').value = '';
    document.getElementById('portfolioFilter').value = '';
    
    filteredProjects = [...projectsData];
    applyFilters();
}

/**
 * Toggle view between table and cards
 */
function toggleView(view) {
    currentView = view;
    
    // Update button states
    document.getElementById('tableViewBtn').classList.toggle('active', view === 'table');
    document.getElementById('cardsViewBtn').classList.toggle('active', view === 'cards');
    
    // Show/hide views
    document.getElementById('tableView').style.display = view === 'table' ? 'block' : 'none';
    document.getElementById('cardsView').style.display = view === 'cards' ? 'block' : 'none';
    
    renderProjects();
}

/**
 * Show create project modal
 */
function showCreateProjectModal() {
    const modal = new bootstrap.Modal(document.getElementById('createProjectModal'));
    modal.show();
}

/**
 * Create new project
 */
async function createProject() {
    try {
        const formData = {
            name: document.getElementById('projectName').value,
            project_id: document.getElementById('projectId').value || null,
            description: document.getElementById('projectDescription').value,
            status_id: parseInt(document.getElementById('projectStatus').value),
            priority_id: parseInt(document.getElementById('projectPriority').value),
            project_type_id: parseInt(document.getElementById('projectType').value),
            portfolio_id: parseInt(document.getElementById('projectPortfolio').value),
            criticality_id: parseInt(document.getElementById('criticality').value) || null,
            investment_type_id: parseInt(document.getElementById('investmentType').value) || null,
            modernization_domain: document.getElementById('modernizationDomain').value || null,
            digitization_category: document.getElementById('digitizationCategory').value || null,
            funding_status: document.getElementById('fundingStatus').value || null,
            budget_status: document.getElementById('budgetStatus').value || null,
            sub_portfolio: document.getElementById('subPortfolio').value || null,
            top_level_portfolio: document.getElementById('topLevelPortfolio').value || null,
            technology_portfolio_leader: document.getElementById('technologyLeader').value || null,
            business_owner: document.getElementById('businessOwner').value || null,
            owner: document.getElementById('owner').value || null,
            start_date: document.getElementById('startDate').value || null,
            due_date: document.getElementById('dueDate').value || null,
            actual_start_date: document.getElementById('actualStartDate').value || null,
            project_manager: document.getElementById('projectManager').value || null,
            esa_id: document.getElementById('esaId').value || null,
            budget_amount: parseFloat(document.getElementById('budget').value) || null,
            percent_complete: parseInt(document.getElementById('percentComplete').value) || 0
        };
        
        const response = await fetch('/api/v1/projects/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const newProject = await response.json();
        console.log('✅ Project created:', newProject);
        
        // Close modal and refresh
        bootstrap.Modal.getInstance(document.getElementById('createProjectModal')).hide();
        document.getElementById('createProjectForm').reset();
        loadProjects();
        
        showSuccess('Project created successfully!');
        
    } catch (error) {
        console.error('❌ Error creating project:', error);
        showError('Failed to create project: ' + error.message);
    }
}

/**
 * Edit project
 */
function editProject(projectId) {
    const project = projectsData.find(p => p.id === projectId);
    if (!project) return;
    
    // Populate edit form
    document.getElementById('editProjectId').value = project.id;
    document.getElementById('editProjectName').value = project.name || '';
    // ... populate other fields
    
    const modal = new bootstrap.Modal(document.getElementById('editProjectModal'));
    modal.show();
}

/**
 * Update project
 */
async function updateProject() {
    try {
        const projectId = document.getElementById('editProjectId').value;
        const formData = {
            name: document.getElementById('editProjectName').value,
            // ... other fields
        };
        
        const response = await fetch(`/api/v1/projects/${projectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        bootstrap.Modal.getInstance(document.getElementById('editProjectModal')).hide();
        loadProjects();
        showSuccess('Project updated successfully!');
        
    } catch (error) {
        console.error('❌ Error updating project:', error);
        showError('Failed to update project: ' + error.message);
    }
}

/**
 * View project details
 */
function viewProject(projectId) {
    window.location.href = `/projects/${projectId}`;
}

/**
 * Delete project
 */
async function deleteProject(projectId) {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/v1/projects/${projectId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        loadProjects();
        showSuccess('Project deleted successfully!');
        
    } catch (error) {
        console.error('❌ Error deleting project:', error);
        showError('Failed to delete project: ' + error.message);
    }
}

/**
 * Duplicate project
 */
async function duplicateProject(projectId) {
    const project = projectsData.find(p => p.id === projectId);
    if (!project) return;
    
    try {
        const duplicateData = {
            ...project,
            name: `${project.name} (Copy)`,
            project_id: `${project.project_id}_COPY`,
            percent_complete: 0,
            id: undefined
        };
        
        const response = await fetch('/api/v1/projects/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(duplicateData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        loadProjects();
        showSuccess('Project duplicated successfully!');
        
    } catch (error) {
        console.error('❌ Error duplicating project:', error);
        showError('Failed to duplicate project: ' + error.message);
    }
}

/**
 * Export project
 */
function exportProject(projectId) {
    const project = projectsData.find(p => p.id === projectId);
    if (!project) return;
    
    const dataStr = JSON.stringify(project, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `project_${project.project_id || project.id}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Export all projects
 */
function exportProjects() {
    const dataStr = JSON.stringify(projectsData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `projects_export_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Import projects
 */
function importProjects() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            const text = await file.text();
            const projects = JSON.parse(text);
            
            // Import projects
            for (const project of projects) {
                await fetch('/api/v1/projects/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(project)
                });
            }
            
            loadProjects();
            showSuccess('Projects imported successfully!');
            
        } catch (error) {
            console.error('❌ Error importing projects:', error);
            showError('Failed to import projects: ' + error.message);
        }
    };
    
    input.click();
}

/**
 * Refresh projects
 */
function refreshProjects() {
    loadProjects();
}

/**
 * Toggle project selection
 */
function toggleProjectSelection(projectId) {
    if (selectedProjects.has(projectId)) {
        selectedProjects.delete(projectId);
    } else {
        selectedProjects.add(projectId);
    }
    
    updateBulkActions();
}

/**
 * Toggle select all
 */
function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.project-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
        const projectId = parseInt(checkbox.value);
        
        if (selectAll.checked) {
            selectedProjects.add(projectId);
        } else {
            selectedProjects.delete(projectId);
        }
    });
    
    updateBulkActions();
}

/**
 * Update bulk actions
 */
function updateBulkActions() {
    const selectedCount = document.getElementById('selectedCount');
    if (selectedCount) {
        selectedCount.textContent = selectedProjects.size;
    }
}

/**
 * Bulk update status
 */
function bulkUpdateStatus() {
    if (selectedProjects.size === 0) return;
    
    const newStatus = prompt('Enter new status (Active, Completed, At Risk, Off Track):');
    if (!newStatus) return;
    
    // Implementation for bulk status update
    console.log('Bulk update status:', newStatus, selectedProjects);
}

/**
 * Bulk update priority
 */
function bulkUpdatePriority() {
    if (selectedProjects.size === 0) return;
    
    const newPriority = prompt('Enter new priority (Low, Medium, High, Critical):');
    if (!newPriority) return;
    
    // Implementation for bulk priority update
    console.log('Bulk update priority:', newPriority, selectedProjects);
}

/**
 * Bulk assign manager
 */
function bulkAssignManager() {
    if (selectedProjects.size === 0) return;
    
    const newManager = prompt('Enter manager name:');
    if (!newManager) return;
    
    // Implementation for bulk manager assignment
    console.log('Bulk assign manager:', newManager, selectedProjects);
}

/**
 * Bulk delete projects
 */
function bulkDeleteProjects() {
    if (selectedProjects.size === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedProjects.size} projects? This action cannot be undone.`)) {
        return;
    }
    
    // Implementation for bulk delete
    console.log('Bulk delete projects:', selectedProjects);
}

// Utility functions
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
}

function getDateClass(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const today = new Date();
    const diffTime = date - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'text-danger';
    if (diffDays <= 7) return 'text-warning';
    return 'text-success';
}

function getProgressBarClass(percent) {
    if (percent >= 100) return 'bg-success';
    if (percent >= 75) return 'bg-info';
    if (percent >= 50) return 'bg-primary';
    if (percent >= 25) return 'bg-warning';
    return 'bg-danger';
}

function showLoading(show) {
    const tbody = document.getElementById('projectsTableBody');
    if (show) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading projects...</p>
                </td>
            </tr>
        `;
    }
}

function showError(message) {
    // Show error message
    console.error(message);
    alert('Error: ' + message);
}

function showSuccess(message) {
    // Show success message
    console.log(message);
    alert('Success: ' + message);
}

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

// Export functions for global access
window.loadProjects = loadProjects;
window.searchProjects = searchProjects;
window.filterProjects = filterProjects;
window.sortProjects = sortProjects;
window.clearFilters = clearFilters;
window.toggleView = toggleView;
window.showCreateProjectModal = showCreateProjectModal;
window.createProject = createProject;
window.editProject = editProject;
window.updateProject = updateProject;
window.viewProject = viewProject;
window.deleteProject = deleteProject;
window.duplicateProject = duplicateProject;
window.exportProject = exportProject;
window.exportProjects = exportProjects;
window.importProjects = importProjects;
window.refreshProjects = refreshProjects;
window.toggleProjectSelection = toggleProjectSelection;
window.toggleSelectAll = toggleSelectAll;
window.bulkUpdateStatus = bulkUpdateStatus;
window.bulkUpdatePriority = bulkUpdatePriority;
window.bulkAssignManager = bulkAssignManager;
window.bulkDeleteProjects = bulkDeleteProjects;
