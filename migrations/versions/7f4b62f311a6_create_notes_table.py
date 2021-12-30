"""Create notes table

Revision ID: 7f4b62f311a6
Revises: 
Create Date: 2021-12-30 15:22:23.199873

"""
from alembic import op
import sqlalchemy as sqlalchemy


# revision identifiers, used by Alembic.
revision = '7f4b62f311a6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notes',
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("text", sqlalchemy.String),
        sqlalchemy.Column("completed", sqlalchemy.Boolean)
    )


def downgrade():
    op.drop_table('notes')
