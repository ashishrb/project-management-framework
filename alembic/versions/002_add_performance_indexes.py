"""Add performance indexes

Revision ID: 002_performance_indexes
Revises: 001_add_performance_indexes
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_performance_indexes'
down_revision = '001_add_performance_indexes'
branch_labels = None
depends_on = None

def upgrade():
    """Add performance indexes for better query optimization"""
    
    # Projects table indexes
    op.create_index('idx_projects_status', 'projects', ['status'])
    op.create_index('idx_projects_priority', 'projects', ['priority'])
    op.create_index('idx_projects_created_at', 'projects', ['created_at'])
    op.create_index('idx_projects_updated_at', 'projects', ['updated_at'])
    op.create_index('idx_projects_user_id', 'projects', ['user_id'])
    op.create_index('idx_projects_status_priority', 'projects', ['status', 'priority'])
    op.create_index('idx_projects_user_status', 'projects', ['user_id', 'status'])
    
    # Features table indexes
    op.create_index('idx_features_project_id', 'features', ['project_id'])
    op.create_index('idx_features_status', 'features', ['status'])
    op.create_index('idx_features_priority', 'features', ['priority'])
    op.create_index('idx_features_created_at', 'features', ['created_at'])
    op.create_index('idx_features_project_status', 'features', ['project_id', 'status'])
    op.create_index('idx_features_project_priority', 'features', ['project_id', 'priority'])
    
    # Resources table indexes
    op.create_index('idx_resources_project_id', 'resources', ['project_id'])
    op.create_index('idx_resources_resource_type', 'resources', ['resource_type'])
    op.create_index('idx_resources_status', 'resources', ['status'])
    op.create_index('idx_resources_created_at', 'resources', ['created_at'])
    op.create_index('idx_resources_project_type', 'resources', ['project_id', 'resource_type'])
    
    # Risks table indexes
    op.create_index('idx_risks_project_id', 'risks', ['project_id'])
    op.create_index('idx_risks_risk_level', 'risks', ['risk_level'])
    op.create_index('idx_risks_status', 'risks', ['status'])
    op.create_index('idx_risks_created_at', 'risks', ['created_at'])
    op.create_index('idx_risks_project_level', 'risks', ['project_id', 'risk_level'])
    
    # Backlogs table indexes
    op.create_index('idx_backlogs_project_id', 'backlogs', ['project_id'])
    op.create_index('idx_backlogs_status', 'backlogs', ['status'])
    op.create_index('idx_backlogs_priority', 'backlogs', ['priority'])
    op.create_index('idx_backlogs_created_at', 'backlogs', ['created_at'])
    op.create_index('idx_backlogs_project_status', 'backlogs', ['project_id', 'status'])
    
    # Reports table indexes
    op.create_index('idx_reports_project_id', 'reports', ['project_id'])
    op.create_index('idx_reports_report_type', 'reports', ['report_type'])
    op.create_index('idx_reports_created_at', 'reports', ['created_at'])
    op.create_index('idx_reports_project_type', 'reports', ['project_id', 'report_type'])
    
    # Analytics table indexes
    op.create_index('idx_analytics_project_id', 'analytics', ['project_id'])
    op.create_index('idx_analytics_metric_type', 'analytics', ['metric_type'])
    op.create_index('idx_analytics_recorded_at', 'analytics', ['recorded_at'])
    op.create_index('idx_analytics_project_metric', 'analytics', ['project_id', 'metric_type'])
    
    # Performance table indexes
    op.create_index('idx_performance_project_id', 'performance', ['project_id'])
    op.create_index('idx_performance_metric_type', 'performance', ['metric_type'])
    op.create_index('idx_performance_recorded_at', 'performance', ['recorded_at'])
    op.create_index('idx_performance_project_metric', 'performance', ['project_id', 'metric_type'])
    
    # Logs table indexes
    op.create_index('idx_logs_level', 'logs', ['level'])
    op.create_index('idx_logs_source', 'logs', ['source'])
    op.create_index('idx_logs_created_at', 'logs', ['created_at'])
    op.create_index('idx_logs_level_source', 'logs', ['level', 'source'])
    op.create_index('idx_logs_created_at_desc', 'logs', [sa.text('created_at DESC')])
    
    # AI Services table indexes
    op.create_index('idx_ai_services_service_type', 'ai_services', ['service_type'])
    op.create_index('idx_ai_services_status', 'ai_services', ['status'])
    op.create_index('idx_ai_services_created_at', 'ai_services', ['created_at'])
    
    # AI Insights table indexes
    op.create_index('idx_ai_insights_project_id', 'ai_insights', ['project_id'])
    op.create_index('idx_ai_insights_insight_type', 'ai_insights', ['insight_type'])
    op.create_index('idx_ai_insights_created_at', 'ai_insights', ['created_at'])
    op.create_index('idx_ai_insights_project_type', 'ai_insights', ['project_id', 'insight_type'])
    
    # AI Dashboard table indexes
    op.create_index('idx_ai_dashboard_dashboard_type', 'ai_dashboard', ['dashboard_type'])
    op.create_index('idx_ai_dashboard_created_at', 'ai_dashboard', ['created_at'])
    
    # Junction table indexes
    op.create_index('idx_project_resources_project_id', 'project_resources', ['project_id'])
    op.create_index('idx_project_resources_resource_id', 'project_resources', ['resource_id'])
    op.create_index('idx_project_risks_project_id', 'project_risks', ['project_id'])
    op.create_index('idx_project_risks_risk_id', 'project_risks', ['risk_id'])
    
    # Text search indexes (PostgreSQL specific)
    op.execute("CREATE INDEX idx_projects_name_search ON projects USING gin(to_tsvector('english', name))")
    op.execute("CREATE INDEX idx_projects_description_search ON projects USING gin(to_tsvector('english', description))")
    op.execute("CREATE INDEX idx_features_name_search ON features USING gin(to_tsvector('english', name))")
    op.execute("CREATE INDEX idx_features_description_search ON features USING gin(to_tsvector('english', description))")
    op.execute("CREATE INDEX idx_resources_name_search ON resources USING gin(to_tsvector('english', name))")
    op.execute("CREATE INDEX idx_resources_description_search ON resources USING gin(to_tsvector('english', description))")

def downgrade():
    """Remove performance indexes"""
    
    # Drop text search indexes
    op.execute("DROP INDEX IF EXISTS idx_projects_name_search")
    op.execute("DROP INDEX IF EXISTS idx_projects_description_search")
    op.execute("DROP INDEX IF EXISTS idx_features_name_search")
    op.execute("DROP INDEX IF EXISTS idx_features_description_search")
    op.execute("DROP INDEX IF EXISTS idx_resources_name_search")
    op.execute("DROP INDEX IF EXISTS idx_resources_description_search")
    
    # Drop junction table indexes
    op.drop_index('idx_project_risks_risk_id', 'project_risks')
    op.drop_index('idx_project_risks_project_id', 'project_risks')
    op.drop_index('idx_project_resources_resource_id', 'project_resources')
    op.drop_index('idx_project_resources_project_id', 'project_resources')
    
    # Drop AI Dashboard table indexes
    op.drop_index('idx_ai_dashboard_created_at', 'ai_dashboard')
    op.drop_index('idx_ai_dashboard_dashboard_type', 'ai_dashboard')
    
    # Drop AI Insights table indexes
    op.drop_index('idx_ai_insights_project_type', 'ai_insights')
    op.drop_index('idx_ai_insights_created_at', 'ai_insights')
    op.drop_index('idx_ai_insights_insight_type', 'ai_insights')
    op.drop_index('idx_ai_insights_project_id', 'ai_insights')
    
    # Drop AI Services table indexes
    op.drop_index('idx_ai_services_created_at', 'ai_services')
    op.drop_index('idx_ai_services_status', 'ai_services')
    op.drop_index('idx_ai_services_service_type', 'ai_services')
    
    # Drop Logs table indexes
    op.drop_index('idx_logs_created_at_desc', 'logs')
    op.drop_index('idx_logs_level_source', 'logs')
    op.drop_index('idx_logs_created_at', 'logs')
    op.drop_index('idx_logs_source', 'logs')
    op.drop_index('idx_logs_level', 'logs')
    
    # Drop Performance table indexes
    op.drop_index('idx_performance_project_metric', 'performance')
    op.drop_index('idx_performance_recorded_at', 'performance')
    op.drop_index('idx_performance_metric_type', 'performance')
    op.drop_index('idx_performance_project_id', 'performance')
    
    # Drop Analytics table indexes
    op.drop_index('idx_analytics_project_metric', 'analytics')
    op.drop_index('idx_analytics_recorded_at', 'analytics')
    op.drop_index('idx_analytics_metric_type', 'analytics')
    op.drop_index('idx_analytics_project_id', 'analytics')
    
    # Drop Reports table indexes
    op.drop_index('idx_reports_project_type', 'reports')
    op.drop_index('idx_reports_created_at', 'reports')
    op.drop_index('idx_reports_report_type', 'reports')
    op.drop_index('idx_reports_project_id', 'reports')
    
    # Drop Backlogs table indexes
    op.drop_index('idx_backlogs_project_status', 'backlogs')
    op.drop_index('idx_backlogs_created_at', 'backlogs')
    op.drop_index('idx_backlogs_priority', 'backlogs')
    op.drop_index('idx_backlogs_status', 'backlogs')
    op.drop_index('idx_backlogs_project_id', 'backlogs')
    
    # Drop Risks table indexes
    op.drop_index('idx_risks_project_level', 'risks')
    op.drop_index('idx_risks_created_at', 'risks')
    op.drop_index('idx_risks_status', 'risks')
    op.drop_index('idx_risks_risk_level', 'risks')
    op.drop_index('idx_risks_project_id', 'risks')
    
    # Drop Resources table indexes
    op.drop_index('idx_resources_project_type', 'resources')
    op.drop_index('idx_resources_created_at', 'resources')
    op.drop_index('idx_resources_status', 'resources')
    op.drop_index('idx_resources_resource_type', 'resources')
    op.drop_index('idx_resources_project_id', 'resources')
    
    # Drop Features table indexes
    op.drop_index('idx_features_project_priority', 'features')
    op.drop_index('idx_features_project_status', 'features')
    op.drop_index('idx_features_created_at', 'features')
    op.drop_index('idx_features_priority', 'features')
    op.drop_index('idx_features_status', 'features')
    op.drop_index('idx_features_project_id', 'features')
    
    # Drop Projects table indexes
    op.drop_index('idx_projects_user_status', 'projects')
    op.drop_index('idx_projects_status_priority', 'projects')
    op.drop_index('idx_projects_user_id', 'projects')
    op.drop_index('idx_projects_updated_at', 'projects')
    op.drop_index('idx_projects_created_at', 'projects')
    op.drop_index('idx_projects_priority', 'projects')
    op.drop_index('idx_projects_status', 'projects')
