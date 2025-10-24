"""Add age column to users table

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add age column to users table
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove age column from users table
    op.drop_column('users', 'age')
