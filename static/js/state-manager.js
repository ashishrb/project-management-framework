/**
 * Centralized State Management System
 * Handles application state, real-time sync, and cross-view communication
 */

class StateManager {
    constructor() {
        this.state = {
            // User session
            user: null,
            sessionId: null,
            
            // Application state
            currentView: 'dashboard',
            navigationHistory: [],
            
            // Data state
            projects: new Map(),
            resources: new Map(),
            risks: new Map(),
            features: new Map(),
            backlogs: new Map(),
            
            // UI state
            loading: {
                dashboard: false,
                projects: false,
                resources: false,
                risks: false
            },
            
            // Real-time sync
            lastSync: null,
            syncStatus: 'connected', // connected, disconnected, syncing
            pendingChanges: new Set(),
            
            // Notifications
            notifications: [],
            
            // Settings
            settings: {
                autoRefresh: true,
                refreshInterval: 30000, // 30 seconds
                notifications: true,
                theme: 'light'
            }
        };
        
        this.listeners = new Map();
        this.websocket = null;
        this.syncInterval = null;
        
        this.init();
    }
    
    init() {
        this.loadSettings();
        this.setupWebSocket();
        this.setupAutoRefresh();
        this.setupEventListeners();
    }
    
    // ==================== STATE MANAGEMENT ====================
    
    getState(key = null) {
        if (key) {
            return this.state[key];
        }
        return { ...this.state };
    }
    
    setState(key, value, notify = true) {
        const oldValue = this.state[key];
        this.state[key] = value;
        
        if (notify) {
            this.notifyListeners(key, value, oldValue);
        }
    }
    
    updateState(updates, notify = true) {
        const oldState = { ...this.state };
        
        Object.keys(updates).forEach(key => {
            this.state[key] = updates[key];
        });
        
        if (notify) {
            this.notifyListeners('state', this.state, oldState);
        }
    }
    
