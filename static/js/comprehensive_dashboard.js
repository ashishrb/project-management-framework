/**
 * Comprehensive Dashboard JavaScript
 * Matching the exact layout and functionality from the screenshot
 */

// Global chart instances
let charts = {
    benefitPlans: null,
    plannedBenefits: null,
    businessUnit: null,
    investmentType: null,
    investmentClass: null,
    priority: null
};

// Dashboard data cache
let dashboardData = null;
let aiAnalysisData = {
    comprehensive: null,
    health: null,
    financial: null,
    resource: null,
    predictive: null
};

// Chart.js default configuration
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.font.size = 12;
Chart.defaults.color = '#6c757d';

/**
 * Load comprehensive dashboard data
 */
window.loadComprehensiveDashboard = async function() {
    console.log('🚀 Loading comprehensive dashboard data...');
    
    // Show loading indicator
    showLoadingIndicator(true);
    
    try {
        const response = await fetch('/api/v1/comprehensive-dashboard/comprehensive-dashboard');
        if (!response.ok) throw new Error('Failed to fetch dashboard data');
        
        dashboardData = await response.json();
        console.log('📊 Dashboard data loaded:', dashboardData);
        
        // Update UI with loaded data
        updateKPICards();
        createAllCharts();
        
        // Load AI analysis
        await loadAIAnalysis();
        
        console.log('✅ Comprehensive dashboard loaded successfully');
        
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        showError('Failed to load dashboard data. Please try again.');
        
        // Set fallback data matching screenshot
        dashboardData = {
            kpis: {
                active_projects: 128,
                planned_cost: 49300000,
                planned_benefits: 65230000,
                estimate_at_completion: 36540000,
                actual_cost: 2750000,
                actual_benefits: 27760000
            },
            charts: {
                benefit_plans_by_category: {
                    labels: ['Cost savings', 'Revenue', 'Process Improvement', 'Productivity', 'Rework time reduction', 'Customer satisfaction', 'Defect rate reduction', 'Ease of use', 'Cost avoidance', 'Risk reduction'],
                    data: [41, 27, 21, 15, 12, 10, 8, 8, 7, 5],
                    colors: ['#28a745', '#fd7e14', '#ffc107', '#6f42c1', '#17a2b8', '#dc3545', '#20c997', '#6c757d', '#e83e8c', '#fd7e14'],
                    total: 150
                },
                projects_planned_benefits_by_category: {
                    labels: ['Cost savings', 'Process improvement', 'Revenue', 'Productivity', 'Rework time reduc...', 'Ease of use', 'Defect rate reduc...', 'Cost avoidance', 'Customer satisfac...', 'Risk reduction'],
                    data: [17500000, 12000000, 9550631.79, 8000000, 6000000, 5000000, 4000000, 3000000, 2500000, 2000000],
                    colors: ['#28a745', '#fd7e14', '#ffc107', '#6f42c1', '#17a2b8', '#dc3545', '#20c997', '#6c757d', '#e83e8c', '#fd7e14']
                },
                projects_by_business_unit: {
                    labels: ['IT', '(empty)', 'Legal', 'Finance', 'HR', 'Facilities', 'Sales'],
                    data: [47, 35, 16, 13, 12, 10, 1],
                    colors: ['#007bff', '#28a745', '#ffc107', '#fd7e14', '#6f42c1', '#17a2b8', '#dc3545'],
                    total: 134
                },
                projects_by_investment_type: {
                    labels: ['End User Experience', 'Cost Reduction', 'Strategic Enabler', 'Revenue Generating'],
                    data: [30, 15, 13, 7],
                    colors: ['#007bff', '#28a745', '#6f42c1', '#dc3545'],
                    total: 65
                },
                projects_by_investment_class: {
                    labels: ['Change', '(empty)', 'Other'],
                    data: [60, 21, 53],
                    colors: ['#007bff', '#ffc107', '#28a745'],
                    total: 134
                },
                projects_by_priority: {
                    labels: ['4-Low', '1-Critical', '2-High', '3-Moderate'],
                    data: [60, 25, 30, 13],
                    colors: ['#17a2b8', '#dc3545', '#ffc107', '#fd7e14']
                }
            }
        };
        
        updateKPICards();
        createAllCharts();
        
    } finally {
        showLoadingIndicator(false);
    }
};

/**
 * Update KPI cards with loaded data
 */
function updateKPICards() {
    if (!dashboardData || !dashboardData.kpis) return;
    
    const kpis = dashboardData.kpis;
    
    // Format currency values
    const formatCurrency = (value) => {
        if (value >= 1000000) {
            return `$${(value / 1000000).toFixed(2)}M`;
        } else if (value >= 1000) {
            return `$${(value / 1000).toFixed(2)}K`;
        } else {
            return `$${value.toFixed(2)}`;
        }
    };
    
    // Update KPI cards
    document.getElementById('active-projects').textContent = kpis.active_projects;
    document.getElementById('active-projects-prev').textContent = kpis.active_projects;
    
    document.getElementById('planned-cost').textContent = formatCurrency(kpis.planned_cost);
    document.getElementById('planned-cost-prev').textContent = formatCurrency(kpis.planned_cost);
    
    document.getElementById('planned-benefits').textContent = formatCurrency(kpis.planned_benefits);
    document.getElementById('planned-benefits-prev').textContent = formatCurrency(kpis.planned_benefits);
    
    document.getElementById('estimate-at-completion').textContent = formatCurrency(kpis.estimate_at_completion);
    document.getElementById('estimate-at-completion-prev').textContent = formatCurrency(kpis.estimate_at_completion);
    
    document.getElementById('actual-cost').textContent = formatCurrency(kpis.actual_cost);
    document.getElementById('actual-cost-prev').textContent = formatCurrency(kpis.actual_cost);
    
    document.getElementById('actual-benefits').textContent = formatCurrency(kpis.actual_benefits);
    document.getElementById('actual-benefits-prev').textContent = formatCurrency(kpis.actual_benefits);
}

/**
 * Create all charts
 */
function createAllCharts() {
    createBenefitPlansChart();
    createPlannedBenefitsChart();
    createBusinessUnitChart();
    createInvestmentTypeChart();
    createInvestmentClassChart();
    createPriorityChart();
}

/**
 * Create benefit plans by category donut chart
 */
function createBenefitPlansChart() {
    const ctx = document.getElementById('benefitPlansChart');
    if (!ctx || !dashboardData) return;
    
    const chartData = dashboardData.charts.benefit_plans_by_category;
    
    charts.benefitPlans = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}

/**
 * Create projects planned benefits by category horizontal bar chart
 */
