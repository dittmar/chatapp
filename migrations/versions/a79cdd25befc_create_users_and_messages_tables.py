"""Create users and messages tables

Revision ID: a79cdd25befc
Revises: 7f4b62f311a6
Create Date: 2021-12-31 00:51:53.368768

"""
from alembic import op
import sqlalchemy as sqlalchemy
import chat_tables as tables

# revision identifiers, used by Alembic.
revision = 'a79cdd25befc'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        tables.user_table.name,
        *tables.user_table.columns
    )

    op.create_table(
        tables.message_table.name,
        *tables.message_table.columns
    )


def downgrade():
    op.drop_table(tables.message_table.name)
    op.drop_table(tables.user_table.name)
