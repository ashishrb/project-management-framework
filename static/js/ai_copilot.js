/**
 * AI Copilot Console JavaScript
 * GenAI Metrics Dashboard - AI Copilot Features
 */

// Global variables
let currentConversation = null;
let conversations = [];
let loadedContext = {
    projects: false,
    resources: false,
    finance: false
};
let uploadedDocuments = [];
let isTyping = false;
let csrfToken = null;

// AI Configuration
let aiConfig = {
    mode: 'balanced',
    contextLength: 'medium',
    memoryType: 'conversation',
    temperature: 0.7
};

// AI Mode configurations
const AI_MODES = {
    balanced: {
        name: 'Balanced',
        description: 'Balanced responses with good speed and detail',
        model: 'llama3:8b',
        maxTokens: 4000,
        temperature: 0.7
    },
    fast: {
        name: 'Fast',
        description: 'Quick responses for simple queries',
        model: 'llama3.2:3b-instruct-q4_K_M',
        maxTokens: 2000,
        temperature: 0.5
    },
    detailed: {
        name: 'Detailed',
        description: 'Comprehensive and thorough responses',
        model: 'llama3:8b',
        maxTokens: 8000,
        temperature: 0.8
    },
    creative: {
        name: 'Creative',
        description: 'Creative and innovative suggestions',
        model: 'mistral:7b-instruct-v0.2-q4_K_M',
        maxTokens: 4000,
        temperature: 0.9
    },
    rag: {
        name: 'RAG',
        description: 'Retrieval-Augmented Generation with document context',
        model: 'llama3:8b',
        maxTokens: 4000,
        temperature: 0.6,
        useRAG: true
    }
};

/**
 * Get CSRF token
 */
async function getCSRFToken() {
    if (csrfToken) return csrfToken;
    
    try {
        const response = await fetch('/csrf-token');
        const data = await response.json();
        csrfToken = data.csrf_token;
        return csrfToken;
    } catch (error) {
        console.error('Failed to get CSRF token:', error);
        return null;
    }
}

/**
 * Initialize AI Copilot
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Initializing AI Copilot Console...');
    initializeCopilot();
    setupEventListeners();
    loadConversations();
    getCSRFToken(); // Pre-load CSRF token
});

/**
 * Initialize copilot components
 */
function initializeCopilot() {
    // Initialize conversation
    startNewConversation();
    
    // Update UI with current config
    updateConfigurationUI();
    
    // Setup file upload
    setupFileUpload();
    
    console.log('✅ AI Copilot initialized');
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // AI Configuration changes
    document.getElementById('aiMode').addEventListener('change', updateAIConfig);
    document.getElementById('contextLength').addEventListener('change', updateAIConfig);
    document.getElementById('memoryType').addEventListener('change', updateAIConfig);
    document.getElementById('temperature').addEventListener('input', updateAIConfig);
    
    // Chat input
    const chatInput = document.getElementById('chatInput');
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // File upload area
    const uploadArea = document.getElementById('documentUploadArea');
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);
}

/**
 * Update AI configuration
 */
function updateAIConfig() {
    aiConfig.mode = document.getElementById('aiMode').value;
    aiConfig.contextLength = document.getElementById('contextLength').value;
    aiConfig.memoryType = document.getElementById('memoryType').value;
    aiConfig.temperature = parseFloat(document.getElementById('temperature').value);
    
    // Update temperature display
    document.getElementById('temperatureValue').textContent = aiConfig.temperature;
    
    // Update status bar
    updateStatusBar();
    
    console.log('🔧 AI Config updated:', aiConfig);
}

/**
 * Update configuration UI
 */
function updateConfigurationUI() {
    document.getElementById('aiMode').value = aiConfig.mode;
    document.getElementById('contextLength').value = aiConfig.contextLength;
    document.getElementById('memoryType').value = aiConfig.memoryType;
    document.getElementById('temperature').value = aiConfig.temperature;
    document.getElementById('temperatureValue').textContent = aiConfig.temperature;
    
    updateStatusBar();
}

/**
 * Update status bar
 */
function updateStatusBar() {
    const contextText = Object.values(loadedContext).some(v => v) ? 'Context loaded' : 'No context loaded';
    const memoryText = aiConfig.memoryType;
    const modeText = AI_MODES[aiConfig.mode].name.toLowerCase();
    
    document.getElementById('currentContext').textContent = contextText;
    document.getElementById('currentMemory').textContent = memoryText;
    document.getElementById('currentMode').textContent = modeText;
    
    // Update context badge
    const contextBadge = document.getElementById('contextBadge');
    if (Object.values(loadedContext).some(v => v)) {
        contextBadge.textContent = 'Context Loaded';
        contextBadge.className = 'badge bg-success';
    } else {
        contextBadge.textContent = 'No Context';
        contextBadge.className = 'badge bg-info';
    }
}

/**
 * Start new conversation
 */
