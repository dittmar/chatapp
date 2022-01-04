"""Create users and messages tables

Revision ID: a79cdd25befc
Revises: 7f4b62f311a6
Create Date: 2021-12-31 00:51:53.368768

"""
from alembic import op
from schema import message_table, user_table

import sqlalchemy as sqlalchemy

# revision identifiers, used by Alembic.
revision = 'a79cdd25befc'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("username", sqlalchemy.String, unique=True, index=True)
    )

    op.create_table(
        'messages',
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("message", sqlalchemy.String),
        sqlalchemy.Column("senderId", sqlalchemy.Integer),
        sqlalchemy.Column("receiverId", sqlalchemy.Integer, nullable=True),
        sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), server_default=sqlalchemy.func.now())
    )


def downgrade():
    op.drop_table('messages')
    op.drop_table('users')