function createPlannedBenefitsChart() {
    const ctx = document.getElementById('plannedBenefitsChart');
    if (!ctx || !dashboardData) return;
    
    const chartData = dashboardData.charts.projects_planned_benefits_by_category;
    
    charts.plannedBenefits = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderColor: chartData.colors,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.x;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(2);
                            return context.label + ' = ' + formatCurrency(value) + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Total Planned Benefits'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Create projects by business unit donut chart
 */
function createBusinessUnitChart() {
    const ctx = document.getElementById('businessUnitChart');
    if (!ctx || !dashboardData) return;
    
    const chartData = dashboardData.charts.projects_by_business_unit;
    
    charts.businessUnit = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}

/**
 * Create projects by investment type donut chart
 */
function createInvestmentTypeChart() {
    const ctx = document.getElementById('investmentTypeChart');
    if (!ctx || !dashboardData) return;
    
    const chartData = dashboardData.charts.projects_by_investment_type;
    
    charts.investmentType = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}

/**
 * Create projects by investment class donut chart
 */
function createInvestmentClassChart() {
    const ctx = document.getElementById('investmentClassChart');
    if (!ctx || !dashboardData) return;
    
    const chartData = dashboardData.charts.projects_by_investment_class;
    
    charts.investmentClass = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}

/**
 * Create projects by priority horizontal bar chart
 */
function createPriorityChart() {
    const ctx = document.getElementById('priorityChart');
    if (!ctx || !dashboardData) return;
    
    const chartData = dashboardData.charts.projects_by_priority;
    
    charts.priority = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderColor: chartData.colors,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.x + ' projects';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 10
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Refresh all charts
 */
window.refreshCharts = function() {
    console.log('🔄 Refreshing charts...');
    
    // Destroy existing charts
    Object.values(charts).forEach(chart => {
        if (chart) chart.destroy();
    });
    
    // Reload data and recreate charts
    loadComprehensiveDashboard();
};

/**
 * Format currency helper function
 */
function formatCurrency(value) {
    if (value >= 1000000) {
        return (value / 1000000).toFixed(2) + 'M';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(2) + 'K';
    } else {
        return value.toFixed(2);
    }
}

/**
 * Show/hide loading indicator
 */
function showLoadingIndicator(show) {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.style.display = show ? 'block' : 'none';
    }
}

/**
 * Show error message
 */
function showError(message) {
    alert('Error: ' + message);
}

/**
 * Load AI Analysis
 */
async function loadAIAnalysis() {
    console.log('🤖 Loading AI analysis...');
    
    try {
        // Load comprehensive analysis first
        await loadComprehensiveAnalysis();
        
        // Load other analyses in parallel
        await Promise.all([
            loadHealthAnalysis(),
            loadFinancialAnalysis(),
            loadResourceAnalysis(),
            loadPredictiveAnalysis()
        ]);
        
        console.log('✅ AI analysis loaded successfully');
        
    } catch (error) {
        console.error('❌ Error loading AI analysis:', error);
        showAIAnalysisError('Failed to load AI analysis. Please check if Ollama is running.');
    }
}

/**
 * Load comprehensive AI analysis
 */
async function loadComprehensiveAnalysis() {
    try {
        const response = await fetch('/api/v1/ai-analysis/comprehensive-analysis');
        if (!response.ok) throw new Error('Failed to fetch comprehensive analysis');
        
        aiAnalysisData.comprehensive = await response.json();
        updateComprehensiveAnalysisUI();
        
    } catch (error) {
        console.error('Error loading comprehensive analysis:', error);
        showAIAnalysisError('Comprehensive analysis unavailable');
    }
}

/**
 * Load project health analysis
 */
async function loadHealthAnalysis() {
    try {
        const response = await fetch('/api/v1/ai-analysis/project-health-analysis');
        if (!response.ok) throw new Error('Failed to fetch health analysis');
        
        aiAnalysisData.health = await response.json();
        updateHealthAnalysisUI();
        
    } catch (error) {
        console.error('Error loading health analysis:', error);
        showAIAnalysisError('Health analysis unavailable');
    }
}

/**
 * Load financial analysis
 */
async function loadFinancialAnalysis() {
    try {
        const response = await fetch('/api/v1/ai-analysis/financial-analysis');
        if (!response.ok) throw new Error('Failed to fetch financial analysis');
        
        aiAnalysisData.financial = await response.json();
        updateFinancialAnalysisUI();
        
    } catch (error) {
        console.error('Error loading financial analysis:', error);
        showAIAnalysisError('Financial analysis unavailable');
    }
}

/**
 * Load resource analysis
 */
async function loadResourceAnalysis() {
    try {
        const response = await fetch('/api/v1/ai-analysis/resource-analysis');
        if (!response.ok) throw new Error('Failed to fetch resource analysis');
        
        aiAnalysisData.resource = await response.json();
        updateResourceAnalysisUI();
        
    } catch (error) {
        console.error('Error loading resource analysis:', error);
        showAIAnalysisError('Resource analysis unavailable');
    }
}

/**
 * Load predictive analysis
 */
async function loadPredictiveAnalysis() {
    try {
        const response = await fetch('/api/v1/ai-analysis/predictive-insights');
        if (!response.ok) throw new Error('Failed to fetch predictive analysis');
        
        aiAnalysisData.predictive = await response.json();
        updatePredictiveAnalysisUI();
        
    } catch (error) {
        console.error('Error loading predictive analysis:', error);
        showAIAnalysisError('Predictive analysis unavailable');
    }
}

/**
 * Update comprehensive analysis UI
 */
function updateComprehensiveAnalysisUI() {
    const contentDiv = document.getElementById('comprehensive-analysis-content');
    const insightsDiv = document.getElementById('comprehensive-insights');
    
    if (!aiAnalysisData.comprehensive) return;
    
    const analysis = aiAnalysisData.comprehensive.analysis;
    const dataSummary = aiAnalysisData.comprehensive.data_summary;
    
    // Update main analysis content
    contentDiv.innerHTML = `
        <div class="ai-analysis-success">
            <strong>Strategic Analysis Generated:</strong><br>
            ${formatAnalysisText(analysis)}
        </div>
    `;
    
    // Update insights sidebar
    insightsDiv.innerHTML = `
        <div class="insight-item success">
            <strong>Total Projects:</strong> ${dataSummary.total_projects}
        </div>
        <div class="insight-item success">
            <strong>Active Projects:</strong> ${dataSummary.active_projects}
        </div>
        <div class="insight-item success">
            <strong>Total Budget:</strong> ${formatCurrency(dataSummary.total_budget)}
        </div>
        <div class="insight-item success">
            <strong>Completion Rate:</strong> ${dataSummary.completion_rate}%
        </div>
    `;
}

/**
 * Update health analysis UI
 */
function updateHealthAnalysisUI() {
    const contentDiv = document.getElementById('health-analysis-content');
    const insightsDiv = document.getElementById('health-insights');
    
    if (!aiAnalysisData.health) return;
    
    const analysis = aiAnalysisData.health.analysis;
    const metrics = aiAnalysisData.health.health_metrics;
    
    contentDiv.innerHTML = `
        <div class="ai-analysis-success">
            <strong>Health Assessment:</strong><br>
            ${formatAnalysisText(analysis)}
        </div>
    `;
    
    // Extract risk alerts from analysis
    const riskAlerts = extractRiskAlerts(analysis);
    insightsDiv.innerHTML = riskAlerts.map(alert => `
        <div class="insight-item ${alert.type}">
            <strong>${alert.title}:</strong> ${alert.message}
        </div>
    `).join('');
}

/**
 * Update financial analysis UI
 */
function updateFinancialAnalysisUI() {
    const contentDiv = document.getElementById('financial-analysis-content');
    const insightsDiv = document.getElementById('financial-insights');
    
    if (!aiAnalysisData.financial) return;
    
    const analysis = aiAnalysisData.financial.analysis;
    const metrics = aiAnalysisData.financial.financial_metrics;
    
    contentDiv.innerHTML = `
        <div class="ai-analysis-success">
            <strong>Financial Analysis:</strong><br>
            ${formatAnalysisText(analysis)}
        </div>
    `;
    
    // Extract ROI insights
    const roiInsights = extractROIInsights(analysis);
    insightsDiv.innerHTML = roiInsights.map(insight => `
        <div class="insight-item ${insight.type}">
            <strong>${insight.title}:</strong> ${insight.message}
        </div>
    `).join('');
}

/**
 * Update resource analysis UI
 */
function updateResourceAnalysisUI() {
    const contentDiv = document.getElementById('resource-analysis-content');
    const insightsDiv = document.getElementById('resource-insights');
    
    if (!aiAnalysisData.resource) return;
    
    const analysis = aiAnalysisData.resource.analysis;
    
    contentDiv.innerHTML = `
        <div class="ai-analysis-success">
            <strong>Resource Analysis:</strong><br>
            ${formatAnalysisText(analysis)}
        </div>
    `;
    
    // Extract optimization tips
    const optimizationTips = extractOptimizationTips(analysis);
    insightsDiv.innerHTML = optimizationTips.map(tip => `
        <div class="insight-item ${tip.type}">
            <strong>${tip.title}:</strong> ${tip.message}
        </div>
    `).join('');
}

/**
 * Update predictive analysis UI
 */
function updatePredictiveAnalysisUI() {
    const contentDiv = document.getElementById('predictive-analysis-content');
    const insightsDiv = document.getElementById('predictive-insights');
    
    if (!aiAnalysisData.predictive) return;
    
    const predictions = aiAnalysisData.predictive.predictions;
    const metrics = aiAnalysisData.predictive.predictive_metrics;
    
    contentDiv.innerHTML = `
        <div class="ai-analysis-success">
            <strong>Predictive Insights:</strong><br>
            ${formatAnalysisText(predictions)}
        </div>
    `;
    
    // Extract forecasts
    const forecasts = extractForecasts(predictions);
    insightsDiv.innerHTML = forecasts.map(forecast => `
        <div class="insight-item ${forecast.type}">
            <strong>${forecast.title}:</strong> ${forecast.message}
        </div>
    `).join('');
}

/**
 * Refresh AI Analysis
 */
window.refreshAIAnalysis = async function() {
    console.log('🔄 Refreshing AI analysis...');
    
    // Clear existing data
    aiAnalysisData = {
        comprehensive: null,
        health: null,
        financial: null,
        resource: null,
        predictive: null
    };
    
    // Reset UI
    resetAIAnalysisUI();
    
    // Reload analysis
    await loadAIAnalysis();
};

/**
 * Reset AI Analysis UI
 */
function resetAIAnalysisUI() {
    const analysisDivs = [
        'comprehensive-analysis-content',
        'health-analysis-content',
        'financial-analysis-content',
        'resource-analysis-content',
        'predictive-analysis-content'
    ];
    
    const insightsDivs = [
        'comprehensive-insights',
        'health-insights',
        'financial-insights',
        'resource-insights',
        'predictive-insights'
    ];
    
    analysisDivs.forEach(id => {
        const div = document.getElementById(id);
        if (div) {
            div.innerHTML = '<div class="text-center text-muted py-4"><i class="fas fa-spinner fa-spin me-2"></i>Loading AI analysis...</div>';
        }
    });
    
    insightsDivs.forEach(id => {
        const div = document.getElementById(id);
        if (div) {
            div.innerHTML = '<div class="text-center text-muted py-2"><small>Loading insights...</small></div>';
        }
    });
}

/**
 * Format analysis text for display - now handles HTML directly
 */
function formatAnalysisText(text) {
    if (!text) return 'No analysis available';
    
    // Since we're now generating HTML directly, just return the text
    // The text already contains proper HTML structure
    return text;
}

/**
 * Extract risk alerts from analysis text
 */
function extractRiskAlerts(analysis) {
    // Simple extraction - in a real implementation, you'd use NLP
    const alerts = [];
    
    // Extract health score from analysis
    const healthScoreMatch = analysis.match(/health score: (\d+\.?\d*)%/);
    if (healthScoreMatch) {
        const score = parseFloat(healthScoreMatch[1]);
        if (score >= 90) {
            alerts.push({
                type: 'success',
                title: 'Excellent Health',
                message: `Portfolio health score: ${score}% - All systems green`
            });
        } else if (score >= 70) {
            alerts.push({
                type: 'info',
                title: 'Good Health',
                message: `Portfolio health score: ${score}% - Minor attention needed`
            });
        } else {
            alerts.push({
                type: 'warning',
                title: 'Health Alert',
                message: `Portfolio health score: ${score}% - Requires attention`
            });
        }
    }
    
    // Extract at-risk projects
    const atRiskMatch = analysis.match(/(\d+) at-risk initiatives/);
    if (atRiskMatch) {
        const atRisk = parseInt(atRiskMatch[1]);
        if (atRisk > 0) {
            alerts.push({
                type: 'danger',
                title: 'At-Risk Projects',
                message: `${atRisk} projects require immediate attention`
            });
        } else {
            alerts.push({
                type: 'success',
                title: 'No At-Risk Projects',
                message: 'All projects are on track'
            });
        }
    }
    
    return alerts.length > 0 ? alerts : [{
        type: 'info',
        title: 'Health Assessment',
        message: 'Project health analysis completed'
    }];
}

/**
 * Extract ROI insights from analysis text
 */
function extractROIInsights(analysis) {
    const insights = [];
    
    // Extract ROI performance
    const roiMatch = analysis.match(/ROI Performance: ([\d.-]+)% \(([^)]+)\)/);
    if (roiMatch) {
        const roi = parseFloat(roiMatch[1]);
        const status = roiMatch[2];
        insights.push({
            type: roi >= 10 ? 'success' : roi >= 0 ? 'info' : 'warning',
            title: 'ROI Performance',
            message: `${roi}% ROI (${status})`
        });
    }
    
    // Extract budget variance
    const budgetMatch = analysis.match(/Budget Variance: ([\d.-]+)% \(([^)]+)\)/);
    if (budgetMatch) {
        const variance = parseFloat(budgetMatch[1]);
        const status = budgetMatch[2];
        insights.push({
            type: Math.abs(variance) <= 5 ? 'success' : Math.abs(variance) <= 15 ? 'info' : 'warning',
            title: 'Budget Variance',
            message: `${variance}% (${status})`
        });
    }
    
    // Extract total investment
    const investmentMatch = analysis.match(/Total investment: \$([\d,]+)/);
    if (investmentMatch) {
        const investment = investmentMatch[1];
        insights.push({
            type: 'info',
            title: 'Total Investment',
            message: `$${investment} portfolio value`
        });
    }
    
    return insights.length > 0 ? insights : [{
        type: 'info',
        title: 'Financial Analysis',
        message: 'Financial performance analysis completed'
    }];
}

/**
 * Extract optimization tips from analysis text
 */
function extractOptimizationTips(analysis) {
    const tips = [];
    
    // Extract resource efficiency
    const efficiencyMatch = analysis.match(/Resource Efficiency: ([\d.]+)% \(([^)]+)\)/);
    if (efficiencyMatch) {
        const efficiency = parseFloat(efficiencyMatch[1]);
        const status = efficiencyMatch[2];
        tips.push({
            type: efficiency >= 80 ? 'success' : efficiency >= 60 ? 'info' : 'warning',
            title: 'Resource Efficiency',
            message: `${efficiency}% efficiency (${status})`
        });
    }
    
    // Extract business unit coverage
    const unitsMatch = analysis.match(/Business Unit Coverage: (\d+) units/);
    if (unitsMatch) {
        const units = parseInt(unitsMatch[1]);
        tips.push({
            type: 'info',
            title: 'Business Units',
            message: `${units} business units covered`
        });
    }
    
    // Extract project density
    const densityMatch = analysis.match(/Project Density: ([\d.]+) projects per unit/);
    if (densityMatch) {
        const density = parseFloat(densityMatch[1]);
        tips.push({
            type: density <= 20 ? 'success' : density <= 30 ? 'info' : 'warning',
            title: 'Workload Distribution',
            message: `${density} projects per business unit`
        });
    }
    
    return tips.length > 0 ? tips : [{
        type: 'info',
        title: 'Resource Analysis',
        message: 'Resource utilization analysis completed'
    }];
}

/**
 * Extract forecasts from analysis text
 */
function extractForecasts(analysis) {
    const forecasts = [];
    
    // Extract success rate
    const successMatch = analysis.match(/Success Rate: ([\d.]+)% \(([^)]+)\)/);
    if (successMatch) {
        const success = parseFloat(successMatch[1]);
        const outlook = successMatch[2];
        forecasts.push({
            type: success >= 80 ? 'success' : success >= 60 ? 'info' : 'warning',
            title: 'Success Rate',
            message: `${success}% (${outlook} probability)`
        });
    }
    
    // Extract completion forecast
    const completionMatch = analysis.match(/Completion Forecast: ([\d.]+)% \(([^)]+)\)/);
    if (completionMatch) {
        const completion = parseFloat(completionMatch[1]);
        const status = completionMatch[2];
        forecasts.push({
            type: completion >= 80 ? 'success' : completion >= 60 ? 'info' : 'warning',
            title: 'Completion Forecast',
            message: `${completion}% (${status})`
        });
    }
    
    // Extract timeline risk
    const riskMatch = analysis.match(/Timeline Risk: ([^-\n]+)/);
    if (riskMatch) {
        const risk = riskMatch[1].trim();
        forecasts.push({
            type: risk === 'Low' ? 'success' : risk === 'Moderate' ? 'info' : 'warning',
            title: 'Timeline Risk',
            message: `${risk} risk level`
        });
    }
    
    return forecasts.length > 0 ? forecasts : [{
        type: 'info',
        title: 'Predictive Analysis',
        message: 'Predictive insights analysis completed'
    }];
}

/**
 * Show AI analysis error
 */
function showAIAnalysisError(message) {
    const errorDivs = [
        'comprehensive-analysis-content',
        'health-analysis-content',
        'financial-analysis-content',
        'resource-analysis-content',
        'predictive-analysis-content'
    ];
    
    errorDivs.forEach(id => {
        const div = document.getElementById(id);
        if (div && div.innerHTML.includes('Loading')) {
            div.innerHTML = `
                <div class="ai-analysis-error">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${message}
                </div>
            `;
        }
    });
}

/**
 * Initialize dashboard when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Comprehensive dashboard initialized');
    console.log('📊 Available charts: Benefit Plans, Planned Benefits, Business Unit, Investment Type, Investment Class, Priority');
    console.log('💰 KPI metrics: Active Projects, Planned Cost, Planned Benefits, Estimate at Completion, Actual Cost, Actual Benefits');
    console.log('🤖 AI Analysis: Strategic Overview, Project Health, Financial Insights, Resource Analysis, Predictive Insights');
    
    // Auto-load dashboard data
    loadComprehensiveDashboard();
    
    // Initialize new tab functionality
    initializeNewTabs();
});

/**
 * Initialize new tab functionality
 */
function initializeNewTabs() {
    console.log('🔄 Initializing new tab functionality...');
    
    // Set up tab click handlers
    const tabs = ['pipeline', 'health', 'quality', 'actuals', 'calendar'];
    tabs.forEach(tabId => {
        const tabElement = document.getElementById(`${tabId}-tab`);
        if (tabElement) {
            tabElement.addEventListener('click', () => {
                loadTabData(tabId);
            });
        }
    });
}

/**
 * Load data for specific tab
 */
async function loadTabData(tabId) {
    console.log(`📊 Loading data for ${tabId} tab...`);
    
    try {
        switch(tabId) {
            case 'pipeline':
                await loadPipelineData();
                break;
            case 'health':
                await loadHealthData();
                break;
            case 'quality':
                await loadQualityData();
                break;
            case 'actuals':
                await loadActualsData();
                break;
            case 'calendar':
                await loadCalendarData();
                break;
        }
    } catch (error) {
        console.error(`❌ Error loading ${tabId} data:`, error);
    }
}

/**
 * Load Pipeline tab data
 */
async function loadPipelineData() {
    const pipelineTableBody = document.getElementById('pipelineTableBody');
    if (pipelineTableBody && dashboardData) {
        const projects = dashboardData.charts?.projects_by_business_unit?.data || [];
        const businessUnits = dashboardData.charts?.projects_by_business_unit?.labels || [];
        
        let tableHTML = '';
        for (let i = 0; i < Math.min(10, projects.length); i++) {
            const projectId = `P-${String(i + 1).padStart(5, '0')}`;
            const businessUnit = businessUnits[i] || 'IT';
            const status = ['Active', 'In Progress', 'Pending', 'On Hold'][i % 4];
            const progress = Math.floor(Math.random() * 100);
            
            tableHTML += `
                <tr>
                    <td>${projectId}</td>
                    <td>Project ${i + 1}</td>
                    <td>${businessUnit}</td>
                    <td><span class="badge bg-primary">${status}</span></td>
                    <td>2024-01-01</td>
                    <td>2024-12-31</td>
                    <td>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar" style="width: ${progress}%"></div>
                        </div>
                        <small>${progress}%</small>
                    </td>
                </tr>
            `;
        }
        pipelineTableBody.innerHTML = tableHTML;
    }
    createPipelineCharts();
}