function startNewConversation() {
    const conversationId = Date.now().toString();
    currentConversation = {
        id: conversationId,
        title: `Conversation ${conversations.length + 1}`,
        messages: [],
        createdAt: new Date(),
        context: { ...loadedContext }
    };
    
    conversations.unshift(currentConversation);
    updateConversationHistory();
    clearChatMessages();
    
    // Add welcome message
    addMessage('ai', 'New conversation started. How can I help you today?');
    
    console.log('💬 New conversation started:', conversationId);
}

/**
 * Load conversations from storage
 */
function loadConversations() {
    const stored = localStorage.getItem('ai_copilot_conversations');
    if (stored) {
        conversations = JSON.parse(stored);
        if (conversations.length > 0) {
            currentConversation = conversations[0];
            loadConversation(currentConversation.id);
        }
    }
    updateConversationHistory();
}

/**
 * Save conversations to storage
 */
function saveConversations() {
    localStorage.setItem('ai_copilot_conversations', JSON.stringify(conversations));
}

/**
 * Update conversation history UI
 */
function updateConversationHistory() {
    const container = document.getElementById('conversationHistory');
    
    if (conversations.length === 0) {
        container.innerHTML = '<div class="text-center text-muted p-3">No conversations yet</div>';
        return;
    }
    
    container.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.id === currentConversation?.id ? 'active' : ''}" 
             onclick="loadConversation('${conv.id}')">
            <div class="conversation-title">${conv.title}</div>
            <div class="conversation-preview">${conv.messages[0]?.text || 'New conversation'}</div>
            <div class="conversation-time">${formatTime(conv.createdAt)}</div>
        </div>
    `).join('');
}

/**
 * Load specific conversation
 */
function loadConversation(conversationId) {
    currentConversation = conversations.find(c => c.id === conversationId);
    if (!currentConversation) return;
    
    clearChatMessages();
    currentConversation.messages.forEach(msg => {
        addMessage(msg.type, msg.text, false);
    });
    
    updateConversationHistory();
    console.log('📖 Loaded conversation:', conversationId);
}

/**
 * Clear chat messages
 */
function clearChatMessages() {
    document.getElementById('chatMessages').innerHTML = '';
}

/**
 * Add message to chat
 */
function addMessage(type, text, save = true) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const time = new Date().toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${text}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Save to conversation
    if (save && currentConversation) {
        currentConversation.messages.push({
            type: type,
            text: text,
            timestamp: new Date()
        });
        saveConversations();
    }
}

/**
 * Send message
 */
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage('user', message);
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Get AI response
        const response = await getAIResponse(message);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add AI response
        addMessage('ai', response);
        
    } catch (error) {
        hideTypingIndicator();
        addMessage('ai', 'Sorry, I encountered an error. Please try again.');
        console.error('❌ Error getting AI response:', error);
    }
}

/**
 * Get AI response
 */
async function getAIResponse(message) {
    const mode = AI_MODES[aiConfig.mode];
    
    // Build context
    const context = buildContext();
    
    // Prepare request
    const requestData = {
        message: message,
        mode: aiConfig.mode,
        model: mode.model,
        temperature: mode.temperature,
        max_tokens: mode.maxTokens,
        context: context,
        use_rag: mode.useRAG || false,
        documents: uploadedDocuments
    };
    
    // Get CSRF token
    const token = await getCSRFToken();
    
    const response = await fetch('/api/v1/ai/copilot/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': token || ''
        },
        credentials: 'include',
        body: JSON.stringify({
            ...requestData,
            csrf_token: token
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.response || 'I apologize, but I couldn\'t generate a response at this time.';
}

/**
 * Build context from loaded data
 */
function buildContext() {
    const context = {
        projects: loadedContext.projects ? 'Project data loaded' : null,
        resources: loadedContext.resources ? 'Resource data loaded' : null,
        finance: loadedContext.finance ? 'Financial data loaded' : null,
        documents: uploadedDocuments.length > 0 ? `${uploadedDocuments.length} documents loaded` : null
    };
    
    return Object.entries(context)
        .filter(([key, value]) => value !== null)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    isTyping = true;
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai-message';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="typing-indicator show">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    isTyping = false;
    const typingDiv = document.getElementById('typingIndicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

/**
 * Load context data
 */
async function loadContext(type) {
    try {
        let endpoint = '';
        let data = null;
        
        switch (type) {
            case 'projects':
                endpoint = '/api/v1/projects';
                break;
            case 'resources':
                endpoint = '/api/v1/resources';
                break;
            case 'finance':
                endpoint = '/api/v1/analytics/financial-summary';
                break;
        }
        
        if (endpoint) {
            const response = await fetch(endpoint);
            if (response.ok) {
                data = await response.json();
                loadedContext[type] = true;
                updateContextStatus();
                updateStatusBar();
                
                addMessage('ai', `${type.charAt(0).toUpperCase() + type.slice(1)} data loaded successfully!`);
                console.log(`✅ ${type} context loaded`);
            }
        }
        
    } catch (error) {
        console.error(`❌ Error loading ${type} context:`, error);
        addMessage('ai', `Failed to load ${type} data. Please try again.`);
    }
}

/**
 * Update context status
 */
function updateContextStatus() {
    const status = Object.values(loadedContext).some(v => v) ? 'Context loaded' : 'No context loaded';
    document.getElementById('contextStatus').textContent = status;
}

/**
 * Setup file upload
 */
function setupFileUpload() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    uploadFiles(files);
}

/**
 * Handle drag over
 */
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

/**
 * Handle drag leave
 */
function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

/**
 * Handle file drop
 */
function handleFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = Array.from(event.dataTransfer.files);
    uploadFiles(files);
}

/**
 * Browse files
 */
function browseFiles() {
    const modal = new bootstrap.Modal(document.getElementById('fileUploadModal'));
    modal.show();
}

/**
 * Upload files
 */
function uploadFiles(files) {
    files.forEach(file => {
        const document = {
            id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: new Date()
        };
        
        uploadedDocuments.push(document);
    });
    
    updateDocumentList();
    updateDocumentStatus();
    
    addMessage('ai', `${files.length} document(s) uploaded successfully!`);
    console.log('📄 Documents uploaded:', files.length);
}

/**
 * Upload documents from modal
 */
function uploadDocuments() {
    const fileInput = document.getElementById('fileInput');
    const files = Array.from(fileInput.files);
    
    if (files.length === 0) {
        alert('Please select files to upload');
        return;
    }
    
    uploadFiles(files);
    
    // Close modal
    bootstrap.Modal.getInstance(document.getElementById('fileUploadModal')).hide();
    
    // Reset form
    document.getElementById('fileInput').value = '';
    document.getElementById('documentDescription').value = '';
}

/**
 * Update document list
 */
function updateDocumentList() {
    const container = document.getElementById('uploadedDocuments');
    
    if (uploadedDocuments.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = uploadedDocuments.map(doc => `
        <div class="document-item">
            <div class="document-name">
                <i class="fas fa-file me-1"></i>
                ${doc.name}
            </div>
            <div class="document-actions">
                <button class="btn btn-sm btn-outline-danger" onclick="removeDocument('${doc.id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Remove document
 */
