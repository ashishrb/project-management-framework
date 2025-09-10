/**
 * Data Synchronization Manager
 * Handles real-time data sync, conflict resolution, and offline support
 */

class SyncManager {
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.syncQueue = [];
        this.conflictResolver = new ConflictResolver();
        this.offlineStorage = new OfflineStorage();
        this.syncInProgress = false;
        this.lastSyncTime = null;
        this.syncInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupSyncInterval();
        this.setupOfflineDetection();
        this.setupConflictHandling();
        this.setupDataValidation();
    }
    
    // ==================== SYNC MANAGEMENT ====================
    
    setupSyncInterval() {
        // Sync every 30 seconds when online
        this.syncInterval = setInterval(() => {
            if (this.stateManager.isConnected() && !this.syncInProgress) {
                this.syncAllData();
            }
        }, 30000);
    }
    
    async syncAllData() {
        if (this.syncInProgress) return;
        
        this.syncInProgress = true;
        this.stateManager.setState('syncStatus', 'syncing');
        
        try {
            // Process sync queue first
            await this.processSyncQueue();
            
            // Sync all data types
            await Promise.all([
                this.syncData('projects'),
                this.syncData('resources'),
                this.syncData('risks'),
                this.syncData('features'),
                this.syncData('backlogs')
            ]);
            
            this.lastSyncTime = new Date();
            this.stateManager.setState('lastSync', this.lastSyncTime.toISOString());
            this.stateManager.setState('syncStatus', 'connected');
            
        } catch (error) {
            console.error('Sync error:', error);
            this.stateManager.setState('syncStatus', 'error');
            this.handleSyncError(error);
        } finally {
            this.syncInProgress = false;
        }
    }
    
    async syncData(dataType) {
        try {
            // Get local changes
            const localChanges = this.offlineStorage.getChanges(dataType);
            
            if (localChanges.length > 0) {
                // Push local changes to server
                await this.pushChanges(dataType, localChanges);
            }
            
            // Pull server changes
            const serverChanges = await this.pullChanges(dataType);
            
            if (serverChanges.length > 0) {
                // Apply server changes
                await this.applyChanges(dataType, serverChanges);
            }
            
        } catch (error) {
            console.error(`Sync error for ${dataType}:`, error);
            throw error;
        }
    }
    
    // ==================== CHANGE MANAGEMENT ====================
    
    async pushChanges(dataType, changes) {
        for (const change of changes) {
            try {
                const response = await fetch(`/api/v1/${dataType}/`, {
                    method: change.type === 'create' ? 'POST' : 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(change.data)
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to push ${change.type} for ${dataType}`);
                }
                
                const result = await response.json();
                
                // Update local data with server response
                this.updateLocalData(dataType, result);
                
                // Remove from offline storage
                this.offlineStorage.removeChange(dataType, change.id);
                
            } catch (error) {
                console.error(`Error pushing change for ${dataType}:`, error);
                // Keep change in queue for retry
            }
        }
    }
    
    async pullChanges(dataType) {
        try {
            const lastSync = this.offlineStorage.getLastSync(dataType);
            const url = lastSync 
                ? `/api/v1/${dataType}/?since=${lastSync}`
                : `/api/v1/${dataType}/`;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Failed to pull changes for ${dataType}`);
            }
            
            const data = await response.json();
            this.offlineStorage.setLastSync(dataType, new Date().toISOString());
            
            return data;
            
        } catch (error) {
            console.error(`Error pulling changes for ${dataType}:`, error);
            return [];
        }
    }
    
    async applyChanges(dataType, changes) {
        const currentData = this.stateManager.getDataByType(dataType);
        
        for (const change of changes) {
            try {
                // Check for conflicts
                const conflict = this.detectConflict(dataType, change, currentData);
                
                if (conflict) {
                    // Resolve conflict
                    const resolved = await this.conflictResolver.resolve(conflict);
                    this.updateLocalData(dataType, resolved);
                } else {
                    // Apply change directly
                    this.updateLocalData(dataType, change);
                }
                
            } catch (error) {
                console.error(`Error applying change for ${dataType}:`, error);
            }
        }
        
        // Notify listeners
        this.stateManager.notifyListeners(dataType, currentData, currentData);
    }
    
    updateLocalData(dataType, data) {
        const currentData = this.stateManager.getDataByType(dataType);
        
        if (Array.isArray(data)) {
            // Replace entire dataset
            const newMap = new Map(data.map(item => [item.id, item]));
            this.stateManager.setState(dataType, newMap);
        } else {
            // Update single item
            currentData.set(data.id, data);
            this.stateManager.notifyListeners(dataType, currentData, currentData);
        }
    }
    
    // ==================== CONFLICT RESOLUTION ====================
    
    detectConflict(dataType, serverChange, localData) {
        const localItem = localData.get(serverChange.id);
        
        if (!localItem) {
            return null; // No conflict, new item
        }
        
        // Check if local item was modified after server version
        const localModified = new Date(localItem.updated_at || localItem.created_at);
        const serverModified = new Date(serverChange.updated_at || serverChange.created_at);
        
        if (localModified > serverModified) {
            return {
                type: 'update_conflict',
                dataType,
                localItem,
                serverItem: serverChange,
                conflictFields: this.getConflictFields(localItem, serverChange)
            };
        }
        
        return null;
    }
    
    getConflictFields(localItem, serverItem) {
        const conflicts = [];
        
        // Compare common fields
        const fieldsToCheck = ['name', 'description', 'status', 'priority', 'updated_at'];
        
        fieldsToCheck.forEach(field => {
            if (localItem[field] !== serverItem[field]) {
                conflicts.push({
                    field,
                    localValue: localItem[field],
                    serverValue: serverItem[field]
                });
            }
        });
        
        return conflicts;
    }
    
    // ==================== OFFLINE SUPPORT ====================
    
    setupOfflineDetection() {
        window.addEventListener('online', () => {
            console.log('Connection restored');
            this.stateManager.setState('syncStatus', 'connected');
            this.syncAllData();
        });
        
        window.addEventListener('offline', () => {
            console.log('Connection lost');
            this.stateManager.setState('syncStatus', 'disconnected');
        });
    }
    
    queueChange(dataType, change) {
        const changeId = Date.now() + Math.random();
        const queuedChange = {
            id: changeId,
            dataType,
            type: change.type,
            data: change.data,
            timestamp: new Date().toISOString()
        };
        
        this.offlineStorage.addChange(dataType, queuedChange);
        this.syncQueue.push(queuedChange);
        
        // Try to sync immediately if online
        if (this.stateManager.isConnected()) {
            this.syncAllData();
        }
    }
    
    async processSyncQueue() {
        if (this.syncQueue.length === 0) return;
        
        const queue = [...this.syncQueue];
        this.syncQueue = [];
        
        for (const change of queue) {
            try {
                await this.pushChanges(change.dataType, [change]);
            } catch (error) {
                // Re-queue failed changes
                this.syncQueue.push(change);
            }
        }
    }
    
    // ==================== DATA VALIDATION ====================
    
    setupDataValidation() {
        // Validate data before syncing
        this.stateManager.subscribe('projects', (newData) => {
            this.validateData('projects', newData);
        });
        
        this.stateManager.subscribe('resources', (newData) => {
            this.validateData('resources', newData);
        });
        
        this.stateManager.subscribe('risks', (newData) => {
            this.validateData('risks', newData);
        });
    }
    
    validateData(dataType, data) {
        const validators = {
            projects: this.validateProject,
            resources: this.validateResource,
            risks: this.validateRisk
        };
        
        const validator = validators[dataType];
        if (validator) {
            if (data instanceof Map) {
                data.forEach((item, id) => {
                    const errors = validator(item);
                    if (errors.length > 0) {
                        console.warn(`Validation errors for ${dataType} ${id}:`, errors);
                    }
                });
            } else {
                const errors = validator(data);
                if (errors.length > 0) {
                    console.warn(`Validation errors for ${dataType}:`, errors);
                }
            }
        }
    }
    
    validateProject(project) {
        const errors = [];
        
        if (!project.name || project.name.trim() === '') {
            errors.push('Project name is required');
        }
        
        if (project.start_date && project.due_date) {
            const start = new Date(project.start_date);
            const due = new Date(project.due_date);
            if (start > due) {
                errors.push('Start date cannot be after due date');
            }
        }
        
        if (project.percent_complete < 0 || project.percent_complete > 100) {
            errors.push('Percent complete must be between 0 and 100');
        }
        
        return errors;
    }
    
    validateResource(resource) {
        const errors = [];
        
        if (!resource.name || resource.name.trim() === '') {
            errors.push('Resource name is required');
        }
        
        if (!resource.email || !this.isValidEmail(resource.email)) {
            errors.push('Valid email is required');
        }
        
        if (resource.availability_percentage < 0 || resource.availability_percentage > 100) {
            errors.push('Availability percentage must be between 0 and 100');
        }
        
        return errors;
    }
    
    validateRisk(risk) {
        const errors = [];
        
        if (!risk.title || risk.title.trim() === '') {
            errors.push('Risk title is required');
        }
        
        if (!risk.severity || !['low', 'medium', 'high', 'critical'].includes(risk.severity)) {
            errors.push('Valid severity level is required');
        }
        
        return errors;
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // ==================== ERROR HANDLING ====================
    
    handleSyncError(error) {
        this.stateManager.addNotification({
            type: 'error',
            title: 'Sync Error',
            message: `Failed to sync data: ${error.message}`,
            timestamp: new Date()
        });
        
        // Retry sync after delay
        setTimeout(() => {
            if (this.stateManager.isConnected()) {
                this.syncAllData();
            }
        }, 5000);
    }
    
    // ==================== UTILITY METHODS ====================
    
    getSyncStatus() {
        return {
            inProgress: this.syncInProgress,
            lastSync: this.lastSyncTime,
            queueLength: this.syncQueue.length,
            isOnline: navigator.onLine
        };
    }
    
    forceSync() {
        if (!this.syncInProgress) {
            this.syncAllData();
        }
    }
    
    clearSyncQueue() {
        this.syncQueue = [];
        this.offlineStorage.clearChanges();
    }
    
    // ==================== CLEANUP ====================
    
    destroy() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
        }
        
        this.syncQueue = [];
    }
}

