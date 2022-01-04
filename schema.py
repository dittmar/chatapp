import sqlalchemy as sqlalchemy
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

metadata = sqlalchemy.MetaData()

user_table = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("hashed_password", sqlalchemy.String),
    sqlalchemy.Column("salt", sqlalchemy.String)
)

message_table = sqlalchemy.Table(
    'messages',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("message", sqlalchemy.String),
    sqlalchemy.Column("senderId", sqlalchemy.Integer),
    sqlalchemy.Column("receiverId", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), server_default=sqlalchemy.func.now())
)