    // ==================== EVENT SYSTEM ====================
    
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);
        
        // Return unsubscribe function
        return () => {
            const listeners = this.listeners.get(key);
            if (listeners) {
                listeners.delete(callback);
            }
        };
    }
    
    notifyListeners(key, newValue, oldValue) {
        const listeners = this.listeners.get(key);
        if (listeners) {
            listeners.forEach(callback => {
                try {
                    callback(newValue, oldValue);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }
    }
    
    // ==================== WEBSOCKET INTEGRATION ====================
    
    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.setState('syncStatus', 'connected');
            this.sendWebSocketMessage({ type: 'ping' });
        };
        
        this.websocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            } catch (error) {
                console.error('WebSocket message error:', error);
            }
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.setState('syncStatus', 'disconnected');
            this.scheduleReconnect();
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.setState('syncStatus', 'error');
        };
    }
    
    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'pong':
                this.setState('lastSync', new Date().toISOString());
                break;
                
            case 'project_updated':
                this.handleProjectUpdate(message);
                break;
                
            case 'resource_updated':
                this.handleResourceUpdate(message);
                break;
                
            case 'risk_alerted':
                this.handleRiskAlert(message);
                break;
                
            case 'broadcast_message':
                this.handleBroadcastMessage(message);
                break;
                
            default:
                console.log('Unknown WebSocket message:', message);
        }
    }
    
    sendWebSocketMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }
    
    scheduleReconnect() {
        setTimeout(() => {
            if (this.state.syncStatus === 'disconnected') {
                this.setupWebSocket();
            }
        }, 5000);
    }
    
    // ==================== DATA HANDLERS ====================
    
    handleProjectUpdate(message) {
        const { project_id, changes } = message;
        
        // Update project in state
        const currentProject = this.state.projects.get(project_id);
        if (currentProject) {
            const updatedProject = { ...currentProject, ...changes };
            this.state.projects.set(project_id, updatedProject);
            this.notifyListeners('projects', this.state.projects, this.state.projects);
        }
        
        // Show notification
        this.addNotification({
            type: 'info',
            title: 'Project Updated',
            message: `Project ${project_id} has been updated`,
            timestamp: new Date()
        });
    }
    
    handleResourceUpdate(message) {
        const { resource_id, changes } = message;
        
        // Update resource in state
        const currentResource = this.state.resources.get(resource_id);
        if (currentResource) {
            const updatedResource = { ...currentResource, ...changes };
            this.state.resources.set(resource_id, updatedResource);
            this.notifyListeners('resources', this.state.resources, this.state.resources);
        }
        
        // Show notification
        this.addNotification({
            type: 'info',
            title: 'Resource Updated',
            message: `Resource ${resource_id} has been updated`,
            timestamp: new Date()
        });
    }
    
    handleRiskAlert(message) {
        const { risk_id, severity, message: alertMessage } = message;
        
        // Update risk in state
        const currentRisk = this.state.risks.get(risk_id);
        if (currentRisk) {
            const updatedRisk = { ...currentRisk, severity, last_alert: new Date().toISOString() };
            this.state.risks.set(risk_id, updatedRisk);
            this.notifyListeners('risks', this.state.risks, this.state.risks);
        }
        
        // Show high-priority notification
        this.addNotification({
            type: severity === 'high' ? 'error' : 'warning',
            title: 'Risk Alert',
            message: alertMessage,
            timestamp: new Date(),
            priority: 'high'
        });
    }
    
    handleBroadcastMessage(message) {
        this.addNotification({
            type: 'info',
            title: 'System Message',
            message: message.content,
            timestamp: new Date()
        });
    }
    
    // ==================== DATA MANAGEMENT ====================
    
    async loadData(dataType, forceRefresh = false) {
        if (this.state.loading[dataType] && !forceRefresh) {
            return;
        }
        
        this.setState(`loading.${dataType}`, true);
        
        try {
            const response = await fetch(`/api/v1/${dataType}/`);
            if (!response.ok) {
                throw new Error(`Failed to load ${dataType}`);
            }
            
            const data = await response.json();
            this.setState(dataType, new Map(data.map(item => [item.id, item])));
            this.setState('lastSync', new Date().toISOString());
            
        } catch (error) {
            console.error(`Error loading ${dataType}:`, error);
            this.addNotification({
                type: 'error',
                title: 'Data Load Error',
                message: `Failed to load ${dataType} data`,
                timestamp: new Date()
            });
        } finally {
            this.setState(`loading.${dataType}`, false);
        }
    }
    
    async saveData(dataType, data, optimistic = true) {
        if (optimistic) {
            // Update state immediately for better UX
            const currentData = this.state[dataType];
            if (currentData instanceof Map) {
                currentData.set(data.id, data);
                this.notifyListeners(dataType, currentData, currentData);
            }
        }
        
        try {
            const response = await fetch(`/api/v1/${dataType}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to save ${dataType}`);
            }
            
            const savedData = await response.json();
            
            if (!optimistic) {
                // Update state with server response
                const currentData = this.state[dataType];
                if (currentData instanceof Map) {
                    currentData.set(savedData.id, savedData);
                    this.notifyListeners(dataType, currentData, currentData);
                }
            }
            
            return savedData;
            
        } catch (error) {
            console.error(`Error saving ${dataType}:`, error);
            
            if (optimistic) {
                // Revert optimistic update on error
                this.loadData(dataType, true);
            }
            
            throw error;
        }
    }
    
    // ==================== NAVIGATION ====================
    
    navigateTo(view, params = {}) {
        const currentView = this.state.currentView;
        
        // Add to navigation history
        this.state.navigationHistory.push({
            view: currentView,
            params: this.state.navigationParams || {},
            timestamp: new Date()
        });
        
        // Update current view
        this.setState('currentView', view);
        this.setState('navigationParams', params);
        
        // Notify listeners
        this.notifyListeners('navigation', { view, params }, { view: currentView });
    }
    
    goBack() {
        if (this.state.navigationHistory.length > 0) {
            const previous = this.state.navigationHistory.pop();
            this.setState('currentView', previous.view);
            this.setState('navigationParams', previous.params);
            this.notifyListeners('navigation', { 
                view: previous.view, 
                params: previous.params 
            }, {});
        }
    }
    
    // ==================== NOTIFICATIONS ====================
    
    addNotification(notification) {
        const notifications = [...this.state.notifications, {
            id: Date.now(),
            ...notification
        }];
        
        this.setState('notifications', notifications);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeNotification(notification.id);
        }, 5000);
    }
    
    removeNotification(id) {
        const notifications = this.state.notifications.filter(n => n.id !== id);
        this.setState('notifications', notifications);
    }
    
    clearNotifications() {
        this.setState('notifications', []);
    }
    
    // ==================== SETTINGS ====================
    
    loadSettings() {
        const saved = localStorage.getItem('genai-metrics-settings');
        if (saved) {
            try {
                const settings = JSON.parse(saved);
                this.setState('settings', { ...this.state.settings, ...settings });
            } catch (error) {
                console.error('Error loading settings:', error);
            }
        }
    }
    
    saveSettings(settings) {
        const newSettings = { ...this.state.settings, ...settings };
        this.setState('settings', newSettings);
        localStorage.setItem('genai-metrics-settings', JSON.stringify(newSettings));
    }
    
    // ==================== AUTO REFRESH ====================
    
    setupAutoRefresh() {
        if (this.state.settings.autoRefresh) {
            this.syncInterval = setInterval(() => {
                this.refreshAllData();
            }, this.state.settings.refreshInterval);
        }
    }
    
    async refreshAllData() {
        this.setState('syncStatus', 'syncing');
        
        try {
            await Promise.all([
                this.loadData('projects'),
                this.loadData('resources'),
                this.loadData('risks')
            ]);
            
            this.setState('syncStatus', 'connected');
        } catch (error) {
            console.error('Auto refresh error:', error);
            this.setState('syncStatus', 'error');
        }
    }
    
    // ==================== EVENT LISTENERS ====================
    
    setupEventListeners() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.setState('syncStatus', 'paused');
            } else {
                this.setState('syncStatus', 'connected');
                this.refreshAllData();
            }
        });
        
        // Handle beforeunload
        window.addEventListener('beforeunload', () => {
            if (this.websocket) {
                this.websocket.close();
            }
        });
    }
    
    // ==================== UTILITY METHODS ====================
    
    getDataByType(type) {
        return this.state[type] || new Map();
    }
    
    getDataById(type, id) {
        const data = this.getDataByType(type);
        return data.get(id);
    }
    
    isConnected() {
        return this.state.syncStatus === 'connected';
    }
    
    isSyncing() {
        return this.state.syncStatus === 'syncing';
    }
    
    // ==================== CLEANUP ====================
    
    destroy() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
        }
        
        if (this.websocket) {
            this.websocket.close();
        }
        
        this.listeners.clear();
    }
}

// Global state manager instance
window.stateManager = new StateManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StateManager;
}
