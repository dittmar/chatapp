import sqlalchemy as sqlalchemy
from sqlalchemy import sql

metadata = sqlalchemy.MetaData()

user_table = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, nullable=False, unique=True, index=True)
)

message_table = sqlalchemy.Table(
    'messages',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("message", sqlalchemy.String),
    sqlalchemy.Column("senderId", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("receiverId", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("createdAt", sqlalchemy.Time, nullable=False)
)