/**
 * Work Plan JavaScript - Gantt Chart and Task Management
 * Professional project management with timeline visualization
 */

// Work Plan State Management
let workPlanState = {
    tasks: [],
    selectedTasks: [],
    currentZoom: 100,
    currentView: 'standard',
    timelineStart: new Date('2021-11-01'),
    timelineEnd: new Date('2023-12-31'),
    currentDate: new Date()
};

// Sample task data (matching the screenshot)
const sampleTasks = [
    {
        id: 'M-16401',
        name: 'Product Setup',
        status: 'completed',
        deliverable: true,
        startDate: new Date('2022-01-01'),
        endDate: new Date('2022-03-31'),
        progress: 100,
        type: 'milestone'
    },
    {
        id: 'M-17201',
        name: 'Configuration',
        status: 'completed',
        deliverable: true,
        startDate: new Date('2022-01-01'),
        endDate: new Date('2022-03-31'),
        progress: 100,
        type: 'milestone'
    },
    {
        id: 'M-17202',
        name: 'Training Core team, EA, SA, BA',
        status: 'completed',
        deliverable: true,
        startDate: new Date('2022-01-01'),
        endDate: new Date('2022-03-31'),
        progress: 100,
        type: 'milestone'
    },
    {
        id: 'T-26004',
        name: 'Self Training - User Set 1',
        status: 'completed',
        deliverable: true,
        startDate: new Date('2022-01-01'),
        endDate: new Date('2022-03-31'),
        progress: 100,
        type: 'task',
        highlighted: true
    },
    {
        id: 'T-26006',
        name: 'Instructor Led Training - Admin',
        status: 'planned',
        deliverable: false,
        startDate: new Date('2022-04-01'),
        endDate: new Date('2022-06-30'),
        progress: 0,
        type: 'task'
    },
    {
        id: 'T-26007',
        name: 'Instructor Led Training - Users Set 1',
        status: 'planned',
        deliverable: false,
        startDate: new Date('2022-04-01'),
        endDate: new Date('2022-06-30'),
        progress: 0,
        type: 'task'
    },
    {
        id: 'M-25301',
        name: 'Load Foundation data - Apps Inventory & Bi',
        status: 'completed',
        deliverable: true,
        startDate: new Date('2022-04-01'),
        endDate: new Date('2022-06-30'),
        progress: 100,
        type: 'milestone'
    },
    {
        id: 'T-83301',
        name: 'Top-down view - Click Through Approach fr',
        status: 'in-progress',
        deliverable: false,
        startDate: new Date('2022-07-01'),
        endDate: new Date('2022-09-30'),
        progress: 95,
        type: 'task'
    },
    {
        id: 'M-17203',
        name: 'Pilot - 1 Transformation program (Skill Reinv',
        status: 'in-progress',
        deliverable: true,
        startDate: new Date('2022-10-01'),
        endDate: new Date('2022-12-31'),
        progress: 54,
        type: 'milestone'
    }
];

/**
 * Initialize Work Plan
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('📋 Initializing Work Plan...');
    
    // Initialize work plan state
    try {
        const projectIdEl = document.getElementById('workPlanProjectId');
        const projectId = projectIdEl ? projectIdEl.value : null;
        if (projectId) {
            const res = await fetch(`/api/v1/projects/${projectId}/tasks`, { credentials: 'include' });
            if (res.ok) {
                const tasks = await res.json();
                workPlanState.tasks = tasks.map(t => ({
                    id: String(t.id),
                    name: t.task_name,
                    status: (t.status && t.status.name) ? t.status.name.toLowerCase().replace(' ', '-') : (t.percent_complete >= 100 ? 'completed' : 'in-progress'),
                    deliverable: false,
                    startDate: t.start_date ? new Date(t.start_date) : new Date('2022-01-01'),
                    endDate: t.due_date ? new Date(t.due_date) : new Date('2022-03-31'),
                    progress: Number(t.percent_complete || 0),
                    type: 'task'
                }));
            } else {
                console.warn('Falling back to sample tasks; API returned', res.status);
                workPlanState.tasks = [...sampleTasks];
            }
        } else {
            workPlanState.tasks = [...sampleTasks];
        }
    } catch (e) {
        console.error('Failed loading tasks, using samples', e);
        workPlanState.tasks = [...sampleTasks];
    }
    
    // Load work plan data
    loadWorkPlanData();
    
    // Initialize timeline
    initializeTimeline();
    
    // Render task list
    renderTaskList();
    
    // Render Gantt chart
    renderGanttChart();
    
    console.log('✅ Work Plan initialized successfully');
});

/**
 * Load work plan data
 */