function removeDocument(documentId) {
    uploadedDocuments = uploadedDocuments.filter(doc => doc.id !== documentId);
    updateDocumentList();
    updateDocumentStatus();
    
    addMessage('ai', 'Document removed successfully!');
}

/**
 * Update document status
 */
function updateDocumentStatus() {
    const status = uploadedDocuments.length > 0 ? 
        `${uploadedDocuments.length} document(s) uploaded` : 
        'No documents uploaded';
    document.getElementById('documentStatus').textContent = status;
}

/**
 * Quick action handler
 */
async function quickAction(action) {
    const actions = {
        'project-report': 'Generate a comprehensive project report',
        'resource-analysis': 'Analyze resource allocation and utilization',
        'budget-review': 'Review budget status and financial performance',
        'risk-summary': 'Provide a risk assessment and mitigation summary',
        'executive-summary': 'Create an executive summary of current status',
        'schedule-tips': 'Provide scheduling optimization recommendations',
        'performance': 'Analyze project performance metrics',
        'strategy': 'Suggest strategic improvements and next steps',
        'financial-report-email': 'Generate financial report and prepare email',
        'save-to-folder': 'Save current analysis to project folder',
        'executive-summary-email': 'Create executive summary and prepare email',
        'resource-report-save': 'Generate resource report and save to folder'
    };
    
    const message = actions[action] || 'Execute quick action';
    
    // Add user message
    addMessage('user', `Quick Action: ${message}`);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Get AI response for quick action
        const response = await getAIResponse(message);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add AI response
        addMessage('ai', response);
        
    } catch (error) {
        hideTypingIndicator();
        addMessage('ai', 'Sorry, I couldn\'t execute that quick action. Please try again.');
        console.error('❌ Error executing quick action:', error);
    }
}

/**
 * Clear conversation
 */
function clearConversation() {
    if (confirm('Are you sure you want to clear the current conversation?')) {
        startNewConversation();
    }
}

/**
 * Export conversation
 */
function exportConversation() {
    if (!currentConversation || currentConversation.messages.length === 0) {
        alert('No conversation to export');
        return;
    }
    
    const content = currentConversation.messages.map(msg => 
        `${msg.type.toUpperCase()}: ${msg.text}`
    ).join('\n\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation-${currentConversation.id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Toggle fullscreen
 */
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

/**
 * Utility functions
 */
function formatTime(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
    return new Date(date).toLocaleDateString();
}

// Make functions globally available
window.startNewConversation = startNewConversation;
window.loadConversation = loadConversation;
window.loadContext = loadContext;
window.browseFiles = browseFiles;
window.uploadDocuments = uploadDocuments;
window.removeDocument = removeDocument;
window.quickAction = quickAction;
window.clearConversation = clearConversation;
window.exportConversation = exportConversation;
window.toggleFullscreen = toggleFullscreen;
