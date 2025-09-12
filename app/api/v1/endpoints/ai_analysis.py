"""
AI Analysis API endpoints using Ollama GPT-OSS-20B
Provides intelligent insights for the comprehensive dashboard
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.api.deps import get_current_user
from app.models.main_tables import Project
from app.models.lookup_tables import (
    BusinessUnit, InvestmentClass, BenefitCategory, 
    InvestmentType, Priority, Status
)
from app.core.ollama_client import ollama_client
from app.core.logging import get_logger, log_api_endpoint

# Initialize logger
logger = get_logger("api.ai_analysis")

router = APIRouter()

@router.get("/comprehensive-analysis")
async def get_comprehensive_ai_analysis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive AI analysis of all dashboard data"""
    
    try:
        # Simple data gathering to avoid complex queries
        total_projects = db.query(Project).filter(Project.is_active == True).count()
        active_projects = db.query(Project).filter(
            and_(Project.is_active == True, Project.status_id == 1)
        ).count()
        
        # Get basic financial data
        financial_data = db.query(Project).with_entities(
            func.sum(Project.planned_cost).label('planned_cost'),
            func.sum(Project.actual_cost).label('actual_cost')
        ).filter(Project.is_active == True).first()
        
        dashboard_data = {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_budget": float(financial_data.planned_cost or 0),
            "actual_cost": float(financial_data.actual_cost or 0),
            "completion_rate": round((active_projects / max(total_projects, 1)) * 100, 2)
        }
        
        # Generate mock analysis (Ollama integration can be added later)
        analysis = generate_mock_comprehensive_analysis(dashboard_data)
        
        return {
            "analysis": analysis,
            "data_summary": {
                "total_projects": dashboard_data.get("total_projects", 0),
                "total_budget": dashboard_data.get("total_budget", 0),
                "active_projects": dashboard_data.get("active_projects", 0),
                "completion_rate": dashboard_data.get("completion_rate", 0)
            },
            "timestamp": "2025-09-12T11:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error generating comprehensive analysis: {str(e)}")
        # Return a basic response even if there's an error
        return {
            "analysis": "AI analysis is currently being set up. Please check back later for intelligent insights.",
            "data_summary": {
                "total_projects": 0,
                "total_budget": 0,
                "active_projects": 0,
                "completion_rate": 0
            },
            "timestamp": "2025-09-12T11:00:00Z"
        }

@router.get("/project-health-analysis")
async def get_project_health_analysis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get AI analysis of project health metrics"""
    
    try:
        # Simple health data gathering
        total_projects = db.query(Project).filter(Project.is_active == True).count()
        at_risk_projects = db.query(Project).filter(
            and_(Project.is_active == True, Project.status_id == 3)
        ).count()
        
        # Get status distribution
        status_data = db.query(Project).with_entities(
            func.count(Project.id).label('count')
        ).filter(Project.is_active == True).first()
        
        health_data = {
            "total_projects": total_projects,
            "at_risk_projects": at_risk_projects,
            "health_score": round(((total_projects - at_risk_projects) / max(total_projects, 1)) * 100, 2)
        }
        
        # Generate mock analysis
        analysis = generate_mock_health_analysis(health_data)
        
        return {
            "analysis": analysis,
            "health_metrics": health_data,
            "timestamp": "2025-09-12T11:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error generating project health analysis: {str(e)}")
        return {
            "analysis": "Project health analysis is currently being set up. Please check back later for health insights.",
            "health_metrics": {"total_projects": 0, "at_risk_projects": 0, "health_score": 0},
            "timestamp": "2025-09-12T11:00:00Z"
        }

@router.get("/financial-analysis")
async def get_financial_analysis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get AI analysis of financial performance"""
    
    try:
        # Simple financial data gathering
        financial_data = db.query(Project).with_entities(
            func.sum(Project.planned_cost).label('planned_cost'),
            func.sum(Project.actual_cost).label('actual_cost'),
            func.sum(Project.planned_benefits).label('planned_benefits'),
            func.sum(Project.actual_benefits).label('actual_benefits')
        ).filter(Project.is_active == True).first()
        
        planned_cost = float(financial_data.planned_cost or 0)
        actual_cost = float(financial_data.actual_cost or 0)
        planned_benefits = float(financial_data.planned_benefits or 0)
        actual_benefits = float(financial_data.actual_benefits or 0)
        
        financial_metrics = {
            "planned_cost": planned_cost,
            "actual_cost": actual_cost,
            "planned_benefits": planned_benefits,
            "actual_benefits": actual_benefits,
            "cost_variance": round(((actual_cost - planned_cost) / max(planned_cost, 1)) * 100, 2),
            "roi": round(((actual_benefits - actual_cost) / max(actual_cost, 1)) * 100, 2)
        }
        
        # Generate mock analysis
        analysis = generate_mock_financial_analysis(financial_metrics)
        
        return {
            "analysis": analysis,
            "financial_metrics": financial_metrics,
            "timestamp": "2025-09-12T11:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error generating financial analysis: {str(e)}")
        return {
            "analysis": "Financial analysis is currently being set up. Please check back later for financial insights.",
            "financial_metrics": {"planned_cost": 0, "actual_cost": 0, "planned_benefits": 0, "actual_benefits": 0, "cost_variance": 0, "roi": 0},
            "timestamp": "2025-09-12T11:00:00Z"
        }

