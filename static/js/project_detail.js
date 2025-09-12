/**
 * Project Detail Management JavaScript
 * Handles form validation, submission, and interactivity
 */

class ProjectDetailManager {
    constructor() {
        this.form = document.getElementById('projectDetailForm');
        this.init();
    }

    init() {
        this.setupFormValidation();
        this.setupLifecycleInteractions();
        this.setupDynamicFields();
        this.setupSaveFunctionality();
    }

    setupFormValidation() {
        // Real-time validation for required fields
        const requiredFields = document.querySelectorAll('[class*="required"]');
        requiredFields.forEach(field => {
            const input = field.parentElement.querySelector('input, select, textarea');
            if (input) {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearValidationError(input));
            }
        });

        // Form submission validation
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.parentElement.querySelector('[class*="required"]');
        
        if (isRequired && !value) {
            this.showValidationError(field, 'This field is required');
            return false;
        }

        // Specific validations
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.showValidationError(field, 'Please enter a valid email address');
                return false;
            }
        }

        if (field.type === 'number' && value) {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            const numValue = parseFloat(value);
            
            if (min && numValue < parseFloat(min)) {
                this.showValidationError(field, `Value must be at least ${min}`);
                return false;
            }
            
            if (max && numValue > parseFloat(max)) {
                this.showValidationError(field, `Value must be at most ${max}`);
                return false;
            }
        }

        this.clearValidationError(field);
        return true;
    }

    showValidationError(field, message) {
        this.clearValidationError(field);
        
        field.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.parentElement.appendChild(errorDiv);
    }

    clearValidationError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    setupLifecycleInteractions() {
        const lifecycleStages = document.querySelectorAll('.lifecycle-stage');
        lifecycleStages.forEach(stage => {
            stage.addEventListener('click', () => {
                // Remove active class from all stages
                lifecycleStages.forEach(s => s.classList.remove('active'));
                // Add active class to clicked stage
                stage.classList.add('active');
                
                // Update phase field
                const phaseField = document.querySelector('select[name="phase"]');
                if (phaseField) {
                    const phaseName = stage.querySelector('h4').textContent;
                    phaseField.value = phaseName;
                }
            });
        });
    }

    setupDynamicFields() {
        // NIST section visibility based on project type
        const projectTypeSelect = document.querySelector('select[name="project_type"]');
        const nistSection = document.querySelector('h4:contains("NIST CSF Alignment")');
        
        if (projectTypeSelect && nistSection) {
            projectTypeSelect.addEventListener('change', () => {
                const nistContainer = nistSection.parentElement;
                if (projectTypeSelect.value === 'IT' || projectTypeSelect.value === 'Security') {
                    nistContainer.style.display = 'block';
                } else {
                    nistContainer.style.display = 'none';
                }
            });
        }

        // Auto-populate related fields
        this.setupAutoPopulation();
    }

    setupAutoPopulation() {
        // Auto-populate ESA ID based on project ID
        const projectIdField = document.querySelector('input[value*="P-"]');
        const esaIdField = document.querySelector('input[placeholder*="ESA ID"]');
        
        if (projectIdField && esaIdField && !esaIdField.value) {
            // Generate ESA ID based on project ID
            const projectId = projectIdField.value;
            const esaId = projectId.replace('P-', '1000');
            esaIdField.value = esaId;
        }
    }

    setupSaveFunctionality() {
        const saveDraftBtn = document.querySelector('button:contains("Save Draft")');
        const saveSubmitBtn = document.querySelector('button:contains("Save & Submit")');
        
        if (saveDraftBtn) {
            saveDraftBtn.addEventListener('click', () => this.saveProject('draft'));
        }
        
        if (saveSubmitBtn) {
            saveSubmitBtn.addEventListener('click', () => this.saveProject('submit'));
        }
    }

    async saveProject(action) {
        // Validate all required fields
        const isValid = this.validateAllFields();
        if (!isValid) {
            this.showNotification('Please fix validation errors before saving', 'error');
            return;
        }

        try {
            const formData = this.collectFormData();
            formData.action = action;
            
            const projectId = this.getProjectId();
            const response = await fetch(`/api/v1/project-detail/${projectId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const message = action === 'draft' ? 'Draft saved successfully' : 'Project submitted successfully';
                this.showNotification(message, 'success');
            } else {
                throw new Error('Save failed');
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showNotification('Failed to save project. Please try again.', 'error');
        }
    }

    validateAllFields() {
        const requiredFields = document.querySelectorAll('[class*="required"]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            const input = field.parentElement.querySelector('input, select, textarea');
            if (input && !this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    collectFormData() {
        const formData = {};
        
        // Collect all form fields
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.name) {
                formData[input.name] = input.value;
            }
        });

        // Collect stakeholders
        formData.stakeholders = this.collectStakeholders();
        
        // Collect charter information
        formData.charter = this.collectCharterInfo();
        
        // Collect NIST information
        formData.nist = this.collectNISTInfo();
        
        return formData;
    }

    collectStakeholders() {
        return {
            business_owner: document.querySelector('input[value*="Neal Ramasamy"]')?.value || '',
            business_sponsor: document.querySelector('input[placeholder*="Business Sponsor"]')?.value || '',
            technology_portfolio_leader: document.querySelector('input[value*="Hariprasad"]')?.value || ''
        };
    }

    collectCharterInfo() {
        return {
            additional_observations: document.querySelector('textarea[placeholder*="charter observations"]')?.value || '',
            sustainability_operationalization: document.querySelector('textarea[placeholder*="sustainability"]')?.value || '',
            assumptions: document.querySelector('textarea[placeholder*="assumptions"]')?.value || '',
            out_of_scope: document.querySelector('textarea[placeholder*="out of scope"]')?.value || '',
            charter_status: document.querySelector('select[placeholder*="Charter Status"]')?.value || '',
            risk_management_approval: document.querySelector('select[placeholder*="Risk Management"]')?.value || '',
            charter_approved: document.querySelector('select[placeholder*="Charter Approval"]')?.value || ''
        };
    }

    collectNISTInfo() {
        return {
            findings: document.querySelector('textarea[placeholder*="NIST findings"]')?.value || '',
            mapping: document.querySelector('input[placeholder*="NIST Mapping"]')?.value || '',
            domain: document.querySelector('input[placeholder*="NIST Domain"]')?.value || '',
            ofi_number: document.querySelector('input[placeholder*="NIST OFI"]')?.value || '',
            self_assessment_score: document.querySelector('input[placeholder*="score 0-5"]')?.value || ''
        };
    }

    getProjectId() {
        const projectIdField = document.querySelector('input[value*="P-"]');
        return projectIdField ? projectIdField.value : 'P-00001';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProjectDetailManager();
});

// Utility function to check if element contains text
Element.prototype.contains = function(text) {
    return this.textContent.includes(text);
};
