"""Add performance indexes

Revision ID: 001_add_performance_indexes
Revises: 
Create Date: 2025-01-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_performance_indexes'
down_revision = 'c62d3e72fe03'
branch_labels = None
depends_on = None


def upgrade():
    """Add critical performance indexes"""
    
    # Projects table indexes
    op.create_index('idx_projects_status_id', 'projects', ['status_id'])
    op.create_index('idx_projects_priority_id', 'projects', ['priority_id'])
    op.create_index('idx_projects_criticality_id', 'projects', ['criticality_id'])
    op.create_index('idx_projects_created_at', 'projects', ['created_at'])
    op.create_index('idx_projects_due_date', 'projects', ['due_date'])
    op.create_index('idx_projects_start_date', 'projects', ['start_date'])
    op.create_index('idx_projects_is_active', 'projects', ['is_active'])
    
    # Composite indexes for common queries
    op.create_index('idx_projects_status_priority', 'projects', ['status_id', 'priority_id'])
    op.create_index('idx_projects_active_dates', 'projects', ['is_active', 'start_date', 'due_date'])
    op.create_index('idx_projects_portfolio_status', 'projects', ['portfolio_id', 'status_id'])
    
    # Features table indexes
    op.create_index('idx_features_project_id', 'features', ['project_id'])
    op.create_index('idx_features_status_id', 'features', ['status_id'])
    op.create_index('idx_features_priority_id', 'features', ['priority_id'])
    op.create_index('idx_features_created_at', 'features', ['created_at'])
    
    # Composite indexes for features
    op.create_index('idx_features_project_status', 'features', ['project_id', 'status_id'])
    op.create_index('idx_features_project_priority', 'features', ['project_id', 'priority_id'])
    
    # Backlogs table indexes
    op.create_index('idx_backlogs_status_id', 'backlogs', ['status_id'])
    op.create_index('idx_backlogs_priority_id', 'backlogs', ['priority_id'])
    op.create_index('idx_backlogs_created_at', 'backlogs', ['created_at'])
    op.create_index('idx_backlogs_backlog_id', 'backlogs', ['backlog_id'])
    op.create_index('idx_backlogs_name', 'backlogs', ['name'])
    
    # Composite indexes for backlogs
    op.create_index('idx_backlogs_status_priority', 'backlogs', ['status_id', 'priority_id'])
    
    # Resources table indexes
    op.create_index('idx_resources_is_active', 'resources', ['is_active'])
    op.create_index('idx_resources_created_at', 'resources', ['created_at'])
    op.create_index('idx_resources_role', 'resources', ['role'])
    op.create_index('idx_resources_experience_level', 'resources', ['experience_level'])
    op.create_index('idx_resources_availability_percentage', 'resources', ['availability_percentage'])
    
    # Functions table indexes
    op.create_index('idx_functions_name', 'functions', ['name'])
    op.create_index('idx_functions_is_active', 'functions', ['is_active'])
    op.create_index('idx_functions_created_at', 'functions', ['created_at'])
    
    # Platforms table indexes
    op.create_index('idx_platforms_is_active', 'platforms', ['is_active'])
    op.create_index('idx_platforms_created_at', 'platforms', ['created_at'])
    
    # Lookup tables indexes
    op.create_index('idx_statuses_is_active', 'statuses', ['is_active'])
    op.create_index('idx_priorities_is_active', 'priorities', ['is_active'])
    op.create_index('idx_risks_is_active', 'risks', ['is_active'])
    
    # Performance monitoring indexes
    op.create_index('idx_projects_performance', 'projects', ['created_at', 'updated_at'])
    op.create_index('idx_features_performance', 'features', ['created_at', 'updated_at'])
    op.create_index('idx_backlogs_performance', 'backlogs', ['created_at', 'updated_at'])


def downgrade():
    """Remove performance indexes"""
    
    # Drop all indexes in reverse order
    op.drop_index('idx_projects_performance', 'projects')
    op.drop_index('idx_features_performance', 'features')
    op.drop_index('idx_backlogs_performance', 'backlogs')
    
    # Drop lookup table indexes
    op.drop_index('idx_risks_is_active', 'risks')
    op.drop_index('idx_priorities_is_active', 'priorities')
    op.drop_index('idx_statuses_is_active', 'statuses')
    
    # Drop platform indexes
    op.drop_index('idx_platforms_created_at', 'platforms')
    op.drop_index('idx_platforms_is_active', 'platforms')
    
    # Drop function indexes
    op.drop_index('idx_functions_created_at', 'functions')
    op.drop_index('idx_functions_is_active', 'functions')
    op.drop_index('idx_functions_name', 'functions')
    
    # Drop resource indexes
    op.drop_index('idx_resources_availability_percentage', 'resources')
    op.drop_index('idx_resources_experience_level', 'resources')
    op.drop_index('idx_resources_role', 'resources')
    op.drop_index('idx_resources_created_at', 'resources')
    op.drop_index('idx_resources_is_active', 'resources')
    
    # Drop backlog indexes
    op.drop_index('idx_backlogs_status_priority', 'backlogs')
    op.drop_index('idx_backlogs_name', 'backlogs')
    op.drop_index('idx_backlogs_backlog_id', 'backlogs')
    op.drop_index('idx_backlogs_created_at', 'backlogs')
    op.drop_index('idx_backlogs_priority_id', 'backlogs')
    op.drop_index('idx_backlogs_status_id', 'backlogs')
    
    # Drop feature indexes
    op.drop_index('idx_features_project_priority', 'features')
    op.drop_index('idx_features_project_status', 'features')
    op.drop_index('idx_features_created_at', 'features')
    op.drop_index('idx_features_priority_id', 'features')
    op.drop_index('idx_features_status_id', 'features')
    op.drop_index('idx_features_project_id', 'features')
    
    # Drop project indexes
    op.drop_index('idx_projects_portfolio_status', 'projects')
    op.drop_index('idx_projects_active_dates', 'projects')
    op.drop_index('idx_projects_status_priority', 'projects')
    op.drop_index('idx_projects_is_active', 'projects')
    op.drop_index('idx_projects_start_date', 'projects')
    op.drop_index('idx_projects_due_date', 'projects')
    op.drop_index('idx_projects_created_at', 'projects')
    op.drop_index('idx_projects_criticality_id', 'projects')
    op.drop_index('idx_projects_priority_id', 'projects')
    op.drop_index('idx_projects_status_id', 'projects')