function loadWorkPlanData() {
    console.log('📊 Loading work plan data...');
    
    // In a real application, this would fetch from API
    // For now, we use sample data
    
    // Sort tasks by start date
    workPlanState.tasks.sort((a, b) => a.startDate - b.startDate);
    
    console.log(`📋 Loaded ${workPlanState.tasks.length} tasks`);
}

/**
 * Initialize timeline
 */
function initializeTimeline() {
    console.log('📅 Initializing timeline...');
    
    const timelineElement = document.getElementById('ganttTimeline');
    if (!timelineElement) return;
    
    // Generate timeline periods
    const periods = generateTimelinePeriods();
    
    timelineElement.innerHTML = periods.map(period => `
        <div class="gantt-period ${period.type}" style="min-width: ${period.width}px;">
            ${period.label}
        </div>
    `).join('');
}

/**
 * Generate timeline periods
 */
function generateTimelinePeriods() {
    const periods = [];
    const startYear = 2021;
    const endYear = 2023;
    
    for (let year = startYear; year <= endYear; year++) {
        // Year header
        periods.push({
            type: 'year',
            label: year.toString(),
            width: 400
        });
        
        // Quarters
        for (let quarter = 1; quarter <= 4; quarter++) {
            const quarterLabel = `Q${quarter} ${year}`;
            periods.push({
                type: 'quarter',
                label: quarterLabel,
                width: 100
            });
            
            // Months in quarter
            const monthsInQuarter = [
                ['Jan', 'Feb', 'Mar'],
                ['Apr', 'May', 'Jun'],
                ['Jul', 'Aug', 'Sep'],
                ['Oct', 'Nov', 'Dec']
            ];
            
            monthsInQuarter[quarter - 1].forEach(month => {
                periods.push({
                    type: 'month',
                    label: month,
                    width: 33
                });
            });
        }
    }
    
    return periods;
}

/**
 * Render task list
 */
function renderTaskList() {
    console.log('📋 Rendering task list...');
    
    const taskListElement = document.getElementById('taskList');
    if (!taskListElement) return;
    
    taskListElement.innerHTML = workPlanState.tasks.map(task => `
        <div class="task-row ${task.highlighted ? 'selected' : ''}" data-task-id="${task.id}" onclick="selectTask('${task.id}')">
            <div class="col task-id">${task.id}</div>
            <div class="col task-status">
                <span class="status-dot status-${getStatusColor(task.status)}"></span>
            </div>
            <div class="col task-deliverable">
                ${task.deliverable ? '<i class="fas fa-check text-success"></i>' : ''}
            </div>
            <div class="col task-name">${task.name}</div>
        </div>
    `).join('');
}

/**
 * Render Gantt chart
 */
function renderGanttChart() {
    console.log('📊 Rendering Gantt chart...');
    
    const ganttTasksElement = document.getElementById('ganttTasks');
    if (!ganttTasksElement) return;
    
    // Clear existing content
    ganttTasksElement.innerHTML = '';
    
    // Render each task
    workPlanState.tasks.forEach((task, index) => {
        const taskElement = createTaskBar(task, index);
        ganttTasksElement.appendChild(taskElement);
    });
    
    // Generate grid lines
    generateGridLines();
}

/**
 * Create task bar element
 */
function createTaskBar(task, index) {
    const taskElement = document.createElement('div');
    taskElement.className = `gantt-task ${task.status}`;
    taskElement.style.top = `${index * 34}px`;
    taskElement.style.left = `${calculateTaskPosition(task.startDate)}px`;
    taskElement.style.width = `${calculateTaskWidth(task.startDate, task.endDate)}px`;
    taskElement.setAttribute('data-task-id', task.id);
    taskElement.onclick = () => selectTask(task.id);
    
    // Add progress indicator
    if (task.progress > 0) {
        const progressElement = document.createElement('div');
        progressElement.className = 'task-progress';
        progressElement.textContent = `${task.progress}%`;
        taskElement.appendChild(progressElement);
    }
    
    // Add task name
    const nameElement = document.createElement('span');
    nameElement.textContent = task.name;
    nameElement.style.fontSize = '11px';
    nameElement.style.overflow = 'hidden';
    nameElement.style.textOverflow = 'ellipsis';
    nameElement.style.whiteSpace = 'nowrap';
    taskElement.appendChild(nameElement);
    
    return taskElement;
}

/**
 * Calculate task position on timeline
 */