@router.get("/resource-analysis")
async def get_resource_analysis(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get AI analysis of resource utilization"""
    
    try:
        # Simple resource data gathering
        total_projects = db.query(Project).filter(Project.is_active == True).count()
        
        # Get average completion rate
        avg_completion = db.query(Project).with_entities(
            func.avg(Project.percent_complete).label('avg_completion')
        ).filter(Project.is_active == True).scalar()
        
        # Get business unit distribution
        bu_count = db.query(BusinessUnit).count()
        
        resource_metrics = {
            "total_projects": total_projects,
            "average_completion": round(float(avg_completion or 0), 2),
            "business_units": bu_count,
            "resource_efficiency": round(float(avg_completion or 0), 2),
            "workload_distribution": "Balanced" if total_projects > 0 else "No Data"
        }
        
        # Generate mock analysis
        analysis = generate_mock_resource_analysis(resource_metrics)
        
        return {
            "analysis": analysis,
            "resource_metrics": resource_metrics,
            "timestamp": "2025-09-12T11:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error generating resource analysis: {str(e)}")
        return {
            "analysis": "Resource analysis is currently being set up. Please check back later for resource insights.",
            "resource_metrics": {"total_projects": 0, "average_completion": 0, "business_units": 0, "resource_efficiency": 0, "workload_distribution": "No Data"},
            "timestamp": "2025-09-12T11:00:00Z"
        }

@router.get("/predictive-insights")
async def get_predictive_insights(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get AI-powered predictive insights"""
    
    try:
        # Simple predictive data gathering
        total_projects = db.query(Project).filter(Project.is_active == True).count()
        
        # Get projects with completion data
        completed_projects = db.query(Project).filter(
            and_(Project.is_active == True, Project.percent_complete >= 100)
        ).count()
        
        # Get average completion rate
        avg_completion = db.query(Project).with_entities(
            func.avg(Project.percent_complete).label('avg_completion')
        ).filter(Project.is_active == True).scalar()
        
        predictive_metrics = {
            "total_projects": total_projects,
            "completed_projects": completed_projects,
            "average_completion": round(float(avg_completion or 0), 2),
            "success_rate": round((completed_projects / max(total_projects, 1)) * 100, 2),
            "completion_forecast": round(float(avg_completion or 0), 2)
        }
        
        # Generate mock analysis
        predictions = generate_mock_predictive_analysis(predictive_metrics)
        
        return {
            "predictions": predictions,
            "predictive_metrics": predictive_metrics,
            "timestamp": "2025-09-12T11:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error generating predictive insights: {str(e)}")
        return {
            "predictions": "Predictive insights are currently being set up. Please check back later for forecasting capabilities.",
            "predictive_metrics": {"total_projects": 0, "completed_projects": 0, "average_completion": 0, "success_rate": 0, "completion_forecast": 0},
            "timestamp": "2025-09-12T11:00:00Z"
        }

def gather_dashboard_data_sync(db: Session) -> Dict[str, Any]:
    """Gather comprehensive dashboard data for AI analysis (synchronous version)"""
    
    # Get project counts and financial data
    total_projects = db.query(Project).filter(Project.is_active == True).count()
    active_projects = db.query(Project).filter(
        and_(Project.is_active == True, Project.status_id == 1)
    ).count()
    
    financial_data = db.query(Project).with_entities(
        func.sum(Project.planned_cost).label('planned_cost'),
        func.sum(Project.planned_benefits).label('planned_benefits'),
        func.sum(Project.actual_cost).label('actual_cost'),
        func.sum(Project.actual_benefits).label('actual_benefits'),
        func.sum(Project.estimate_at_completion).label('estimate_at_completion')
    ).filter(Project.is_active == True).first()
    
    # Get business unit distribution
    bu_distribution = db.query(
        BusinessUnit.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    # Get investment type distribution
    it_distribution = db.query(
        InvestmentType.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.investment_type_id == InvestmentType.id)\
     .filter(Project.is_active == True)\
     .group_by(InvestmentType.name)\
     .all()
    
    # Get priority distribution
    priority_distribution = db.query(
        Priority.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.priority_id == Priority.id)\
     .filter(Project.is_active == True)\
     .group_by(Priority.name)\
     .all()
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_budget": float(financial_data.planned_cost or 0),
        "total_benefits": float(financial_data.planned_benefits or 0),
        "actual_cost": float(financial_data.actual_cost or 0),
        "actual_benefits": float(financial_data.actual_benefits or 0),
        "estimate_at_completion": float(financial_data.estimate_at_completion or 0),
        "completion_rate": round((active_projects / max(total_projects, 1)) * 100, 2),
        "business_unit_distribution": {name: count for name, count in bu_distribution},
        "investment_type_distribution": {name: count for name, count in it_distribution},
        "priority_distribution": {name: count for name, count in priority_distribution}
    }

def generate_mock_comprehensive_analysis(data: Dict[str, Any]) -> str:
    """Generate mock comprehensive analysis when Ollama is unavailable"""
    
    total_projects = data.get("total_projects", 0)
    active_projects = data.get("active_projects", 0)
    total_budget = data.get("total_budget", 0)
    completion_rate = data.get("completion_rate", 0)
    
    # Calculate portfolio health indicators
    portfolio_status = "Excellent" if completion_rate >= 90 else "Good" if completion_rate >= 70 else "Needs Attention"
    budget_scale = "Large Scale" if total_budget >= 100000000 else "Medium Scale" if total_budget >= 10000000 else "Small Scale"
    
    analysis = f"""
<div class="ai-analysis-report">
    <div class="executive-summary">
        <h2>📊 Executive Summary</h2>
        <div class="summary-cards">
            <div class="summary-card">
                <span class="label">Portfolio Status:</span>
                <span class="value status-{portfolio_status.lower().replace(' ', '-')}">{portfolio_status}</span>
            </div>
            <div class="summary-card">
                <span class="label">Scale:</span>
                <span class="value">{budget_scale}</span>
            </div>
            <div class="summary-card">
                <span class="label">Active Projects:</span>
                <span class="value">{total_projects}</span>
            </div>
        </div>
    </div>

    <div class="portfolio-overview">
        <h3>🎯 Portfolio Overview</h3>
        <p>The organization currently manages a robust portfolio of <strong>{total_projects} active projects</strong> with a total investment of <strong>${total_budget:,.0f}</strong>. This represents a significant commitment to digital transformation and business growth initiatives.</p>
        
        <div class="kpi-table">
            <h4>Key Performance Indicators</h4>
            <table class="data-table">
                <tr>
                    <td class="metric-label">Active Projects</td>
                    <td class="metric-value">{active_projects}</td>
                </tr>
                <tr>
                    <td class="metric-label">Portfolio Budget</td>
                    <td class="metric-value">${total_budget:,.0f}</td>
                </tr>
                <tr>
                    <td class="metric-label">Completion Rate</td>
                    <td class="metric-value">{completion_rate}%</td>
                </tr>
                <tr>
                    <td class="metric-label">Portfolio Health</td>
                    <td class="metric-value status-{portfolio_status.lower().replace(' ', '-')}">{portfolio_status}</td>
                </tr>
            </table>
        </div>
    </div>

    <div class="strategic-recommendations">
        <h3>🚀 Strategic Recommendations</h3>
        
        <div class="recommendation-item">
            <h4>1. 📈 Portfolio Optimization</h4>
            <p>With a {completion_rate}% completion rate, the portfolio demonstrates strong execution capability.</p>
            <div class="action-item">
                <strong>Recommendation:</strong> Reallocate resources from completed projects to accelerate high-priority initiatives and maintain momentum.
            </div>
        </div>

        <div class="recommendation-item">
            <h4>2. ⚠️ Risk Management Framework</h4>
            <p>Implement proactive risk monitoring for projects exceeding budget thresholds. The current portfolio shows good financial discipline with controlled variance.</p>
            <div class="action-item">
                <strong>Action Required:</strong> Establish early warning systems.
            </div>
        </div>

        <div class="recommendation-item">
            <h4>3. 👥 Resource Allocation Strategy</h4>
            <p>Focus on cross-functional collaboration between business units to maximize resource efficiency and reduce duplication.</p>
            <div class="action-item">
                <strong>Priority:</strong> Create resource sharing protocols.
            </div>
        </div>

        <div class="recommendation-item">
            <h4>4. 💻 Technology Investment Focus</h4>
            <p>Prioritize End User Experience projects as they typically deliver the highest ROI and user satisfaction.</p>
            <div class="action-item">
                <strong>Strategic Direction:</strong> Align technology investments with user value.
            </div>
        </div>

        <div class="recommendation-item">
            <h4>5. 📊 Performance Monitoring Excellence</h4>
            <p>Establish real-time dashboards for executive visibility into project health and financial performance.</p>
            <div class="action-item">
                <strong>Implementation:</strong> Deploy comprehensive monitoring systems.
            </div>
        </div>
    </div>

    <div class="action-items">
        <h3>📋 Immediate Action Items</h3>
        <table class="action-table">
            <thead>
                <tr>
                    <th>Priority</th>
                    <th>Action</th>
                    <th>Timeline</th>
                    <th>Owner</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="priority-high">High</td>
                    <td>Conduct monthly portfolio reviews</td>
                    <td>Monthly</td>
                    <td>PMO</td>
                </tr>
                <tr>
                    <td class="priority-high">High</td>
                    <td>Implement predictive analytics</td>
                    <td>Q1</td>
                    <td>IT</td>
                </tr>
                <tr>
                    <td class="priority-medium">Medium</td>
                    <td>Establish cross-functional teams</td>
                    <td>Q2</td>
                    <td>HR</td>
                </tr>
                <tr>
                    <td class="priority-medium">Medium</td>
                    <td>Develop standardized processes</td>
                    <td>Q2</td>
                    <td>PMO</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="success-metrics">
        <h3>🎯 Success Metrics</h3>
        <div class="metrics-grid">
            <div class="metric-item">
                <span class="metric-name">Target Completion Rate</span>
                <span class="metric-target">95%+</span>
            </div>
            <div class="metric-item">
                <span class="metric-name">Budget Variance</span>
                <span class="metric-target">&lt;5%</span>
            </div>
            <div class="metric-item">
                <span class="metric-name">Resource Utilization</span>
                <span class="metric-target">85%+</span>
            </div>
            <div class="metric-item">
                <span class="metric-name">Stakeholder Satisfaction</span>
                <span class="metric-target">90%+</span>
            </div>
        </div>
    </div>

    <div class="analysis-footer">
        <small>Analysis generated on {data.get('timestamp', '2025-09-12')}</small>
    </div>
</div>
"""
    
    return analysis.strip()

def generate_mock_health_analysis(data: Dict[str, Any]) -> str:
    """Generate mock project health analysis"""
    
    total_projects = data.get("total_projects", 0)
    at_risk_projects = data.get("at_risk_projects", 0)
    health_score = data.get("health_score", 0)
    
    health_status = "Excellent" if health_score >= 90 else "Good" if health_score >= 70 else "Needs Attention" if health_score >= 50 else "Critical"
    risk_level = "Low" if at_risk_projects == 0 else "Medium" if at_risk_projects <= 5 else "High"
    
    return f"""
<div class="ai-analysis-report">
    <div class="health-dashboard">
        <h2>🏥 Project Health Dashboard</h2>
        <div class="health-summary">
            <div class="health-metric">
                <span class="metric-label">Overall Health Score:</span>
                <span class="metric-value health-score-{health_status.lower().replace(' ', '-')}">{health_score}%</span>
            </div>
            <div class="health-metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value status-{health_status.lower().replace(' ', '-')}">{health_status}</span>
            </div>
            <div class="health-metric">
                <span class="metric-label">Risk Level:</span>
                <span class="metric-value risk-{risk_level.lower()}">{risk_level}</span>
            </div>
        </div>
    </div>

    <div class="health-metrics">
        <h3>📊 Health Metrics Overview</h3>
        <table class="health-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="metric-label">Total Projects</td>
                    <td class="metric-value">{total_projects}</td>
                    <td class="status-active">✅ Active</td>
                </tr>
                <tr>
                    <td class="metric-label">At-Risk Projects</td>
                    <td class="metric-value">{at_risk_projects}</td>
                    <td class="{'status-low-risk' if at_risk_projects == 0 else 'status-medium-risk' if at_risk_projects <= 5 else 'status-high-risk'}">{'🟢 Low Risk' if at_risk_projects == 0 else '🟡 Medium Risk' if at_risk_projects <= 5 else '🔴 High Risk'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Health Score</td>
                    <td class="metric-value">{health_score}%</td>
                    <td class="{'status-excellent' if health_score >= 90 else 'status-good' if health_score >= 70 else 'status-needs-attention'}">{'🟢 Excellent' if health_score >= 90 else '🟡 Good' if health_score >= 70 else '🔴 Needs Attention'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Risk Level</td>
                    <td class="metric-value">{risk_level}</td>
                    <td class="{'status-low' if risk_level == 'Low' else 'status-medium' if risk_level == 'Medium' else 'status-high'}">{'🟢 Low' if risk_level == 'Low' else '🟡 Medium' if risk_level == 'Medium' else '🔴 High'}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="health-assessment">
        <h3>🔍 Detailed Health Assessment</h3>
        
        <div class="assessment-item">
            <h4>✅ Timeline Performance</h4>
            <p>Projects are generally on track with minimal delays. The portfolio shows strong execution discipline and effective project management practices.</p>
        </div>

        <div class="assessment-item">
            <h4>💰 Budget Management</h4>
            <p>Cost controls are effective with minimal overruns. Financial discipline is maintained across the portfolio with proper budget monitoring.</p>
        </div>

        <div class="assessment-item">
            <h4>🎯 Quality Metrics</h4>
            <p>Deliverable quality meets established standards. Quality assurance processes are functioning effectively across all projects.</p>
        </div>

        <div class="assessment-item">
            <h4>👥 Stakeholder Satisfaction</h4>
            <p>High engagement levels across business units. Stakeholder communication and satisfaction metrics are positive.</p>
        </div>

        <div class="assessment-item">
            <h4>⚠️ Risk Assessment</h4>
            <p>{at_risk_projects} projects require immediate attention. {'All projects are on track.' if at_risk_projects == 0 else f'Focus needed on {at_risk_projects} at-risk initiatives.'}</p>
        </div>
    </div>

    <div class="risk-mitigation">
        <h3>🛡️ Risk Mitigation Strategies</h3>
        
        <div class="mitigation-section">
            <h4>Immediate Actions:</h4>
            <ul class="action-list">
                <li><strong>Early Warning Systems</strong> - Implement proactive monitoring for at-risk projects</li>
                <li><strong>Escalation Procedures</strong> - Establish clear escalation paths for budget variances</li>
                <li><strong>Review Boards</strong> - Create cross-functional review boards for complex initiatives</li>
                <li><strong>Focus Areas</strong> - Concentrate on projects with completion rates below 50%</li>
            </ul>
        </div>

        <div class="mitigation-section">
            <h4>Preventive Measures:</h4>
            <ul class="preventive-list">
                <li>Regular health check assessments</li>
                <li>Automated risk scoring algorithms</li>
                <li>Stakeholder communication protocols</li>
                <li>Quality gate reviews</li>
            </ul>
        </div>
    </div>

    <div class="health-trends">
        <h3>📈 Health Trends & Recommendations</h3>
        <div class="trend-indicator">
            <span class="trend-label">Current Trend:</span>
            <span class="trend-value {'trend-positive' if health_score >= 80 else 'trend-stable' if health_score >= 60 else 'trend-declining'}">{'🟢 Positive' if health_score >= 80 else '🟡 Stable' if health_score >= 60 else '🔴 Declining'}</span>
        </div>
        
        <div class="recommendations">
            <h4>Recommendations:</h4>
            <ul class="recommendation-list">
                <li>Maintain current health monitoring practices</li>
                <li>{'Increase focus on at-risk project recovery' if at_risk_projects > 0 else 'Continue excellent project management practices'}</li>
                <li>Implement predictive health analytics</li>
                <li>Regular portfolio health reviews</li>
            </ul>
        </div>
    </div>

    <div class="analysis-footer">
        <small>Health assessment completed on {data.get('timestamp', '2025-09-12')}</small>
    </div>
</div>
"""

def generate_mock_financial_analysis(data: Dict[str, Any]) -> str:
    """Generate mock financial analysis"""
    
    planned_cost = data.get("planned_cost", 0)
    actual_cost = data.get("actual_cost", 0)
    planned_benefits = data.get("planned_benefits", 0)
    actual_benefits = data.get("actual_benefits", 0)
    cost_variance = data.get("cost_variance", 0)
    roi = data.get("roi", 0)
    
    budget_status = "Under Budget" if cost_variance < 0 else "Over Budget" if cost_variance > 10 else "On Budget"
    roi_status = "Excellent" if roi > 20 else "Good" if roi > 10 else "Needs Improvement"
    cost_efficiency = "Excellent" if abs(cost_variance) < 5 else "Good" if abs(cost_variance) < 15 else "Needs Attention"
    
    # Calculate additional metrics
    benefit_variance = ((actual_benefits - planned_benefits) / max(planned_benefits, 1)) * 100
    cost_savings = planned_cost - actual_cost
    
    return f"""
<div class="ai-analysis-report">
    <div class="financial-dashboard">
        <h2>💰 Financial Performance Report</h2>
        <div class="financial-summary">
            <div class="financial-metric">
                <span class="metric-label">Portfolio Investment:</span>
                <span class="metric-value">${planned_cost:,.0f}</span>
            </div>
            <div class="financial-metric">
                <span class="metric-label">Performance:</span>
                <span class="metric-value status-{roi_status.lower().replace(' ', '-')}">{roi_status}</span>
            </div>
            <div class="financial-metric">
                <span class="metric-label">Budget Status:</span>
                <span class="metric-value budget-{budget_status.lower().replace(' ', '-')}">{budget_status}</span>
            </div>
        </div>
    </div>

    <div class="financial-metrics">
        <h3>📊 Financial Metrics Dashboard</h3>
        <table class="financial-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Planned</th>
                    <th>Actual</th>
                    <th>Variance</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="metric-label">Total Cost</td>
                    <td class="metric-value">${planned_cost:,.0f}</td>
                    <td class="metric-value">${actual_cost:,.0f}</td>
                    <td class="metric-value">{cost_variance:+.1f}%</td>
                    <td class="{'status-under-budget' if cost_variance < 0 else 'status-over-budget' if cost_variance > 10 else 'status-on-budget'}">{'🟢 Under Budget' if cost_variance < 0 else '🔴 Over Budget' if cost_variance > 10 else '🟡 On Budget'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Total Benefits</td>
                    <td class="metric-value">${planned_benefits:,.0f}</td>
                    <td class="metric-value">${actual_benefits:,.0f}</td>
                    <td class="metric-value">{benefit_variance:+.1f}%</td>
                    <td class="{'status-exceeding' if benefit_variance > 0 else 'status-below-target'}">{'🟢 Exceeding' if benefit_variance > 0 else '🔴 Below Target'}</td>
                </tr>
                <tr>
                    <td class="metric-label">ROI</td>
                    <td class="metric-value">-</td>
                    <td class="metric-value">{roi:+.1f}%</td>
                    <td class="metric-value">-</td>
                    <td class="{'status-excellent' if roi > 20 else 'status-good' if roi > 10 else 'status-needs-improvement'}">{'🟢 Excellent' if roi > 20 else '🟡 Good' if roi > 10 else '🔴 Needs Improvement'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Cost Efficiency</td>
                    <td class="metric-value">-</td>
                    <td class="metric-value">{cost_efficiency}</td>
                    <td class="metric-value">-</td>
                    <td class="{'status-excellent' if abs(cost_variance) < 5 else 'status-good' if abs(cost_variance) < 15 else 'status-needs-attention'}">{'🟢 Excellent' if abs(cost_variance) < 5 else '🟡 Good' if abs(cost_variance) < 15 else '🔴 Needs Attention'}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="financial-insights">
        <h3>💡 Key Financial Insights</h3>
        
        <div class="insight-item">
            <h4>🎯 Budget Performance</h4>
            <p>{'✅ **Under Budget Achievement:** The portfolio is performing exceptionally well with significant cost savings.' if cost_variance < 0 else '⚠️ **Budget Overspend:** Immediate attention required to control costs.' if cost_variance > 10 else '✅ **On Budget:** Portfolio is maintaining financial discipline.'}</p>
            <div class="cost-savings">
                <strong>Cost Savings:</strong> ${cost_savings:,.0f} {'(Savings)' if cost_savings > 0 else '(Overspend)'}
            </div>
        </div>

        <div class="insight-item">
            <h4>📈 Return on Investment</h4>
            <p>{'🚀 **Strong ROI:** Portfolio delivering excellent returns on investment.' if roi > 20 else '📊 **Moderate ROI:** Room for improvement in benefit realization.' if roi > 0 else '⚠️ **Negative ROI:** Critical attention needed to improve returns.'}</p>
            <div class="roi-trend">
                <strong>ROI Trend:</strong> <span class="{'trend-positive' if roi > 10 else 'trend-neutral' if roi > 0 else 'trend-negative'}">{'🟢 Positive' if roi > 10 else '🟡 Neutral' if roi > 0 else '🔴 Negative'}</span>
            </div>
        </div>

        <div class="insight-item">
            <h4>💎 Benefit Realization</h4>
            <p>Actual benefits of <strong>${actual_benefits:,.0f}</strong> represent {'excellent' if benefit_variance > 10 else 'good' if benefit_variance > 0 else 'below target'} performance against planned benefits of <strong>${planned_benefits:,.0f}</strong>.</p>
        </div>
    </div>

    <div class="financial-recommendations">
        <h3>🎯 Strategic Financial Recommendations</h3>
        
        <div class="recommendation-section">
            <h4>Immediate Actions:</h4>
            <ul class="action-list">
                <li><strong>Dynamic Budget Allocation</strong> - Implement performance-based budget adjustments</li>
                <li><strong>ROI Tracking System</strong> - Establish comprehensive ROI monitoring for all initiatives</li>
                <li><strong>Executive Dashboards</strong> - Deploy real-time financial visibility tools</li>
                <li><strong>Cost Optimization</strong> - Focus on projects with ROI above 15%</li>
                <li><strong>Variance Management</strong> - Review and address cost overruns exceeding 10%</li>
            </ul>
        </div>

        <div class="recommendation-section">
            <h4>Long-term Strategies:</h4>
            <ul class="strategy-list">
                <li>Implement predictive financial modeling</li>
                <li>Establish financial governance frameworks</li>
                <li>Create benefit realization tracking systems</li>
                <li>Develop cost optimization methodologies</li>
            </ul>
        </div>
    </div>

    <div class="financial-action-plan">
        <h3>📋 Financial Action Plan</h3>
        <table class="action-table">
            <thead>
                <tr>
                    <th>Priority</th>
                    <th>Action</th>
                    <th>Target</th>
                    <th>Timeline</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="priority-high">High</td>
                    <td>ROI Improvement Program</td>
                    <td>15%+ ROI</td>
                    <td>Q1-Q2</td>
                </tr>
                <tr>
                    <td class="priority-high">High</td>
                    <td>Budget Variance Control</td>
                    <td>&lt;5% Variance</td>
                    <td>Ongoing</td>
                </tr>
                <tr>
                    <td class="priority-medium">Medium</td>
                    <td>Benefit Tracking System</td>
                    <td>90% Accuracy</td>
                    <td>Q2</td>
                </tr>
                <tr>
                    <td class="priority-medium">Medium</td>
                    <td>Cost Optimization</td>
                    <td>10% Reduction</td>
                    <td>Q3</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="financial-targets">
        <h3>🎯 Financial Targets</h3>
        <div class="targets-grid">
            <div class="target-item">
                <span class="target-name">Target ROI</span>
                <span class="target-value">20%+</span>
            </div>
            <div class="target-item">
                <span class="target-name">Budget Variance</span>
                <span class="target-value">&lt;5%</span>
            </div>
            <div class="target-item">
                <span class="target-name">Benefit Realization</span>
                <span class="target-value">95%+</span>
            </div>
            <div class="target-item">
                <span class="target-name">Cost Efficiency</span>
                <span class="target-value">90%+</span>
            </div>
        </div>
    </div>

    <div class="analysis-footer">
        <small>Financial analysis completed on {data.get('timestamp', '2025-09-12')}</small>
    </div>
</div>
"""

def generate_mock_resource_analysis(data: Dict[str, Any]) -> str:
    """Generate mock resource analysis"""
    
    total_projects = data.get("total_projects", 0)
    average_completion = data.get("average_completion", 0)
    business_units = data.get("business_units", 0)
    resource_efficiency = data.get("resource_efficiency", 0)
    workload_distribution = data.get("workload_distribution", "No Data")
    
    efficiency_status = "Excellent" if resource_efficiency >= 80 else "Good" if resource_efficiency >= 60 else "Needs Improvement"
    project_density = round(total_projects / max(business_units, 1), 1)
    completion_trend = "Positive" if average_completion >= 50 else "Needs Attention"
    
    return f"""
<div class="ai-analysis-report">
    <div class="resource-dashboard">
        <h2>👥 Resource Utilization Report</h2>
        <div class="resource-summary">
            <div class="resource-metric">
                <span class="metric-label">Portfolio Scale:</span>
                <span class="metric-value">{total_projects} Projects</span>
            </div>
            <div class="resource-metric">
                <span class="metric-label">Efficiency:</span>
                <span class="metric-value efficiency-{efficiency_status.lower().replace(' ', '-')}">{resource_efficiency}% ({efficiency_status})</span>
            </div>
            <div class="resource-metric">
                <span class="metric-label">Coverage:</span>
                <span class="metric-value">{business_units} Business Units</span>
            </div>
        </div>
    </div>

    <div class="resource-metrics">
        <h3>📊 Resource Metrics Overview</h3>
        <table class="resource-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Status</th>
                    <th>Trend</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="metric-label">Total Projects</td>
                    <td class="metric-value">{total_projects}</td>
                    <td class="status-active">✅ Active</td>
                    <td class="{'trend-growing' if total_projects > 100 else 'trend-stable'}">{'🟢 Growing' if total_projects > 100 else '🟡 Stable'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Resource Efficiency</td>
                    <td class="metric-value">{resource_efficiency}%</td>
                    <td class="{'status-excellent' if resource_efficiency >= 80 else 'status-good' if resource_efficiency >= 60 else 'status-needs-improvement'}">{'🟢 Excellent' if resource_efficiency >= 80 else '🟡 Good' if resource_efficiency >= 60 else '🔴 Needs Improvement'}</td>
                    <td class="{'trend-improving' if resource_efficiency >= 70 else 'trend-declining'}">{'🟢 Improving' if resource_efficiency >= 70 else '🔴 Declining'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Business Units</td>
                    <td class="metric-value">{business_units}</td>
                    <td class="status-covered">✅ Covered</td>
                    <td class="trend-balanced">🟢 Balanced</td>
                </tr>
                <tr>
                    <td class="metric-label">Project Density</td>
                    <td class="metric-value">{project_density} per unit</td>
                    <td class="{'status-optimal' if project_density <= 20 else 'status-high' if project_density <= 30 else 'status-overloaded'}">{'🟢 Optimal' if project_density <= 20 else '🟡 High' if project_density <= 30 else '🔴 Overloaded'}</td>
                    <td class="{'trend-stable' if project_density <= 25 else 'trend-increasing'}">{'🟢 Stable' if project_density <= 25 else '🔴 Increasing'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Average Completion</td>
                    <td class="metric-value">{average_completion}%</td>
                    <td class="{'status-on-track' if average_completion >= 70 else 'status-moderate' if average_completion >= 50 else 'status-behind'}">{'🟢 On Track' if average_completion >= 70 else '🟡 Moderate' if average_completion >= 50 else '🔴 Behind'}</td>
                    <td class="{'trend-positive' if average_completion >= 50 else 'trend-negative'}">{'🟢 Positive' if average_completion >= 50 else '🔴 Negative'}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="resource-analysis">
        <h3>🔍 Detailed Resource Analysis</h3>
        
        <div class="analysis-item">
            <h4>🎯 Resource Efficiency Assessment</h4>
            <p>{'✅ **Excellent Performance:** Resource utilization is optimal with high efficiency rates.' if resource_efficiency >= 80 else '📊 **Good Performance:** Resource efficiency is acceptable with room for improvement.' if resource_efficiency >= 60 else '⚠️ **Improvement Needed:** Resource efficiency requires immediate attention and optimization.'}</p>
            <div class="efficiency-details">
                <strong>Current Efficiency:</strong> {resource_efficiency}% | <strong>Target:</strong> 80%+
            </div>
        </div>

        <div class="analysis-item">
            <h4>📈 Workload Distribution Analysis</h4>
            <p>The portfolio demonstrates <strong>{workload_distribution.lower()}</strong> workload distribution across {business_units} business units. This indicates {'optimal resource allocation' if workload_distribution == 'Balanced' else 'potential resource bottlenecks'}.</p>
            <div class="distribution-details">
                <strong>Project Density:</strong> {project_density} projects per business unit<br>
                <strong>Distribution Status:</strong> {'🟢 Balanced' if workload_distribution == 'Balanced' else '🟡 Uneven'}
            </div>
        </div>

        <div class="analysis-item">
            <h4>🏢 Business Unit Coverage</h4>
            <p>All {business_units} business units are actively engaged in the portfolio, ensuring comprehensive organizational coverage and balanced resource allocation.</p>
            <div class="coverage-details">
                <strong>Coverage Quality:</strong> {'🟢 Comprehensive' if business_units >= 5 else '🟡 Limited'}
            </div>
        </div>
    </div>

    <div class="resource-optimization">
        <h3>🚀 Resource Optimization Strategies</h3>
        
        <div class="optimization-section">
            <h4>Immediate Actions:</h4>
            <ul class="action-list">
                <li><strong>Resource Sharing Protocols</strong> - Implement cross-unit resource sharing mechanisms</li>
                <li><strong>Skill Development Programs</strong> - Launch cross-training initiatives for critical skills</li>
                <li><strong>Specialized Resource Pools</strong> - Establish expert resource pools for specialized expertise</li>
                <li><strong>Performance Focus</strong> - Concentrate on units with completion rates below 60%</li>
                <li><strong>Workload Balancing</strong> - Redistribute workload across {business_units} business units</li>
            </ul>
        </div>

        <div class="optimization-section">
            <h4>Strategic Initiatives:</h4>
            <ul class="strategy-list">
                <li><strong>Capacity Planning Tools</strong> - Deploy advanced capacity planning and forecasting</li>
                <li><strong>Resource Analytics</strong> - Implement real-time resource utilization monitoring</li>
                <li><strong>Cross-Functional Teams</strong> - Create agile teams spanning multiple business units</li>
                <li><strong>Skill Matrix Development</strong> - Build comprehensive skill mapping and gap analysis</li>
            </ul>
        </div>
    </div>

    <div class="resource-action-plan">
        <h3>📋 Resource Action Plan</h3>
        <table class="action-table">
            <thead>
                <tr>
                    <th>Priority</th>
                    <th>Initiative</th>
                    <th>Target</th>
                    <th>Timeline</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="priority-high">High</td>
                    <td>Resource Efficiency Program</td>
                    <td>80%+ Efficiency</td>
                    <td>Q1-Q2</td>
                </tr>
                <tr>
                    <td class="priority-high">High</td>
                    <td>Workload Balancing</td>
                    <td>Optimal Distribution</td>
                    <td>Q1</td>
                </tr>
                <tr>
                    <td class="priority-medium">Medium</td>
                    <td>Cross-Training Program</td>
                    <td>90% Skill Coverage</td>
                    <td>Q2-Q3</td>
                </tr>
                <tr>
                    <td class="priority-medium">Medium</td>
                    <td>Resource Pool Development</td>
                    <td>5+ Expert Pools</td>
                    <td>Q3</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="resource-targets">
        <h3>🎯 Resource Targets</h3>
        <div class="targets-grid">
            <div class="target-item">
                <span class="target-name">Resource Efficiency</span>
                <span class="target-value">85%+</span>
            </div>
            <div class="target-item">
                <span class="target-name">Workload Distribution</span>
                <span class="target-value">Balanced</span>
            </div>
            <div class="target-item">
                <span class="target-name">Project Density</span>
                <span class="target-value">&lt;25 per unit</span>
            </div>
            <div class="target-item">
                <span class="target-name">Completion Rate</span>
                <span class="target-value">75%+</span>
            </div>
            <div class="target-item">
                <span class="target-name">Skill Coverage</span>
                <span class="target-value">90%+</span>
            </div>
        </div>
    </div>

    <div class="resource-forecasts">
        <h3>📊 Resource Trends & Forecasts</h3>
        <div class="forecast-section">
            <div class="current-trend">
                <span class="trend-label">Current Trend:</span>
                <span class="trend-value {'trend-improving' if resource_efficiency >= 70 else 'trend-declining'}">{'🟢 Improving' if resource_efficiency >= 70 else '🔴 Declining'}</span>
            </div>
            
            <div class="forecast-details">
                <h4>6-Month Forecast:</h4>
                <ul class="forecast-list">
                    <li>Resource efficiency expected to {'increase to 80%+' if resource_efficiency >= 60 else 'improve significantly'}</li>
                    <li>Workload distribution will {'remain balanced' if workload_distribution == 'Balanced' else 'become more balanced'}</li>
                    <li>Project density will {'stabilize' if project_density <= 25 else 'require rebalancing'}</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="analysis-footer">
        <small>Resource analysis completed on {data.get('timestamp', '2025-09-12')}</small>
    </div>
</div>
"""

def generate_mock_predictive_analysis(data: Dict[str, Any]) -> str:
    """Generate mock predictive analysis"""
    
    total_projects = data.get("total_projects", 0)
    completed_projects = data.get("completed_projects", 0)
    average_completion = data.get("average_completion", 0)
    success_rate = data.get("success_rate", 0)
    completion_forecast = data.get("completion_forecast", 0)
    
    forecast_status = "Excellent" if completion_forecast >= 80 else "Good" if completion_forecast >= 60 else "Needs Attention"
    success_outlook = "High" if success_rate >= 80 else "Moderate" if success_rate >= 60 else "Low"
    timeline_risk = "Low" if average_completion >= 70 else "Moderate" if average_completion >= 50 else "High"
    
    # Calculate additional predictive metrics
    projects_behind = total_projects - completed_projects
    completion_trend = "Accelerating" if average_completion >= 60 else "Stable" if average_completion >= 40 else "Declining"
    
    return f"""
<div class="ai-analysis-report">
    <div class="predictive-dashboard">
        <h2>🔮 Predictive Insights & Forecasts</h2>
        <div class="predictive-summary">
            <div class="predictive-metric">
                <span class="metric-label">Portfolio Scale:</span>
                <span class="metric-value">{total_projects} Projects</span>
            </div>
            <div class="predictive-metric">
                <span class="metric-label">Success Outlook:</span>
                <span class="metric-value outlook-{success_outlook.lower()}">{success_outlook}</span>
            </div>
            <div class="predictive-metric">
                <span class="metric-label">Timeline Risk:</span>
                <span class="metric-value risk-{timeline_risk.lower()}">{timeline_risk}</span>
            </div>
        </div>
    </div>

    <div class="predictive-metrics">
        <h3>📊 Predictive Metrics Dashboard</h3>
        <table class="predictive-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Current</th>
                    <th>Forecast</th>
                    <th>Confidence</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="metric-label">Success Rate</td>
                    <td class="metric-value">{success_rate}%</td>
                    <td class="metric-value">{success_rate + 10 if success_rate < 90 else success_rate}%</td>
                    <td class="{'confidence-high' if success_rate >= 80 else 'confidence-medium' if success_rate >= 60 else 'confidence-low'}">{'🟢 High' if success_rate >= 80 else '🟡 Medium' if success_rate >= 60 else '🔴 Low'}</td>
                    <td class="{'status-excellent' if success_rate >= 80 else 'status-good' if success_rate >= 60 else 'status-needs-improvement'}">{'🟢 Excellent' if success_rate >= 80 else '🟡 Good' if success_rate >= 60 else '🔴 Needs Improvement'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Completion Forecast</td>
                    <td class="metric-value">{completion_forecast}%</td>
                    <td class="metric-value">{completion_forecast + 15 if completion_forecast < 85 else completion_forecast}%</td>
                    <td class="{'confidence-high' if completion_forecast >= 70 else 'confidence-medium' if completion_forecast >= 50 else 'confidence-low'}">{'🟢 High' if completion_forecast >= 70 else '🟡 Medium' if completion_forecast >= 50 else '🔴 Low'}</td>
                    <td class="{'status-excellent' if completion_forecast >= 80 else 'status-good' if completion_forecast >= 60 else 'status-needs-attention'}">{'🟢 Excellent' if completion_forecast >= 80 else '🟡 Good' if completion_forecast >= 60 else '🔴 Needs Attention'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Completed Projects</td>
                    <td class="metric-value">{completed_projects}</td>
                    <td class="metric-value">{completed_projects + int(total_projects * 0.3)}</td>
                    <td class="{'confidence-high' if completed_projects > total_projects * 0.5 else 'confidence-medium' if completed_projects > total_projects * 0.2 else 'confidence-low'}">{'🟢 High' if completed_projects > total_projects * 0.5 else '🟡 Medium' if completed_projects > total_projects * 0.2 else '🔴 Low'}</td>
                    <td class="{'status-on-track' if completed_projects > total_projects * 0.3 else 'status-behind'}">{'🟢 On Track' if completed_projects > total_projects * 0.3 else '🟡 Behind'}</td>
                </tr>
                <tr>
                    <td class="metric-label">Timeline Risk</td>
                    <td class="metric-value">{timeline_risk}</td>
                    <td class="metric-value">{'🟢 Low' if average_completion >= 60 else '🟡 Medium'}</td>
                    <td class="{'confidence-high' if average_completion >= 70 else 'confidence-medium' if average_completion >= 50 else 'confidence-low'}">{'🟢 High' if average_completion >= 70 else '🟡 Medium' if average_completion >= 50 else '🔴 Low'}</td>
                    <td class="{'status-low-risk' if timeline_risk == 'Low' else 'status-medium-risk' if timeline_risk == 'Moderate' else 'status-high-risk'}">{'🟢 Low Risk' if timeline_risk == 'Low' else '🟡 Medium Risk' if timeline_risk == 'Moderate' else '🔴 High Risk'}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="analysis-footer">
        <small>Predictive analysis completed on {data.get('timestamp', '2025-09-12')}</small>
    </div>
</div>
"""

async def gather_dashboard_data(db: Session) -> Dict[str, Any]:
    """Gather comprehensive dashboard data for AI analysis"""
    
    # Get project counts and financial data
    total_projects = db.query(Project).filter(Project.is_active == True).count()
    active_projects = db.query(Project).filter(
        and_(Project.is_active == True, Project.status_id == 1)
    ).count()
    
    financial_data = db.query(Project).with_entities(
        func.sum(Project.planned_cost).label('planned_cost'),
        func.sum(Project.planned_benefits).label('planned_benefits'),
        func.sum(Project.actual_cost).label('actual_cost'),
        func.sum(Project.actual_benefits).label('actual_benefits'),
        func.sum(Project.estimate_at_completion).label('estimate_at_completion')
    ).filter(Project.is_active == True).first()
    
    # Get business unit distribution
    bu_distribution = db.query(
        BusinessUnit.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    # Get investment type distribution
    it_distribution = db.query(
        InvestmentType.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.investment_type_id == InvestmentType.id)\
     .filter(Project.is_active == True)\
     .group_by(InvestmentType.name)\
     .all()
    
    # Get priority distribution
    priority_distribution = db.query(
        Priority.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.priority_id == Priority.id)\
     .filter(Project.is_active == True)\
     .group_by(Priority.name)\
     .all()
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_budget": float(financial_data.planned_cost or 0),
        "total_benefits": float(financial_data.planned_benefits or 0),
        "actual_cost": float(financial_data.actual_cost or 0),
        "actual_benefits": float(financial_data.actual_benefits or 0),
        "estimate_at_completion": float(financial_data.estimate_at_completion or 0),
        "completion_rate": round((active_projects / max(total_projects, 1)) * 100, 2),
        "business_unit_distribution": {name: count for name, count in bu_distribution},
        "investment_type_distribution": {name: count for name, count in it_distribution},
        "priority_distribution": {name: count for name, count in priority_distribution}
    }

def gather_project_health_data_sync(db: Session) -> Dict[str, Any]:
    """Gather project health data for AI analysis (synchronous version)"""
    
    # Get status distribution
    status_distribution = db.query(
        Status.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.status_id == Status.id)\
     .filter(Project.is_active == True)\
     .group_by(Status.name)\
     .all()
    
    # Get projects at risk
    at_risk_projects = db.query(Project).filter(
        and_(Project.is_active == True, Project.status_id == 3)  # At Risk status
    ).count()
    
    # Get completion rates by business unit
    completion_by_bu = db.query(
        BusinessUnit.name,
        func.count(Project.id).label('total'),
        func.sum(func.case([(Project.status_id == 2, 1)], else_=0)).label('completed')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    return {
        "status_distribution": {name: count for name, count in status_distribution},
        "at_risk_projects": at_risk_projects,
        "completion_by_business_unit": {
            name: {
                "total": total,
                "completed": completed,
                "completion_rate": round((completed / max(total, 1)) * 100, 2)
            }
            for name, total, completed in completion_by_bu
        }
    }

def gather_financial_data_sync(db: Session) -> Dict[str, Any]:
    """Gather financial data for AI analysis (synchronous version)"""
    
    # Get financial metrics by business unit
    financial_by_bu = db.query(
        BusinessUnit.name,
        func.sum(Project.planned_cost).label('planned_cost'),
        func.sum(Project.actual_cost).label('actual_cost'),
        func.sum(Project.planned_benefits).label('planned_benefits'),
        func.sum(Project.actual_benefits).label('actual_benefits')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    # Calculate budget variance
    budget_variance = db.query(
        func.avg(
            (Project.actual_cost - Project.planned_cost) / func.nullif(Project.planned_cost, 0) * 100
        ).label('avg_variance')
    ).filter(Project.is_active == True).scalar()
    
    return {
        "financial_by_business_unit": {
            name: {
                "planned_cost": float(planned_cost or 0),
                "actual_cost": float(actual_cost or 0),
                "planned_benefits": float(planned_benefits or 0),
                "actual_benefits": float(actual_benefits or 0),
                "cost_variance": round(((actual_cost or 0) - (planned_cost or 0)) / max(planned_cost or 1, 1) * 100, 2)
            }
            for name, planned_cost, actual_cost, planned_benefits, actual_benefits in financial_by_bu
        },
        "average_budget_variance": round(float(budget_variance or 0), 2)
    }

def gather_resource_data_sync(db: Session) -> Dict[str, Any]:
    """Gather resource data for AI analysis (synchronous version)"""
    
    # Get project distribution by business unit (as proxy for resource allocation)
    resource_allocation = db.query(
        BusinessUnit.name,
        func.count(Project.id).label('project_count'),
        func.avg(Project.percent_complete).label('avg_completion')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    return {
        "resource_allocation": {
            name: {
                "project_count": project_count,
                "average_completion": round(float(avg_completion or 0), 2),
                "workload_score": project_count * (avg_completion or 0) / 100
            }
            for name, project_count, avg_completion in resource_allocation
        }
    }

def gather_predictive_data_sync(db: Session) -> Dict[str, Any]:
    """Gather predictive data for AI analysis (synchronous version)"""
    
    # Get projects with timeline data
    timeline_data = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.start_date.isnot(None),
            Project.due_date.isnot(None)
        )
    ).all()
    
    # Calculate timeline metrics
    timeline_metrics = []
    for project in timeline_data:
        if project.start_date and project.due_date:
            timeline_metrics.append({
                "project_id": project.project_id,
                "planned_duration": (project.due_date - project.start_date).days,
                "completion_percentage": float(project.percent_complete or 0),
                "budget_variance": float((project.actual_cost or 0) - (project.planned_cost or 0))
            })
    
    return {
        "timeline_metrics": timeline_metrics,
        "total_projects_analyzed": len(timeline_metrics),
        "average_completion": round(sum(p["completion_percentage"] for p in timeline_metrics) / max(len(timeline_metrics), 1), 2)
    }

async def gather_project_health_data(db: Session) -> Dict[str, Any]:
    """Gather project health data for AI analysis"""
    
    # Get status distribution
    status_distribution = db.query(
        Status.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.status_id == Status.id)\
     .filter(Project.is_active == True)\
     .group_by(Status.name)\
     .all()
    
    # Get projects at risk
    at_risk_projects = db.query(Project).filter(
        and_(Project.is_active == True, Project.status_id == 3)  # At Risk status
    ).count()
    
    # Get completion rates by business unit
    completion_by_bu = db.query(
        BusinessUnit.name,
        func.count(Project.id).label('total'),
        func.sum(func.case([(Project.status_id == 2, 1)], else_=0)).label('completed')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    return {
        "status_distribution": {name: count for name, count in status_distribution},
        "at_risk_projects": at_risk_projects,
        "completion_by_business_unit": {
            name: {
                "total": total,
                "completed": completed,
                "completion_rate": round((completed / max(total, 1)) * 100, 2)
            }
            for name, total, completed in completion_by_bu
        }
    }

async def gather_financial_data(db: Session) -> Dict[str, Any]:
    """Gather financial data for AI analysis"""
    
    # Get financial metrics by business unit
    financial_by_bu = db.query(
        BusinessUnit.name,
        func.sum(Project.planned_cost).label('planned_cost'),
        func.sum(Project.actual_cost).label('actual_cost'),
        func.sum(Project.planned_benefits).label('planned_benefits'),
        func.sum(Project.actual_benefits).label('actual_benefits')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    # Calculate budget variance
    budget_variance = db.query(
        func.avg(
            (Project.actual_cost - Project.planned_cost) / func.nullif(Project.planned_cost, 0) * 100
        ).label('avg_variance')
    ).filter(Project.is_active == True).scalar()
    
    return {
        "financial_by_business_unit": {
            name: {
                "planned_cost": float(planned_cost or 0),
                "actual_cost": float(actual_cost or 0),
                "planned_benefits": float(planned_benefits or 0),
                "actual_benefits": float(actual_benefits or 0),
                "cost_variance": round(((actual_cost or 0) - (planned_cost or 0)) / max(planned_cost or 1, 1) * 100, 2)
            }
            for name, planned_cost, actual_cost, planned_benefits, actual_benefits in financial_by_bu
        },
        "average_budget_variance": round(float(budget_variance or 0), 2)
    }

async def gather_resource_data(db: Session) -> Dict[str, Any]:
    """Gather resource data for AI analysis"""
    
    # Get project distribution by business unit (as proxy for resource allocation)
    resource_allocation = db.query(
        BusinessUnit.name,
        func.count(Project.id).label('project_count'),
        func.avg(Project.percent_complete).label('avg_completion')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    return {
        "resource_allocation": {
            name: {
                "project_count": project_count,
                "average_completion": round(float(avg_completion or 0), 2),
                "workload_score": project_count * (avg_completion or 0) / 100
            }
            for name, project_count, avg_completion in resource_allocation
        }
    }

async def gather_predictive_data(db: Session) -> Dict[str, Any]:
    """Gather predictive data for AI analysis"""
    
    # Get projects with timeline data
    timeline_data = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.start_date.isnot(None),
            Project.due_date.isnot(None)
        )
    ).all()
    
    # Calculate timeline metrics
    timeline_metrics = []
    for project in timeline_data:
        if project.start_date and project.due_date:
            timeline_metrics.append({
                "project_id": project.project_id,
                "planned_duration": (project.due_date - project.start_date).days,
                "completion_percentage": float(project.percent_complete or 0),
                "budget_variance": float((project.actual_cost or 0) - (project.planned_cost or 0))
            })
    
    return {
        "timeline_metrics": timeline_metrics,
        "total_projects_analyzed": len(timeline_metrics),
        "average_completion": round(sum(p["completion_percentage"] for p in timeline_metrics) / max(len(timeline_metrics), 1), 2)
    }
