/**
 * Comprehensive Backlog Management JavaScript
 * GenAI Metrics Dashboard - Backlog Management Features
 */

// Global variables
let backlogData = [];
let filteredBacklogData = [];
let currentView = 'table';
let sortField = 'name';
let sortDirection = 'asc';
let selectedBacklogItems = new Set();

// Priority and Status mappings
const PRIORITY_MAP = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Critical'
};

const STATUS_MAP = {
    1: 'Not Started',
    2: 'In Progress',
    3: 'Completed',
    4: 'On Hold'
};

const PRIORITY_CLASSES = {
    'Low': 'bg-secondary',
    'Medium': 'bg-info',
    'High': 'bg-warning',
    'Critical': 'bg-danger'
};

const STATUS_CLASSES = {
    'Not Started': 'bg-secondary',
    'In Progress': 'bg-primary',
    'Completed': 'bg-success',
    'On Hold': 'bg-warning'
};

const COMPLEXITY_CLASSES = {
    'Low': 'text-success',
    'Medium': 'text-warning',
    'High': 'text-danger'
};

/**
 * Initialize backlog page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Backlog Management...');
    console.log('🔍 DEBUG: Current URL:', window.location.href);
    console.log('🔍 DEBUG: Backlog table body element:', document.getElementById('backlogTableBody'));
    loadBacklogData();
    setupEventListeners();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('searchBacklog');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchBacklog, 300));
    }

    // Filter functionality
    const priorityFilter = document.getElementById('priorityFilter');
    const statusFilter = document.getElementById('statusFilter');
    const quarterFilter = document.getElementById('quarterFilter');

    if (priorityFilter) priorityFilter.addEventListener('change', filterBacklog);
    if (statusFilter) statusFilter.addEventListener('change', filterBacklog);
    if (quarterFilter) quarterFilter.addEventListener('change', filterBacklog);

    // Select all functionality
    const selectAll = document.getElementById('selectAllBacklog');
    if (selectAll) {
        selectAll.addEventListener('change', toggleSelectAllBacklog);
    }
}

/**
 * Load backlog data from API
 */