// Conflict Resolution Class
class ConflictResolver {
    constructor() {
        this.resolutionStrategies = {
            'last_write_wins': this.lastWriteWins,
            'merge_fields': this.mergeFields,
            'user_choice': this.userChoice
        };
    }
    
    async resolve(conflict) {
        // For now, use last-write-wins strategy
        // In a real application, you might want to show a UI for user choice
        return this.lastWriteWins(conflict);
    }
    
    lastWriteWins(conflict) {
        const { localItem, serverItem } = conflict;
        
        // Use server version as it's more recent
        return {
            ...serverItem,
            // Keep local metadata
            local_modified: localItem.updated_at,
            conflict_resolved: true,
            resolution_strategy: 'last_write_wins'
        };
    }
    
    mergeFields(conflict) {
        const { localItem, serverItem, conflictFields } = conflict;
        const merged = { ...serverItem };
        
        // Merge non-conflicting fields from local item
        Object.keys(localItem).forEach(key => {
            if (!conflictFields.some(field => field.field === key)) {
                merged[key] = localItem[key];
            }
        });
        
        return {
            ...merged,
            conflict_resolved: true,
            resolution_strategy: 'merge_fields'
        };
    }
    
    userChoice(conflict) {
        // This would show a UI for user to choose
        // For now, return server version
        return this.lastWriteWins(conflict);
    }
}

