"""Add friends list tables

Revision ID: c322a65e60e5
Revises: 3aadbd0e32bb
Create Date: 2022-01-05 01:21:25.630173

"""
from alembic import op
import sqlalchemy as sqlalchemy


# revision identifiers, used by Alembic.
revision = 'c322a65e60e5'
down_revision = '3aadbd0e32bb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_friends',
        sqlalchemy.Column("userId", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("friendId", sqlalchemy.Integer, primary_key=True)
    )


def downgrade():
    op.drop_table('user_friends')
