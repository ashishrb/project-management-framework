/**
 * WebSocket Manager for Real-time Updates
 * Handles WebSocket connections and real-time UI updates
 */

// WebSocket Manager State
let websocketManager = {
    connections: {},
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    isInitialized: false
};

/**
 * Initialize WebSocket Manager
 */
function initializeWebSocketManager() {
    console.log('🔌 Initializing WebSocket Manager...');
    
    try {
        // Connect to different WebSocket rooms
        connectToRoom('dashboard', '/ws/dashboard');
        connectToRoom('projects', '/ws/projects');
        connectToRoom('risks', '/ws/risks');
        connectToRoom('resources', '/ws/resources');
        
        websocketManager.isInitialized = true;
        console.log('✅ WebSocket Manager initialized successfully');
        
    } catch (error) {
        console.error('❌ Error initializing WebSocket Manager:', error);
    }
}

/**
 * Connect to a specific WebSocket room
 */
function connectToRoom(roomName, endpoint) {
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}${endpoint}`;
        
        console.log(`🔌 Connecting to ${roomName} room: ${wsUrl}`);
        
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = function(event) {
            console.log(`✅ Connected to ${roomName} room`);
            websocketManager.reconnectAttempts = 0;
            
            // Send initial message to identify room
            ws.send(JSON.stringify({
                type: 'join_room',
                room: roomName,
                timestamp: new Date().toISOString()
            }));
        };
        
        ws.onmessage = function(event) {
            try {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(roomName, message);
            } catch (error) {
                console.error(`Error parsing message from ${roomName}:`, error);
            }
        };
        
        ws.onclose = function(event) {
            console.log(`🔌 Disconnected from ${roomName} room`);
            websocketManager.connections[roomName] = null;
            
            // Attempt to reconnect
            if (websocketManager.reconnectAttempts < websocketManager.maxReconnectAttempts) {
                setTimeout(() => {
                    websocketManager.reconnectAttempts++;
                    console.log(`🔄 Attempting to reconnect to ${roomName} (attempt ${websocketManager.reconnectAttempts})`);
                    connectToRoom(roomName, endpoint);
                }, websocketManager.reconnectDelay * websocketManager.reconnectAttempts);
            }
        };
        
        ws.onerror = function(error) {
            console.error(`❌ WebSocket error in ${roomName} room:`, error);
        };
        
        websocketManager.connections[roomName] = ws;
        
    } catch (error) {
        console.error(`❌ Error connecting to ${roomName} room:`, error);
    }
}

/**
 * Handle WebSocket Messages
 */
function handleWebSocketMessage(roomName, message) {
    console.log(`📨 Received message from ${roomName}:`, message);
    
    switch (message.type) {
        case 'project_updated':
            handleProjectUpdate(message);
            break;
        case 'project_created':
            handleProjectCreated(message);
            break;
        case 'project_deleted':
            handleProjectDeleted(message);
            break;
        case 'task_created':
            handleTaskCreated(message);
            break;
        case 'task_updated':
            handleTaskUpdated(message);
            break;
        case 'risk_created':
            handleRiskCreated(message);
            break;
        case 'risk_updated':
            handleRiskUpdated(message);
            break;
        case 'resource_created':
            handleResourceCreated(message);
            break;
        case 'resource_updated':
            handleResourceUpdated(message);
            break;
        case 'dashboard_refresh':
            handleDashboardRefresh(message);
            break;
        case 'broadcast_message':
            handleBroadcastMessage(message);
            break;
        default:
            console.log(`Unknown message type: ${message.type}`);
    }
}

/**
 * Handle Project Updates
 */
function handleProjectUpdate(message) {
    console.log('📊 Handling project update:', message);
    
    // Update project cards if they exist
    updateProjectCard(message.project_id, message);
    
    // Update dashboard metrics if on dashboard page
    if (window.location.pathname.includes('dashboard')) {
        refreshDashboardMetrics();
    }
    
    // Update home page metrics if on home page
    if (window.location.pathname === '/' && window.refreshHomePageData) {
        window.refreshHomePageData();
    }
    
    // Show notification
    showWebSocketNotification(`Project ${message.name || message.project_id} updated`, 'info');
}

/**
 * Handle Project Created
 */
function handleProjectCreated(message) {
    console.log('➕ Handling project created:', message);
    
    // Refresh project lists
    if (window.location.pathname.includes('projects')) {
        refreshProjectList();
    }
    
    // Update dashboard metrics
    if (window.location.pathname.includes('dashboard')) {
        refreshDashboardMetrics();
    }
    
    // Show notification
    showWebSocketNotification(`New project created: ${message.name || message.project_id}`, 'success');
}

/**
 * Handle Project Deleted
 */
function handleProjectDeleted(message) {
    console.log('🗑️ Handling project deleted:', message);
    
    // Remove project from UI
    removeProjectFromUI(message.project_id);
    
    // Refresh project lists
    if (window.location.pathname.includes('projects')) {
        refreshProjectList();
    }
    
    // Show notification
    showWebSocketNotification(`Project ${message.project_id} deleted`, 'warning');
}

/**
 * Handle Task Updates
 */
function handleTaskCreated(message) {
    console.log('📋 Handling task created:', message);
    
    // Update work plan if on work plan page
    if (window.location.pathname.includes('work-plan') && window.refreshWorkPlan) {
        window.refreshWorkPlan();
    }
    
    // Show notification
    showWebSocketNotification(`New task created in project ${message.project_id}`, 'info');
}

function handleTaskUpdated(message) {
    console.log('📋 Handling task updated:', message);
    
    // Update work plan if on work plan page
    if (window.location.pathname.includes('work-plan') && window.refreshWorkPlan) {
        window.refreshWorkPlan();
    }
    
    // Show notification
    showWebSocketNotification(`Task ${message.task_id} updated`, 'info');
}

/**
 * Handle Risk Updates
 */
function handleRiskCreated(message) {
    console.log('⚠️ Handling risk created:', message);
    
    // Update risk management page
    if (window.location.pathname.includes('risk') && window.refreshRiskData) {
        window.refreshRiskData();
    }
    
    // Show notification
    showWebSocketNotification(`New risk identified: ${message.risk_type || 'Risk'}`, 'warning');
}

function handleRiskUpdated(message) {
    console.log('⚠️ Handling risk updated:', message);
    
    // Update risk management page
    if (window.location.pathname.includes('risk') && window.refreshRiskData) {
        window.refreshRiskData();
    }
    
    // Show notification
    showWebSocketNotification(`Risk ${message.risk_id} updated`, 'warning');
}

/**
 * Handle Resource Updates
 */
function handleResourceCreated(message) {
    console.log('👥 Handling resource created:', message);
    
    // Update resource management page
    if (window.location.pathname.includes('resource') && window.refreshResourceData) {
        window.refreshResourceData();
    }
    
    // Show notification
    showWebSocketNotification(`New resource added: ${message.name || message.resource_id}`, 'info');
}

function handleResourceUpdated(message) {
    console.log('👥 Handling resource updated:', message);
    
    // Update resource management page
    if (window.location.pathname.includes('resource') && window.refreshResourceData) {
        window.refreshResourceData();
    }
    
    // Show notification
    showWebSocketNotification(`Resource ${message.resource_id} updated`, 'info');
}

/**
 * Handle Dashboard Refresh
 */
function handleDashboardRefresh(message) {
    console.log('🔄 Handling dashboard refresh:', message);
    
    // Refresh current dashboard
    if (window.location.pathname.includes('dashboard')) {
        if (window.refreshManagerDashboard) {
            window.refreshManagerDashboard();
        } else if (window.refreshPortfolioDashboard) {
            window.refreshPortfolioDashboard();
        } else if (window.refreshComprehensiveDashboard) {
            window.refreshComprehensiveDashboard();
        }
    }
    
    // Show notification
    showWebSocketNotification('Dashboard data refreshed', 'info');
}

/**
 * Handle Broadcast Messages
 */
function handleBroadcastMessage(message) {
    console.log('📢 Handling broadcast message:', message);
    
    // Show broadcast notification
    showWebSocketNotification(`Broadcast: ${message.content}`, 'info');
}

/**
 * UI Update Functions
 */
function updateProjectCard(projectId, data) {
    const projectCard = document.querySelector(`[data-project-id="${projectId}"]`);
    if (projectCard) {
        // Update project status if provided
        if (data.status) {
            const statusElement = projectCard.querySelector('.project-status');
            if (statusElement) {
                statusElement.textContent = data.status;
                statusElement.className = `project-status badge bg-${getStatusColor(data.status)}`;
            }
        }
        
        // Update project name if provided
        if (data.name) {
            const nameElement = projectCard.querySelector('.project-name');
            if (nameElement) {
                nameElement.textContent = data.name;
            }
        }
        
        // Add update animation
        projectCard.classList.add('updated');
        setTimeout(() => {
            projectCard.classList.remove('updated');
        }, 2000);
    }
}

function removeProjectFromUI(projectId) {
    const projectCard = document.querySelector(`[data-project-id="${projectId}"]`);
    if (projectCard) {
        projectCard.style.transition = 'opacity 0.5s ease';
        projectCard.style.opacity = '0';
        setTimeout(() => {
            projectCard.remove();
        }, 500);
    }
}

function refreshProjectList() {
    // Trigger project list refresh if function exists
    if (window.refreshProjectList) {
        window.refreshProjectList();
    } else if (window.loadProjects) {
        window.loadProjects();
    }
}

function refreshDashboardMetrics() {
    // Trigger dashboard refresh if function exists
    if (window.refreshDashboardMetrics) {
        window.refreshDashboardMetrics();
    } else if (window.loadDashboardData) {
        window.loadDashboardData();
    }
}

/**
 * Show WebSocket Notification
 */
function showWebSocketNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed websocket-notification`;
    notification.style.top = '80px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.maxWidth = '400px';
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-broadcast-tower me-2"></i>
            <div class="flex-grow-1">
                <strong>Real-time Update</strong><br>
                <small>${message}</small>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Helper Functions
 */