/**
 * Load Health tab data
 */
async function loadHealthData() {
    const healthTableBody = document.getElementById('healthTableBody');
    if (healthTableBody) {
        let tableHTML = '';
        for (let i = 1; i <= 10; i++) {
            const projectId = `P-${String(i).padStart(5, '0')}`;
            const healthScore = Math.floor(Math.random() * 40) + 60;
            const status = healthScore > 80 ? 'Healthy' : healthScore > 60 ? 'At Risk' : 'Critical';
            const statusClass = healthScore > 80 ? 'success' : healthScore > 60 ? 'warning' : 'danger';
            
            tableHTML += `
                <tr>
                    <td>${projectId}</td>
                    <td>Project ${i}</td>
                    <td>${healthScore}%</td>
                    <td><span class="badge bg-${statusClass}">${status}</span></td>
                    <td><span class="badge bg-success">Good</span></td>
                    <td><span class="badge bg-info">On Track</span></td>
                    <td><span class="badge bg-primary">High</span></td>
                    <td><button class="btn btn-sm btn-outline-primary">View</button></td>
                </tr>
            `;
        }
        healthTableBody.innerHTML = tableHTML;
    }
    createHealthCharts();
}

/**
 * Load Quality tab data
 */
async function loadQualityData() {
    const qualityTableBody = document.getElementById('qualityTableBody');
    if (qualityTableBody) {
        const issues = [
            { type: 'Missing Data', severity: 'High', description: 'Project manager not assigned', impact: 'High' },
            { type: 'Data Inconsistency', severity: 'Medium', description: 'Budget amounts don\'t match', impact: 'Medium' },
            { type: 'Outdated Information', severity: 'Low', description: 'Last updated 30+ days ago', impact: 'Low' },
            { type: 'Validation Error', severity: 'High', description: 'Invalid date format', impact: 'High' }
        ];
        
        let tableHTML = '';
        issues.forEach((issue, index) => {
            const projectId = `P-${String(index + 1).padStart(5, '0')}`;
            const severityClass = issue.severity === 'High' ? 'danger' : issue.severity === 'Medium' ? 'warning' : 'info';
            const status = ['Open', 'In Progress', 'Resolved'][index % 3];
            const statusClass = status === 'Resolved' ? 'success' : status === 'In Progress' ? 'warning' : 'secondary';
            
            tableHTML += `
                <tr>
                    <td>${projectId}</td>
                    <td>${issue.type}</td>
                    <td><span class="badge bg-${severityClass}">${issue.severity}</span></td>
                    <td>${issue.description}</td>
                    <td>${issue.impact}</td>
                    <td><span class="badge bg-${statusClass}">${status}</span></td>
                    <td><button class="btn btn-sm btn-outline-primary">Fix</button></td>
                </tr>
            `;
        });
        qualityTableBody.innerHTML = tableHTML;
    }
    createQualityCharts();
}

/**
 * Load Actuals tab data
 */
async function loadActualsData() {
    const actualsTableBody = document.getElementById('actualsTableBody');
    if (actualsTableBody) {
        let tableHTML = '';
        for (let i = 1; i <= 10; i++) {
            const projectId = `P-${String(i).padStart(5, '0')}`;
            const plannedCost = Math.floor(Math.random() * 1000000) + 500000;
            const actualCost = Math.floor(plannedCost * (0.7 + Math.random() * 0.6));
            const variance = ((actualCost - plannedCost) / plannedCost * 100).toFixed(1);
            const plannedBenefits = Math.floor(plannedCost * (1.2 + Math.random() * 0.8));
            const actualBenefits = Math.floor(plannedBenefits * (0.5 + Math.random() * 0.8));
            const roi = ((actualBenefits - actualCost) / actualCost * 100).toFixed(1);
            
            tableHTML += `
                <tr>
                    <td>${projectId}</td>
                    <td>Project ${i}</td>
                    <td>$${plannedCost.toLocaleString()}</td>
                    <td>$${actualCost.toLocaleString()}</td>
                    <td class="${variance < 0 ? 'text-success' : 'text-danger'}">${variance}%</td>
                    <td>$${plannedBenefits.toLocaleString()}</td>
                    <td>$${actualBenefits.toLocaleString()}</td>
                    <td class="${roi > 0 ? 'text-success' : 'text-danger'}">${roi}%</td>
                </tr>
            `;
        }
        actualsTableBody.innerHTML = tableHTML;
    }
    createActualsCharts();
}

/**
 * Load Calendar tab data
 */
async function loadCalendarData() {
    console.log('📅 Loading calendar data...');
    
    // Initialize calendar
    initializeCalendar();
    
    // Load calendar events
    await loadCalendarEvents();
    
    // Render calendar
    renderCalendar();
}

// Calendar state
let calendarState = {
    currentDate: new Date(),
    events: [],
    view: 'month'
};

// Dashboard filter state
let dashboardFilters = {
    businessUnit: '',
    dataView: '',
    timeRange: '',
    status: ''
};

/**
 * Initialize calendar functionality
 */
function initializeCalendar() {
    console.log('🗓️ Initializing calendar...');
    
    // Set current date to today
    calendarState.currentDate = new Date();
    
    // Create tooltip element
    if (!document.getElementById('calendar-tooltip')) {
        const tooltip = document.createElement('div');
        tooltip.id = 'calendar-tooltip';
        tooltip.className = 'calendar-event-tooltip';
        document.body.appendChild(tooltip);
    }
}

/**
 * Load calendar events from project data
 */
async function loadCalendarEvents() {
    console.log('📅 Loading calendar events...');
    
    // Generate sample events based on project data
    const events = [];
    const today = new Date();
    
    // Generate events for the next 3 months
    for (let i = 0; i < 90; i++) {
        const eventDate = new Date(today);
        eventDate.setDate(today.getDate() + i);
        
        // Randomly generate events
        if (Math.random() < 0.3) { // 30% chance of event per day
            const eventTypes = ['milestone', 'deadline', 'review', 'meeting'];
            const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
            const projectId = `P-${String(Math.floor(Math.random() * 10) + 1).padStart(5, '0')}`;
            
            const eventTitles = {
                'milestone': ['Phase Completion', 'Sprint Review', 'Feature Release', 'Testing Complete'],
                'deadline': ['Project Deadline', 'Budget Review', 'Documentation Due', 'Final Delivery'],
                'review': ['Code Review', 'Design Review', 'Performance Review', 'Security Audit'],
                'meeting': ['Stakeholder Meeting', 'Team Standup', 'Planning Session', 'Retrospective']
            };
            
            const title = eventTitles[eventType][Math.floor(Math.random() * eventTitles[eventType].length)];
            
            events.push({
                id: `event-${i}`,
                title: `${projectId}: ${title}`,
                date: eventDate,
                type: eventType,
                projectId: projectId,
                description: `${title} for ${projectId}`,
                overdue: eventDate < today && Math.random() < 0.1 // 10% chance of being overdue
            });
        }
    }
    
    calendarState.events = events;
    console.log(`📅 Loaded ${events.length} calendar events`);
}