async function loadBacklogData() {
    try {
        console.log('📊 Loading backlog data...');
        console.log('🔍 DEBUG: About to fetch from /api/v1/projects/backlog/items');
        showLoading(true);
        
        const response = await fetch('/api/v1/projects/backlog/items');
        console.log('🔍 DEBUG: Response status:', response.status);
        console.log('🔍 DEBUG: Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        backlogData = await response.json();
        console.log('🔍 DEBUG: Backlog data received:', backlogData.length, 'items');
        console.log('🔍 DEBUG: Sample backlog item:', backlogData[0]);
        console.log('🔍 DEBUG: About to call updateStatistics()');
        
        filteredBacklogData = [...backlogData];
        
        updateStatistics();
        console.log('🔍 DEBUG: About to call renderBacklog()');
        renderBacklog();
        
        console.log(`✅ Loaded ${backlogData.length} backlog items`);
        
    } catch (error) {
        console.error('❌ Error loading backlog data:', error);
        showError('Failed to load backlog data: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Update statistics cards
 */
function updateStatistics() {
    const stats = {
        total: backlogData.length,
        highPriority: backlogData.filter(item => PRIORITY_MAP[item.priority_id] === 'High' || PRIORITY_MAP[item.priority_id] === 'Critical').length,
        inProgress: backlogData.filter(item => STATUS_MAP[item.status_id] === 'In Progress').length,
        completed: backlogData.filter(item => STATUS_MAP[item.status_id] === 'Completed').length
    };
    
    document.getElementById('total-backlog').textContent = stats.total;
    document.getElementById('high-priority').textContent = stats.highPriority;
    document.getElementById('in-progress').textContent = stats.inProgress;
    document.getElementById('completed').textContent = stats.completed;
}

/**
 * Render backlog based on current view
 */
function renderBacklog() {
    console.log('🔍 DEBUG: renderBacklog called, currentView:', currentView);
    console.log('🔍 DEBUG: filteredBacklogData length:', filteredBacklogData.length);
    if (currentView === 'table') {
        console.log('🔍 DEBUG: Rendering table view');
        renderTableView();
    } else {
        console.log('🔍 DEBUG: Rendering kanban view');
        renderKanbanView();
    }
}

/**
 * Render table view
 */
function renderTableView() {
    console.log('🔍 DEBUG: renderTableView called');
    console.log('🎨 Rendering table view with', filteredBacklogData.length, 'items');
    const tbody = document.getElementById('backlogTableBody');
    console.log('🔍 DEBUG: Table body element:', tbody);
    
    if (!tbody) {
        console.error('❌ Table body element not found');
        return;
    }
    
    if (filteredBacklogData.length === 0) {
        console.log('📭 No backlog items to display');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="fas fa-search fa-2x mb-2"></i>
                    <p>No backlog items found matching your criteria</p>
                </td>
            </tr>
        `;
        return;
    }

    console.log('🔍 DEBUG: About to render', filteredBacklogData.length, 'backlog items');
    const htmlContent = filteredBacklogData.map(item => {
        const priorityName = PRIORITY_MAP[item.priority_id] || 'Unknown';
        const statusName = STATUS_MAP[item.status_id] || 'Unknown';
        const effort = item.effort_estimate || 0;
        
        console.log('🔍 DEBUG: Rendering item:', item.id, item.name);
        
        return `
        <tr>
            <td>
                <input type="checkbox" class="form-check-input backlog-checkbox" 
                       value="${item.id}" onchange="toggleBacklogSelection(${item.id})">
            </td>
            <td>
                <div class="backlog-name">
                    <strong>${item.name || 'Unnamed Item'}</strong>
                    ${item.description ? `<br><small class="text-muted">${truncateText(item.description, 60)}</small>` : ''}
                </div>
            </td>
            <td>
                <span class="badge ${PRIORITY_CLASSES[priorityName] || 'bg-secondary'}">
                    ${priorityName}
                </span>
            </td>
            <td>
                <span class="badge ${STATUS_CLASSES[statusName] || 'bg-secondary'}">
                    ${statusName}
                </span>
            </td>
            <td>
                <span class="${COMPLEXITY_CLASSES[item.complexity] || 'text-muted'}">
                    ${item.complexity || 'N/A'}
                </span>
            </td>
            <td>
                <span class="badge bg-info">${effort} pts</span>
            </td>
            <td>
                ${item.target_quarter || 'N/A'}
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewBacklogItem(${item.id})" 
                            title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-secondary" onclick="editBacklogItem(${item.id})" 
                            title="Edit Item">
                        <i class="fas fa-edit"></i>
                    </button>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-secondary dropdown-toggle" 
                                data-bs-toggle="dropdown" title="More Actions">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="moveToSprint(${item.id})">
                                <i class="fas fa-calendar-plus me-2"></i>Add to Sprint
                            </a></li>
                            <li><a class="dropdown-item" href="#" onclick="duplicateBacklogItem(${item.id})">
                                <i class="fas fa-copy me-2"></i>Duplicate
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="deleteBacklogItem(${item.id})">
                                <i class="fas fa-trash me-2"></i>Delete
                            </a></li>
                        </ul>
                    </div>
                </div>
            </td>
        </tr>
        `;
    }).join('');
    
    console.log('🔍 DEBUG: Generated HTML length:', htmlContent.length);
    console.log('🔍 DEBUG: Sample HTML:', htmlContent.substring(0, 500));
    console.log('🔍 DEBUG: About to set innerHTML');
    
    tbody.innerHTML = htmlContent;
    console.log('🔍 DEBUG: innerHTML set, table body children count:', tbody.children.length);
}

/**
 * Render kanban view
 */
function renderKanbanView() {
    const statusColumns = {
        'Not Started': document.getElementById('kanban-not-started'),
        'In Progress': document.getElementById('kanban-in-progress'),
        'On Hold': document.getElementById('kanban-on-hold'),
        'Completed': document.getElementById('kanban-completed')
    };

    // Clear all columns
    Object.values(statusColumns).forEach(column => {
        if (column) column.innerHTML = '';
    });

    // Group items by status
    const groupedItems = {};
    Object.keys(STATUS_MAP).forEach(statusId => {
        groupedItems[STATUS_MAP[statusId]] = [];
    });

    filteredBacklogData.forEach(item => {
        const statusName = STATUS_MAP[item.status_id] || 'Not Started';
        if (groupedItems[statusName]) {
            groupedItems[statusName].push(item);
        }
    });

    // Render items in each column
    Object.entries(groupedItems).forEach(([status, items]) => {
        const column = statusColumns[status];
        if (!column) return;

        if (items.length === 0) {
            column.innerHTML = '<p class="text-muted text-center">No items</p>';
            return;
        }

        column.innerHTML = items.map(item => {
            const priorityName = PRIORITY_MAP[item.priority_id] || 'Unknown';
            const effort = item.effort_estimate || 0;
            
            return `
            <div class="card mb-2" draggable="true" data-item-id="${item.id}">
                <div class="card-body p-2">
                    <h6 class="card-title mb-1">${item.name || 'Unnamed Item'}</h6>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge ${PRIORITY_CLASSES[priorityName] || 'bg-secondary'}">${priorityName}</span>
                        <span class="badge bg-info">${effort} pts</span>
                    </div>
                    <p class="card-text small text-muted">${truncateText(item.description || '', 50)}</p>
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">${item.target_quarter || 'No quarter'}</small>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-sm" onclick="editBacklogItem(${item.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            `;
        }).join('');
    });
}

/**
 * Search backlog items
 */
function searchBacklog() {
    const searchTerm = document.getElementById('searchBacklog').value.toLowerCase();
    
    filteredBacklogData = backlogData.filter(item => {
        const name = (item.name || '').toLowerCase();
        const description = (item.description || '').toLowerCase();
        const userStory = (item.user_story || '').toLowerCase();
        const businessValue = (item.business_value || '').toLowerCase();
        
        return name.includes(searchTerm) || 
               description.includes(searchTerm) || 
               userStory.includes(searchTerm) || 
               businessValue.includes(searchTerm);
    });
    
    renderBacklog();
}

/**
 * Filter backlog items
 */
function filterBacklog() {
    const priorityFilter = document.getElementById('priorityFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const quarterFilter = document.getElementById('quarterFilter').value;
    
    filteredBacklogData = backlogData.filter(item => {
        const priorityMatch = !priorityFilter || item.priority_id == priorityFilter;
        const statusMatch = !statusFilter || item.status_id == statusFilter;
        const quarterMatch = !quarterFilter || item.target_quarter === quarterFilter;
        
        return priorityMatch && statusMatch && quarterMatch;
    });
    
    renderBacklog();
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('searchBacklog').value = '';
    document.getElementById('priorityFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('quarterFilter').value = '';
    
    filteredBacklogData = [...backlogData];
    renderBacklog();
}

/**
 * Sort backlog items
 */
function sortBacklog(field) {
    if (sortField === field) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortField = field;
        sortDirection = 'asc';
    }
    
    filteredBacklogData.sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];
        
        // Handle priority and status sorting
        if (field === 'priority_id') {
            aVal = PRIORITY_MAP[a.priority_id] || '';
            bVal = PRIORITY_MAP[b.priority_id] || '';
        } else if (field === 'status_id') {
            aVal = STATUS_MAP[a.status_id] || '';
            bVal = STATUS_MAP[b.status_id] || '';
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
    
    renderBacklog();
}

/**
 * Toggle view between table and kanban
 */
function toggleView(view) {
    currentView = view;
    
    const tableView = document.getElementById('tableView');
    const kanbanView = document.getElementById('kanbanView');
    
    if (view === 'table') {
        tableView.style.display = 'block';
        kanbanView.style.display = 'none';
    } else {
        tableView.style.display = 'none';
        kanbanView.style.display = 'block';
    }
    
    renderBacklog();
}

/**
 * Show create backlog modal
 */
function showCreateBacklogModal() {
    const modal = new bootstrap.Modal(document.getElementById('createBacklogModal'));
    modal.show();
}

/**
 * Create new backlog item
 */
async function createBacklogItem() {
    try {
        const formData = {
            name: document.getElementById('backlogName').value,
            backlog_id: document.getElementById('backlogId').value || null,
            description: document.getElementById('backlogDescription').value || null,
            priority_id: parseInt(document.getElementById('backlogPriority').value),
            status_id: parseInt(document.getElementById('backlogStatus').value),
            complexity: document.getElementById('backlogComplexity').value || null,
            effort_estimate: parseFloat(document.getElementById('backlogEffort').value) || null,
            target_quarter: document.getElementById('backlogQuarter').value || null,
            planned_start_date: document.getElementById('backlogStartDate').value || null,
            user_story: document.getElementById('backlogUserStory').value || null,
            acceptance_criteria: document.getElementById('backlogAcceptanceCriteria').value || null,
            business_value: document.getElementById('backlogBusinessValue').value || null
        };
        
        const response = await fetch('/api/v1/projects/backlog/items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const newItem = await response.json();
        console.log('✅ Backlog item created:', newItem);
        
        // Close modal and refresh
        bootstrap.Modal.getInstance(document.getElementById('createBacklogModal')).hide();
        document.getElementById('createBacklogForm').reset();
        loadBacklogData();
        
        showSuccess('Backlog item created successfully!');
        
    } catch (error) {
        console.error('❌ Error creating backlog item:', error);
        showError('Failed to create backlog item: ' + error.message);
    }
}

/**
 * Show sprint planning modal
 */
function showSprintPlanningModal() {
    const modal = new bootstrap.Modal(document.getElementById('sprintPlanningModal'));
    modal.show();
    loadAvailableBacklogItems();
}

/**
 * Load available backlog items for sprint planning
 */
async function loadAvailableBacklogItems() {
    try {
        const availableItems = backlogData.filter(item => 
            STATUS_MAP[item.status_id] === 'Not Started' || 
            STATUS_MAP[item.status_id] === 'In Progress'
        );
        
        const container = document.getElementById('availableBacklogItems');
        container.innerHTML = availableItems.map(item => {
            const priorityName = PRIORITY_MAP[item.priority_id] || 'Unknown';
            const effort = item.effort_estimate || 0;
            
            return `
            <div class="card mb-2" data-item-id="${item.id}">
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="card-title mb-1">${item.name || 'Unnamed Item'}</h6>
                            <div class="d-flex gap-2 mb-2">
                                <span class="badge ${PRIORITY_CLASSES[priorityName] || 'bg-secondary'}">${priorityName}</span>
                                <span class="badge bg-info">${effort} pts</span>
                            </div>
                            <p class="card-text small text-muted">${truncateText(item.description || '', 80)}</p>
                        </div>
                        <button class="btn btn-outline-primary btn-sm" onclick="addToSprint(${item.id})">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('❌ Error loading available items:', error);
    }
}

/**
 * Add item to sprint
 */
function addToSprint(itemId) {
    const item = backlogData.find(i => i.id === itemId);
    if (!item) return;
    
    const selectedContainer = document.getElementById('selectedSprintItems');
    const priorityName = PRIORITY_MAP[item.priority_id] || 'Unknown';
    const effort = item.effort_estimate || 0;
    
    const itemElement = document.createElement('div');
    itemElement.className = 'card mb-2';
    itemElement.setAttribute('data-item-id', itemId);
    itemElement.innerHTML = `
        <div class="card-body p-2">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="card-title mb-1">${item.name || 'Unnamed Item'}</h6>
                    <div class="d-flex gap-2 mb-2">
                        <span class="badge ${PRIORITY_CLASSES[priorityName] || 'bg-secondary'}">${priorityName}</span>
                        <span class="badge bg-info">${effort} pts</span>
                    </div>
                </div>
                <button class="btn btn-outline-danger btn-sm" onclick="removeFromSprint(${itemId})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    
    selectedContainer.appendChild(itemElement);
    
    // Remove from available items
    const availableItem = document.querySelector(`[data-item-id="${itemId}"]`);
    if (availableItem) {
        availableItem.remove();
    }
}

/**
 * Remove item from sprint
 */
function removeFromSprint(itemId) {
    const selectedItem = document.querySelector(`#selectedSprintItems [data-item-id="${itemId}"]`);
    if (selectedItem) {
        selectedItem.remove();
    }
    
    // Add back to available items
    loadAvailableBacklogItems();
}

/**
 * Create sprint
 */
async function createSprint() {
    const sprintName = document.getElementById('sprintName').value;
    const sprintCapacity = parseInt(document.getElementById('sprintCapacity').value);
    
    if (!sprintName) {
        showError('Please enter a sprint name');
        return;
    }
    
    const selectedItems = Array.from(document.querySelectorAll('#selectedSprintItems [data-item-id]'))
        .map(el => parseInt(el.getAttribute('data-item-id')));
    
    if (selectedItems.length === 0) {
        showError('Please select at least one item for the sprint');
        return;
    }
    
    // Calculate total effort
    const totalEffort = selectedItems.reduce((total, itemId) => {
        const item = backlogData.find(i => i.id === itemId);
        return total + (item?.effort_estimate || 0);
    }, 0);
    
    if (totalEffort > sprintCapacity) {
        showError(`Total effort (${totalEffort} pts) exceeds sprint capacity (${sprintCapacity} pts)`);
        return;
    }
    
    try {
        // Here you would typically create a sprint record
        console.log('Creating sprint:', { sprintName, sprintCapacity, selectedItems, totalEffort });
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('sprintPlanningModal')).hide();
        
        showSuccess(`Sprint "${sprintName}" created with ${selectedItems.length} items (${totalEffort} story points)`);
        
    } catch (error) {
        console.error('❌ Error creating sprint:', error);
        showError('Failed to create sprint: ' + error.message);
    }
}

/**
 * Toggle backlog item selection
 */
function toggleBacklogSelection(itemId) {
    if (selectedBacklogItems.has(itemId)) {
        selectedBacklogItems.delete(itemId);
    } else {
        selectedBacklogItems.add(itemId);
    }
}

/**
 * Toggle select all backlog items
 */
function toggleSelectAllBacklog() {
    const selectAll = document.getElementById('selectAllBacklog');
    const checkboxes = document.querySelectorAll('.backlog-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
        const itemId = parseInt(checkbox.value);
        
        if (selectAll.checked) {
            selectedBacklogItems.add(itemId);
        } else {
            selectedBacklogItems.delete(itemId);
        }
    });
}

/**
 * Utility functions
 */
function showLoading(show) {
    // Implementation for showing/hiding loading state
}

function showError(message) {
    // Implementation for showing error messages
    console.error(message);
}

function showSuccess(message) {
    // Implementation for showing success messages
    console.log(message);
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
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

// Placeholder functions for future implementation
function viewBacklogItem(itemId) {
    console.log('🔍 DEBUG: View backlog item:', itemId);
    const item = backlogData.find(i => i.id === itemId);
    if (item) {
        alert(`Viewing Item: ${item.name}\nDescription: ${item.description || 'No description'}\nPriority: ${PRIORITY_MAP[item.priority_id] || 'Unknown'}\nStatus: ${STATUS_MAP[item.status_id] || 'Unknown'}`);
    } else {
        alert('Item not found!');
    }
}

function editBacklogItem(itemId) {
    console.log('🔍 DEBUG: Edit backlog item:', itemId);
    const item = backlogData.find(i => i.id === itemId);
    if (item) {
        // For now, show an alert with edit form
        const newName = prompt('Edit item name:', item.name || '');
        if (newName !== null && newName !== item.name) {
            // In a real app, this would make an API call
            item.name = newName;
            renderBacklog();
            alert('Item updated! (This is a demo - changes are not saved)');
        }
    } else {
        alert('Item not found!');
    }
}

function deleteBacklogItem(itemId) {
    console.log('🔍 DEBUG: Delete backlog item:', itemId);
    const item = backlogData.find(i => i.id === itemId);
    if (item) {
        if (confirm(`Are you sure you want to delete "${item.name}"?`)) {
            // In a real app, this would make an API call
            const index = backlogData.findIndex(i => i.id === itemId);
            if (index > -1) {
                backlogData.splice(index, 1);
                filteredBacklogData = backlogData.filter(i => i.id !== itemId);
                renderBacklog();
                updateStatistics();
                alert('Item deleted! (This is a demo - changes are not saved)');
            }
        }
    } else {
        alert('Item not found!');
    }
}

function duplicateBacklogItem(itemId) {
    console.log('🔍 DEBUG: Duplicate backlog item:', itemId);
    const item = backlogData.find(i => i.id === itemId);
    if (item) {
        // Create a copy with a new ID
        const newItem = {
            ...item,
            id: Math.max(...backlogData.map(i => i.id)) + 1,
            name: item.name + ' (Copy)',
            status_id: 1 // Not Started
        };
        backlogData.push(newItem);
        filteredBacklogData = [...backlogData];
        renderBacklog();
        updateStatistics();
        alert('Item duplicated! (This is a demo - changes are not saved)');
    } else {
        alert('Item not found!');
    }
}

function moveToSprint(itemId) {
    console.log('🔍 DEBUG: Move to sprint:', itemId);
    const item = backlogData.find(i => i.id === itemId);
    if (item) {
        alert(`Moving "${item.name}" to sprint...\n(This is a demo - sprint planning not implemented yet)`);
    } else {
        alert('Item not found!');
    }
}

function exportBacklog() {
    console.log('Export backlog');
}

// Make functions globally available
window.showCreateBacklogModal = showCreateBacklogModal;
window.showSprintPlanningModal = showSprintPlanningModal;
window.createBacklogItem = createBacklogItem;
window.addToSprint = addToSprint;
window.removeFromSprint = removeFromSprint;
window.createSprint = createSprint;
window.toggleBacklogSelection = toggleBacklogSelection;
window.toggleSelectAllBacklog = toggleSelectAllBacklog;
window.searchBacklog = searchBacklog;
window.filterBacklog = filterBacklog;
window.clearFilters = clearFilters;
window.sortBacklog = sortBacklog;
window.toggleView = toggleView;
window.viewBacklogItem = viewBacklogItem;
window.editBacklogItem = editBacklogItem;
window.deleteBacklogItem = deleteBacklogItem;
window.duplicateBacklogItem = duplicateBacklogItem;
window.moveToSprint = moveToSprint;
window.exportBacklog = exportBacklog;