function getStatusColor(status) {
    const colors = {
        'Active': 'success',
        'Completed': 'success',
        'Planning': 'info',
        'At Risk': 'warning',
        'On Hold': 'secondary',
        'Cancelled': 'danger'
    };
    return colors[status] || 'secondary';
}

/**
 * Send Message to WebSocket Room
 */
function sendWebSocketMessage(roomName, message) {
    const ws = websocketManager.connections[roomName];
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
    } else {
        console.warn(`WebSocket connection to ${roomName} is not available`);
    }
}

/**
 * Disconnect All WebSocket Connections
 */
function disconnectAllWebSockets() {
    console.log('🔌 Disconnecting all WebSocket connections...');
    
    Object.keys(websocketManager.connections).forEach(roomName => {
        const ws = websocketManager.connections[roomName];
        if (ws) {
            ws.close();
        }
    });
    
    websocketManager.connections = {};
    websocketManager.isInitialized = false;
}

/**
 * Reconnect All WebSocket Connections
 */
function reconnectAllWebSockets() {
    console.log('🔄 Reconnecting all WebSocket connections...');
    
    disconnectAllWebSockets();
    setTimeout(() => {
        initializeWebSocketManager();
    }, 1000);
}

// Initialize WebSocket Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if not already initialized
    if (!websocketManager.isInitialized) {
        initializeWebSocketManager();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    disconnectAllWebSockets();
});

// Export functions for global access
window.websocketManager = websocketManager;
window.sendWebSocketMessage = sendWebSocketMessage;
window.reconnectAllWebSockets = reconnectAllWebSockets;
window.disconnectAllWebSockets = disconnectAllWebSockets;

// Add CSS for update animations
const style = document.createElement('style');
style.textContent = `
    .updated {
        animation: updatePulse 2s ease-in-out;
    }
    
    @keyframes updatePulse {
        0% { background-color: transparent; }
        50% { background-color: rgba(0, 123, 255, 0.1); }
        100% { background-color: transparent; }
    }
    
    .websocket-notification {
        border-left: 4px solid #007bff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
`;
document.head.appendChild(style);