/**
 * Render the calendar
 */
function renderCalendar() {
    console.log('🗓️ Rendering calendar...');
    
    const calendarDays = document.getElementById('calendar-days');
    if (!calendarDays) return;
    
    const year = calendarState.currentDate.getFullYear();
    const month = calendarState.currentDate.getMonth();
    
    // Update month/year display
    const monthYearElement = document.getElementById('calendar-month-year');
    if (monthYearElement) {
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December'];
        monthYearElement.textContent = `${monthNames[month]} ${year}`;
    }
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    // Clear existing calendar
    calendarDays.innerHTML = '';
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
        const prevMonthDay = new Date(year, month, -startingDayOfWeek + i + 1);
        const dayElement = createDayElement(prevMonthDay.getDate(), true, prevMonthDay);
        calendarDays.appendChild(dayElement);
    }
    
    // Add days of the current month
    for (let day = 1; day <= daysInMonth; day++) {
        const currentDate = new Date(year, month, day);
        const dayElement = createDayElement(day, false, currentDate);
        calendarDays.appendChild(dayElement);
    }
    
    // Add empty cells for days after the last day of the month
    const totalCells = calendarDays.children.length;
    const remainingCells = 42 - totalCells; // 6 weeks * 7 days = 42 cells
    for (let i = 1; i <= remainingCells; i++) {
        const nextMonthDay = new Date(year, month + 1, i);
        const dayElement = createDayElement(i, true, nextMonthDay);
        calendarDays.appendChild(dayElement);
    }
}

/**
 * Create a day element for the calendar
 */
function createDayElement(dayNumber, isOtherMonth, date) {
    const dayElement = document.createElement('div');
    dayElement.className = 'calendar-day';
    
    if (isOtherMonth) {
        dayElement.classList.add('other-month');
    }
    
    // Check if it's today
    const today = new Date();
    if (date.toDateString() === today.toDateString()) {
        dayElement.classList.add('today');
    }
    
    // Get events for this day
    const dayEvents = calendarState.events.filter(event => 
        event.date.toDateString() === date.toDateString()
    );
    
    if (dayEvents.length > 0) {
        dayElement.classList.add('has-events');
    }
    
    // Create day content
    const dayNumberElement = document.createElement('div');
    dayNumberElement.className = 'calendar-day-number';
    dayNumberElement.textContent = dayNumber;
    dayElement.appendChild(dayNumberElement);
    
    // Add events
    if (dayEvents.length > 0) {
        const eventsContainer = document.createElement('div');
        eventsContainer.className = 'calendar-events';
        
        dayEvents.slice(0, 3).forEach(event => { // Show max 3 events per day
            const eventElement = document.createElement('div');
            eventElement.className = `calendar-event ${event.type}`;
            if (event.overdue) {
                eventElement.classList.add('calendar-event-overdue');
            }
            
            // Add tooltip functionality
            eventElement.addEventListener('mouseenter', (e) => showEventTooltip(e, event));
            eventElement.addEventListener('mouseleave', hideEventTooltip);
            
            eventsContainer.appendChild(eventElement);
        });
        
        if (dayEvents.length > 3) {
            const moreElement = document.createElement('div');
            moreElement.className = 'calendar-event';
            moreElement.style.backgroundColor = '#6c757d';
            moreElement.title = `+${dayEvents.length - 3} more events`;
            eventsContainer.appendChild(moreElement);
        }
        
        dayElement.appendChild(eventsContainer);
    }
    
    // Add click functionality
    dayElement.addEventListener('click', () => showDayDetails(date, dayEvents));
    
    return dayElement;
}

/**
 * Show event tooltip
 */
function showEventTooltip(event, eventData) {
    const tooltip = document.getElementById('calendar-tooltip');
    if (!tooltip) return;
    
    tooltip.innerHTML = `
        <strong>${eventData.title}</strong><br>
        <small>${eventData.type.charAt(0).toUpperCase() + eventData.type.slice(1)}</small><br>
        <small>${eventData.description}</small>
    `;
    
    tooltip.classList.add('show');
    
    // Position tooltip
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
}

/**
 * Hide event tooltip
 */
function hideEventTooltip() {
    const tooltip = document.getElementById('calendar-tooltip');
    if (tooltip) {
        tooltip.classList.remove('show');
    }
}

/**
 * Show day details modal
 */
function showDayDetails(date, events) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${date.toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    })}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${events.length === 0 ? 
                        '<p class="text-muted">No events scheduled for this day.</p>' :
                        events.map(event => `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h6 class="card-title">${event.title}</h6>
                                    <p class="card-text">${event.description}</p>
                                    <span class="badge bg-${getEventBadgeColor(event.type)}">${event.type}</span>
                                    ${event.overdue ? '<span class="badge bg-danger ms-2">Overdue</span>' : ''}
                                </div>
                            </div>
                        `).join('')
                    }
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

/**
 * Get badge color for event type
 */
function getEventBadgeColor(type) {
    const colors = {
        'milestone': 'primary',
        'deadline': 'success',
        'review': 'warning',
        'meeting': 'info'
    };
    return colors[type] || 'secondary';
}

/**
 * Create Pipeline Charts
 */
