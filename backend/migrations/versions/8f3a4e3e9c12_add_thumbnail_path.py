"""add thumbnail_path to conversions

Revision ID: 8f3a4e3e9c12
Revises: 7dfc6b23d843
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8f3a4e3e9c12'
down_revision = '7dfc6b23d843'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('conversions', sa.Column('thumbnail_path', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('conversions', 'thumbnail_path')