// Offline Storage Class
class OfflineStorage {
    constructor() {
        this.storageKey = 'genai-metrics-offline';
        this.changesKey = 'genai-metrics-changes';
        this.syncKey = 'genai-metrics-sync';
    }
    
    addChange(dataType, change) {
        const changes = this.getChanges(dataType);
        changes.push(change);
        this.setChanges(dataType, changes);
    }
    
    getChanges(dataType) {
        const key = `${this.changesKey}-${dataType}`;
        const stored = localStorage.getItem(key);
        return stored ? JSON.parse(stored) : [];
    }
    
    setChanges(dataType, changes) {
        const key = `${this.changesKey}-${dataType}`;
        localStorage.setItem(key, JSON.stringify(changes));
    }
    
    removeChange(dataType, changeId) {
        const changes = this.getChanges(dataType);
        const filtered = changes.filter(change => change.id !== changeId);
        this.setChanges(dataType, filtered);
    }
    
    clearChanges() {
        const dataTypes = ['projects', 'resources', 'risks', 'features', 'backlogs'];
        dataTypes.forEach(dataType => {
            const key = `${this.changesKey}-${dataType}`;
            localStorage.removeItem(key);
        });
    }
    
    getLastSync(dataType) {
        const key = `${this.syncKey}-${dataType}`;
        return localStorage.getItem(key);
    }
    
    setLastSync(dataType, timestamp) {
        const key = `${this.syncKey}-${dataType}`;
        localStorage.setItem(key, timestamp);
    }
}

// Initialize sync manager when state manager is available
document.addEventListener('DOMContentLoaded', () => {
    if (window.stateManager) {
        window.syncManager = new SyncManager(window.stateManager);
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SyncManager;
}