function createPipelineCharts() {
    const pipelineBusinessCtx = document.getElementById('pipelineBusinessUnitChart');
    if (pipelineBusinessCtx && dashboardData) {
        const data = dashboardData.charts?.projects_by_business_unit;
        if (data) {
            new Chart(pipelineBusinessCtx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: data.colors,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
    
    const pipelineInvestmentCtx = document.getElementById('pipelineInvestmentChart');
    if (pipelineInvestmentCtx && dashboardData) {
        const data = dashboardData.charts?.projects_by_investment_type;
        if (data) {
            new Chart(pipelineInvestmentCtx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Projects',
                        data: data.data,
                        backgroundColor: data.colors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
}

/**
 * Create Health Charts
 */
function createHealthCharts() {
    const healthDistCtx = document.getElementById('healthDistributionChart');
    if (healthDistCtx) {
        new Chart(healthDistCtx, {
            type: 'pie',
            data: {
                labels: ['Healthy', 'At Risk', 'Critical'],
                datasets: [{
                    data: [98, 24, 12],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    const healthTrendsCtx = document.getElementById('healthTrendsChart');
    if (healthTrendsCtx) {
        new Chart(healthTrendsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Health Score',
                    data: [82, 85, 88, 86, 89, 85],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

/**
 * Create Quality Charts
 */
function createQualityCharts() {
    const qualityTrendsCtx = document.getElementById('qualityTrendsChart');
    if (qualityTrendsCtx) {
        new Chart(qualityTrendsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Data Quality %',
                    data: [85, 87, 89, 88, 90, 88],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    const qualityIssuesCtx = document.getElementById('qualityIssuesChart');
    if (qualityIssuesCtx) {
        new Chart(qualityIssuesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Missing Data', 'Data Inconsistency', 'Outdated Info', 'Validation Errors'],
                datasets: [{
                    data: [35, 25, 20, 20],
                    backgroundColor: ['#dc3545', '#ffc107', '#17a2b8', '#6f42c1'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

/**
 * Create Actuals Charts
 */
function createActualsCharts() {
    const costBudgetCtx = document.getElementById('costBudgetChart');
    if (costBudgetCtx) {
        new Chart(costBudgetCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Planned Cost',
                    data: [12000000, 15000000, 18000000, 20000000, 22000000, 25000000],
                    backgroundColor: 'rgba(0, 123, 255, 0.8)',
                    borderColor: '#007bff',
                    borderWidth: 1
                }, {
                    label: 'Actual Cost',
                    data: [8000000, 10000000, 12000000, 14000000, 16000000, 18000000],
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: '#28a745',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000000) + 'M';
                            }
                        }
                    }
                }
            }
        });
    }
    
    const benefitsCtx = document.getElementById('benefitsChart');
    if (benefitsCtx) {
        new Chart(benefitsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Planned Benefits',
                    data: [15000000, 18000000, 22000000, 25000000, 28000000, 30000000],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: false
                }, {
                    label: 'Actual Benefits',
                    data: [10000000, 12000000, 15000000, 18000000, 20000000, 22000000],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000000) + 'M';
                            }
                        }
                    }
                }
            }
        });
    }
}

/**
 * Calendar view change handler
 */
window.changeCalendarView = function(view) {
    console.log(`📅 Changing calendar view to: ${view}`);
    calendarState.view = view;
    
    // Update active button
    document.querySelectorAll('.btn-group button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // For now, we only support month view
    // This can be extended to support week and day views
    if (view === 'month') {
        renderCalendar();
    } else {
        alert(`${view} view coming soon! Currently showing month view.`);
    }
};

/**
 * Change calendar month
 */
window.changeCalendarMonth = function(direction) {
    console.log(`📅 Changing calendar month: ${direction}`);
    
    const currentDate = calendarState.currentDate;
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    
    calendarState.currentDate = newDate;
    renderCalendar();
};

/**
 * Go to today
 */
window.goToToday = function() {
    console.log('📅 Going to today');
    
    calendarState.currentDate = new Date();
    renderCalendar();
};

/**
 * Filter by Business Unit
 */
window.filterByBusinessUnit = function() {
    const businessUnit = document.getElementById('businessUnit').value;
    dashboardFilters.businessUnit = businessUnit;
    
    console.log(`🏢 Filtering by Business Unit: ${businessUnit}`);
    
    // Apply filter to dashboard data
    applyDashboardFilters();
    
    // Update charts and data
    updateFilteredCharts();
    
    // Show filter status
    showFilterStatus();
}

/**
 * Filter by Data View
 */
window.filterByDataView = function() {
    const dataView = document.getElementById('selectElements').value;
    dashboardFilters.dataView = dataView;
    
    console.log(`📊 Filtering by Data View: ${dataView}`);
    
    // Apply filter to dashboard data
    applyDashboardFilters();
    
    // Update charts and data
    updateFilteredCharts();
    
    // Show filter status
    showFilterStatus();
}

/**
 * Filter by Time Range
 */
window.filterByTimeRange = function() {
    const timeRange = document.getElementById('timeRange').value;
    dashboardFilters.timeRange = timeRange;
    
    console.log(`📅 Filtering by Time Range: ${timeRange}`);
    
    // Apply filter to dashboard data
    applyDashboardFilters();
    
    // Update charts and data
    updateFilteredCharts();
    
    // Show filter status
    showFilterStatus();
}

/**
 * Filter by Status
 */
window.filterByStatus = function() {
    const status = document.getElementById('statusFilter').value;
    dashboardFilters.status = status;
    
    console.log(`📋 Filtering by Status: ${status}`);
    
    // Apply filter to dashboard data
    applyDashboardFilters();
    
    // Update charts and data
    updateFilteredCharts();
    
    // Show filter status
    showFilterStatus();
}

/**
 * Apply dashboard filters
 */
function applyDashboardFilters() {
    console.log('🔍 Applying dashboard filters:', dashboardFilters);
    
    // This function will filter the dashboard data based on current filters
    // For now, we'll simulate the filtering effect
    
    // Update KPI cards based on filters
    updateKPICardsWithFilters();
    
    // Update charts based on filters
    updateChartsWithFilters();
    
    // Update tables based on filters
    updateTablesWithFilters();
}

/**
 * Update KPI cards with filters
 */
function updateKPICardsWithFilters() {
    console.log('📊 Updating KPI cards with filters...');
    
    // Get base metrics
    let activeProjects = 134;
    let plannedCost = 142000000;
    let plannedBenefits = 170000000;
    let actualCost = 28600000;
    let actualBenefits = 28100000;
    
    // Apply business unit filter
    if (dashboardFilters.businessUnit) {
        const businessUnitMultiplier = getBusinessUnitMultiplier(dashboardFilters.businessUnit);
        activeProjects = Math.floor(activeProjects * businessUnitMultiplier);
        plannedCost = Math.floor(plannedCost * businessUnitMultiplier);
        plannedBenefits = Math.floor(plannedBenefits * businessUnitMultiplier);
        actualCost = Math.floor(actualCost * businessUnitMultiplier);
        actualBenefits = Math.floor(actualBenefits * businessUnitMultiplier);
    }
    
    // Apply status filter
    if (dashboardFilters.status) {
        const statusMultiplier = getStatusMultiplier(dashboardFilters.status);
        activeProjects = Math.floor(activeProjects * statusMultiplier);
    }
    
    // Update KPI display
    updateKPIDisplay(activeProjects, plannedCost, plannedBenefits, actualCost, actualBenefits);
}

/**
 * Get business unit multiplier for filtering
 */
function getBusinessUnitMultiplier(businessUnit) {
    const multipliers = {
        'IT': 0.35,
        'Legal': 0.08,
        'Finance': 0.15,
        'HR': 0.10,
        'Facilities': 0.12,
        'Sales': 0.15,
        'Operations': 0.20,
        'R&D': 0.25
    };
    return multipliers[businessUnit] || 1.0;
}

/**
 * Get status multiplier for filtering
 */
function getStatusMultiplier(status) {
    const multipliers = {
        'active': 0.70,
        'completed': 0.20,
        'on-hold': 0.05,
        'cancelled': 0.02,
        'planning': 0.15,
        'execution': 0.60
    };
    return multipliers[status] || 1.0;
}

/**
 * Update KPI display
 */
function updateKPIDisplay(activeProjects, plannedCost, plannedBenefits, actualCost, actualBenefits) {
    // Update active projects
    const activeProjectsElement = document.getElementById('active-projects');
    if (activeProjectsElement) {
        activeProjectsElement.textContent = activeProjects.toLocaleString();
    }
    
    // Update planned cost
    const plannedCostElement = document.getElementById('planned-cost');
    if (plannedCostElement) {
        plannedCostElement.textContent = '$' + (plannedCost / 1000000).toFixed(1) + 'M';
    }
    
    // Update planned benefits
    const plannedBenefitsElement = document.getElementById('planned-benefits');
    if (plannedBenefitsElement) {
        plannedBenefitsElement.textContent = '$' + (plannedBenefits / 1000000).toFixed(1) + 'M';
    }
    
    // Update actual cost
    const actualCostElement = document.getElementById('actual-cost');
    if (actualCostElement) {
        actualCostElement.textContent = '$' + (actualCost / 1000000).toFixed(1) + 'M';
    }
    
    // Update actual benefits
    const actualBenefitsElement = document.getElementById('actual-benefits');
    if (actualBenefitsElement) {
        actualBenefitsElement.textContent = '$' + (actualBenefits / 1000000).toFixed(1) + 'M';
    }
}

/**
 * Update charts with filters
 */
function updateChartsWithFilters() {
    console.log('📈 Updating charts with filters...');
    
    // Update business unit chart
    if (charts.businessUnit && dashboardFilters.businessUnit) {
        // Highlight selected business unit
        highlightChartSegment(charts.businessUnit, dashboardFilters.businessUnit);
    }
    
    // Update other charts based on filters
    updateInvestmentTypeChart();
    updatePriorityChart();
}

/**
 * Highlight chart segment
 */
function highlightChartSegment(chart, segmentName) {
    if (chart && chart.data && chart.data.datasets) {
        chart.data.datasets.forEach(dataset => {
            if (dataset.backgroundColor) {
                // Reset all colors
                dataset.backgroundColor = dataset.backgroundColor.map(() => '#6c757d');
                
                // Highlight selected segment
                const segmentIndex = chart.data.labels.indexOf(segmentName);
                if (segmentIndex !== -1) {
                    dataset.backgroundColor[segmentIndex] = '#007bff';
                }
            }
        });
        chart.update();
    }
}

/**
 * Update investment type chart
 */
function updateInvestmentTypeChart() {
    if (charts.investmentType) {
        // Add animation to show filter effect
        charts.investmentType.update('active');
    }
}

/**
 * Update priority chart
 */
function updatePriorityChart() {
    if (charts.priority) {
        // Add animation to show filter effect
        charts.priority.update('active');
    }
}

/**
 * Update tables with filters
 */
function updateTablesWithFilters() {
    console.log('📋 Updating tables with filters...');
    
    // Update pipeline table
    updatePipelineTableWithFilters();
    
    // Update health table
    updateHealthTableWithFilters();
    
    // Update other tables as needed
}

/**
 * Update pipeline table with filters
 */
function updatePipelineTableWithFilters() {
    const pipelineTableBody = document.getElementById('pipelineTableBody');
    if (pipelineTableBody) {
        // Add filter indicator to table rows
        const rows = pipelineTableBody.querySelectorAll('tr');
        rows.forEach(row => {
            const businessUnitCell = row.cells[2]; // Business Unit column
            if (businessUnitCell && dashboardFilters.businessUnit) {
                if (businessUnitCell.textContent.includes(dashboardFilters.businessUnit)) {
                    row.style.backgroundColor = '#e3f2fd';
                    row.style.fontWeight = '600';
                } else {
                    row.style.opacity = '0.5';
                }
            }
        });
    }
}

/**
 * Update health table with filters
 */
function updateHealthTableWithFilters() {
    const healthTableBody = document.getElementById('healthTableBody');
    if (healthTableBody) {
        // Add filter indicator to table rows
        const rows = healthTableBody.querySelectorAll('tr');
        rows.forEach(row => {
            const statusCell = row.cells[3]; // Status column
            if (statusCell && dashboardFilters.status) {
                const statusText = statusCell.textContent.toLowerCase();
                if (statusText.includes(dashboardFilters.status)) {
                    row.style.backgroundColor = '#e3f2fd';
                    row.style.fontWeight = '600';
                } else {
                    row.style.opacity = '0.5';
                }
            }
        });
    }
}

/**
 * Update filtered charts
 */
function updateFilteredCharts() {
    console.log('📊 Updating filtered charts...');
    
    // Refresh all charts with filtered data
    if (charts.benefitPlans) charts.benefitPlans.update();
    if (charts.plannedBenefits) charts.plannedBenefits.update();
    if (charts.businessUnit) charts.businessUnit.update();
    if (charts.investmentType) charts.investmentType.update();
    if (charts.investmentClass) charts.investmentClass.update();
    if (charts.priority) charts.priority.update();
}

/**
 * Show filter status
 */
function showFilterStatus() {
    const activeFilters = Object.entries(dashboardFilters)
        .filter(([key, value]) => value !== '')
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
    
    if (activeFilters) {
        console.log(`🔍 Active filters: ${activeFilters}`);
        
        // Show filter status in UI (optional)
        showFilterStatusBadge(activeFilters);
    } else {
        console.log('🔍 No active filters');
        hideFilterStatusBadge();
    }
}

/**
 * Show filter status badge
 */
function showFilterStatusBadge(filters) {
    let badge = document.getElementById('filter-status-badge');
    if (!badge) {
        badge = document.createElement('div');
        badge.id = 'filter-status-badge';
        badge.className = 'alert alert-info alert-dismissible fade show position-fixed';
        badge.style.top = '20px';
        badge.style.right = '20px';
        badge.style.zIndex = '9999';
        badge.innerHTML = `
            <i class="fas fa-filter me-2"></i>
            <strong>Active Filters:</strong> ${filters}
            <button type="button" class="btn-close" onclick="clearAllFilters()"></button>
        `;
        document.body.appendChild(badge);
    } else {
        badge.innerHTML = `
            <i class="fas fa-filter me-2"></i>
            <strong>Active Filters:</strong> ${filters}
            <button type="button" class="btn-close" onclick="clearAllFilters()"></button>
        `;
    }
}

/**
 * Hide filter status badge
 */
function hideFilterStatusBadge() {
    const badge = document.getElementById('filter-status-badge');
    if (badge) {
        badge.remove();
    }
}

/**
 * Clear all filters
 */
window.clearAllFilters = function() {
    console.log('🧹 Clearing all filters...');
    
    // Reset filter values
    document.getElementById('businessUnit').value = '';
    document.getElementById('selectElements').value = '';
    document.getElementById('timeRange').value = '';
    document.getElementById('statusFilter').value = '';
    
    // Reset filter state
    dashboardFilters = {
        businessUnit: '',
        dataView: '',
        timeRange: '',
        status: ''
    };
    
    // Reload dashboard data
    loadComprehensiveDashboard();
    
    // Hide filter status
    hideFilterStatusBadge();
};

// Export functions for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadComprehensiveDashboard: window.loadComprehensiveDashboard,
        refreshCharts: window.refreshCharts
    };
}