function calculateTaskPosition(startDate) {
    const timelineStart = workPlanState.timelineStart;
    const daysDiff = Math.floor((startDate - timelineStart) / (1000 * 60 * 60 * 24));
    return daysDiff * (workPlanState.currentZoom / 100) * 2; // 2px per day at 100% zoom
}

/**
 * Calculate task width
 */
function calculateTaskWidth(startDate, endDate) {
    const daysDiff = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
    return daysDiff * (workPlanState.currentZoom / 100) * 2; // 2px per day at 100% zoom
}

/**
 * Generate grid lines
 */
function generateGridLines() {
    const gridElement = document.getElementById('ganttGrid');
    if (!gridElement) return;
    
    gridElement.innerHTML = '';
    
    // Generate vertical grid lines for months
    const months = generateMonthPositions();
    months.forEach(position => {
        const line = document.createElement('div');
        line.className = 'gantt-grid-line';
        line.style.left = `${position}px`;
        gridElement.appendChild(line);
    });
}

/**
 * Generate month positions for grid lines
 */
function generateMonthPositions() {
    const positions = [];
    const startDate = workPlanState.timelineStart;
    const endDate = workPlanState.timelineEnd;
    
    let currentDate = new Date(startDate);
    while (currentDate <= endDate) {
        const position = calculateTaskPosition(currentDate);
        positions.push(position);
        
        // Move to next month
        currentDate.setMonth(currentDate.getMonth() + 1);
    }
    
    return positions;
}

/**
 * Get status color class
 */
function getStatusColor(status) {
    const colors = {
        'completed': 'green',
        'in-progress': 'blue',
        'planned': 'orange',
        'overdue': 'red'
    };
    return colors[status] || 'blue';
}

/**
 * Select task
 */
function selectTask(taskId) {
    console.log(`🎯 Selecting task: ${taskId}`);
    
    // Remove previous selection
    document.querySelectorAll('.task-row.selected').forEach(row => {
        row.classList.remove('selected');
    });
    
    // Add selection to clicked task
    const taskRow = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskRow) {
        taskRow.classList.add('selected');
    }
    
    // Update selected tasks
    workPlanState.selectedTasks = [taskId];
    
    // Highlight corresponding Gantt bar
    highlightGanttTask(taskId);
}

/**
 * Highlight Gantt task
 */
function highlightGanttTask(taskId) {
    // Remove previous highlights
    document.querySelectorAll('.gantt-task').forEach(task => {
        task.style.border = 'none';
    });
    
    // Highlight selected task
    const ganttTask = document.querySelector(`.gantt-task[data-task-id="${taskId}"]`);
    if (ganttTask) {
        ganttTask.style.border = '2px solid #ff6b6b';
        ganttTask.style.boxShadow = '0 0 10px rgba(255, 107, 107, 0.5)';
    }
}

/**
 * Search tasks
 */
