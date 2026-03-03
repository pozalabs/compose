from sqlalchemy import Column, MetaData, String, Table

metadata = MetaData()

users_table = Table(
    "user",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("name", String(100)),
    Column("email", String(100)),
    Column("created_at", String),
    Column("updated_at", String),
)
