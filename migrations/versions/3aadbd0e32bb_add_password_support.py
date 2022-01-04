"""Add password support

Revision ID: 3aadbd0e32bb
Revises: a79cdd25befc
Create Date: 2022-01-03 23:06:56.504906

"""
from alembic import op
import sqlalchemy as sqlalchemy
from sqlalchemy.sql.expression import false


# revision identifiers, used by Alembic.
revision = '3aadbd0e32bb'
down_revision = 'a79cdd25befc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sqlalchemy.Column('hashed_password', sqlalchemy.String))
    op.add_column('users', sqlalchemy.Column('salt', sqlalchemy.String))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('salt')
        batch_op.drop_column('hashed_password')