function searchTasks(searchTerm) {
    console.log(`🔍 Searching tasks: ${searchTerm}`);
    
    if (!searchTerm) {
        // Show all tasks
        document.querySelectorAll('.task-row').forEach(row => {
            row.style.display = 'flex';
        });
        return;
    }
    
    // Filter tasks
    document.querySelectorAll('.task-row').forEach(row => {
        const taskId = row.querySelector('.task-id').textContent;
        const taskName = row.querySelector('.task-name').textContent;
        
        if (taskId.toLowerCase().includes(searchTerm.toLowerCase()) || 
            taskName.toLowerCase().includes(searchTerm.toLowerCase())) {
            row.style.display = 'flex';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Zoom functions
 */
function zoomIn() {
    workPlanState.currentZoom = Math.min(workPlanState.currentZoom + 25, 200);
    updateZoom();
}

function zoomOut() {
    workPlanState.currentZoom = Math.max(workPlanState.currentZoom - 25, 50);
    updateZoom();
}

function zoomChange(value) {
    workPlanState.currentZoom = parseInt(value);
    updateZoom();
}

function updateZoom() {
    console.log(`🔍 Updating zoom to ${workPlanState.currentZoom}%`);
    
    // Update zoom slider
    const zoomSlider = document.querySelector('.zoom-slider');
    if (zoomSlider) {
        zoomSlider.value = workPlanState.currentZoom;
    }
    
    // Re-render Gantt chart with new zoom
    renderGanttChart();
}

/**
 * Fit to screen
 */
function fitToScreen() {
    console.log('📐 Fitting to screen...');
    
    const ganttPanel = document.querySelector('.gantt-panel');
    if (!ganttPanel) return;
    
    const panelWidth = ganttPanel.clientWidth;
    const timelineWidth = 2000; // Approximate timeline width
    
    workPlanState.currentZoom = Math.floor((panelWidth / timelineWidth) * 100);
    updateZoom();
}

/**
 * Export work plan
 */
function exportWorkPlan() {
    console.log('📤 Exporting work plan...');
    
    // Create export data
    const exportData = {
        tasks: workPlanState.tasks,
        exportDate: new Date().toISOString(),
        version: '1.0'
    };
    
    // Create and download file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `work-plan-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Print work plan
 */
function printWorkPlan() {
    console.log('🖨️ Printing work plan...');
    window.print();
}

/**
 * Refresh work plan
 */
function refreshWorkPlan() {
    console.log('🔄 Refreshing work plan...');
    
    // Reload data
    loadWorkPlanData();
    
    // Re-render components
    renderTaskList();
    renderGanttChart();
    
    // Show refresh notification
    showNotification('Work plan refreshed successfully', 'success');
}

/**
 * Task management functions
 */
function addTask() {
    console.log('➕ Adding new task...');
    showNotification('Add task functionality coming soon', 'info');
}

function insertTask() {
    console.log('📝 Inserting task...');
    showNotification('Insert task functionality coming soon', 'info');
}

function markAsComplete() {
    console.log('✅ Marking tasks as complete...');
    if (workPlanState.selectedTasks.length === 0) {
        showNotification('Please select a task first', 'warning');
        return;
    }
    showNotification('Mark as complete functionality coming soon', 'info');
}

function markAsInProgress() {
    console.log('▶️ Marking tasks as in progress...');
    if (workPlanState.selectedTasks.length === 0) {
        showNotification('Please select a task first', 'warning');
        return;
    }
    showNotification('Mark as in progress functionality coming soon', 'info');
}

function emailTask() {
    console.log('📧 Emailing task...');
    showNotification('Email task functionality coming soon', 'info');
}

function reportTime() {
    console.log('⏰ Reporting time...');
    showNotification('Report time functionality coming soon', 'info');
}

function deleteTask() {
    console.log('🗑️ Deleting task...');
    if (workPlanState.selectedTasks.length === 0) {
        showNotification('Please select a task first', 'warning');
        return;
    }
    showNotification('Delete task functionality coming soon', 'info');
}

function linkTasks() {
    console.log('🔗 Linking tasks...');
    showNotification('Link tasks functionality coming soon', 'info');
}

function unlinkTasks() {
    console.log('🔓 Unlinking tasks...');
    showNotification('Unlink tasks functionality coming soon', 'info');
}

function cutTask() {
    console.log('✂️ Cutting task...');
    showNotification('Cut task functionality coming soon', 'info');
}

function copyTask() {
    console.log('📋 Copying task...');
    showNotification('Copy task functionality coming soon', 'info');
}

function pasteTask() {
    console.log('📋 Pasting task...');
    showNotification('Paste task functionality coming soon', 'info');
}

function indentTask() {
    console.log('📏 Indenting task...');
    showNotification('Indent task functionality coming soon', 'info');
}

function outdentTask() {
    console.log('📏 Outdenting task...');
    showNotification('Outdent task functionality coming soon', 'info');
}

function expandAll() {
    console.log('📖 Expanding all tasks...');
    showNotification('Expand all functionality coming soon', 'info');
}

function collapseAll() {
    console.log('📕 Collapsing all tasks...');
    showNotification('Collapse all functionality coming soon', 'info');
}

function toggleFollowing() {
    console.log('👁️ Toggling following...');
    showNotification('Following functionality coming soon', 'info');
}

function toggleFavorite() {
    console.log('⭐ Toggling favorite...');
    showNotification('Favorite functionality coming soon', 'info');
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
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
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Export functions for global access
window.selectTask = selectTask;
window.searchTasks = searchTasks;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.zoomChange = zoomChange;
window.fitToScreen = fitToScreen;
window.exportWorkPlan = exportWorkPlan;
window.printWorkPlan = printWorkPlan;
window.refreshWorkPlan = refreshWorkPlan;
window.addTask = addTask;
window.insertTask = insertTask;
window.markAsComplete = markAsComplete;
window.markAsInProgress = markAsInProgress;
window.emailTask = emailTask;
window.reportTime = reportTime;
window.deleteTask = deleteTask;
window.linkTasks = linkTasks;
window.unlinkTasks = unlinkTasks;
window.cutTask = cutTask;
window.copyTask = copyTask;
window.pasteTask = pasteTask;
window.indentTask = indentTask;
window.outdentTask = outdentTask;
window.expandAll = expandAll;
window.collapseAll = collapseAll;
window.toggleFollowing = toggleFollowing;
window.toggleFavorite = toggleFavorite;
