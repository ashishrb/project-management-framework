"""merge heads 5fe3127cdfdb and 6a1d2b3c4d5e

Revision ID: 7a8b9c0d1e2f
Revises: 5fe3127cdfdb, 6a1d2b3c4d5e
Create Date: 2025-09-12
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a8b9c0d1e2f'
down_revision = ('5fe3127cdfdb', '6a1d2b3c4d5e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass


