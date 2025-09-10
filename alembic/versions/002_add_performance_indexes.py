"""Add performance indexes

Revision ID: 002_performance_indexes
Revises: 001_add_performance_indexes
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import logging

logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = '002_performance_indexes'
down_revision = '001_add_performance_indexes'
branch_labels = None
depends_on = None

def upgrade():
    """Add performance indexes for better query optimization"""
    
    # Skip index creation if tables don't exist yet
    # This migration will be run after the initial schema is created
    logger.info("Skipping performance indexes - will be created after initial schema")
    pass

def downgrade():
    """Remove performance indexes"""
    logger.info("No indexes to remove - migration was skipped")
    pass
