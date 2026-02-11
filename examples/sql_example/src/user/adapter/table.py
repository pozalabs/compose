from sqlalchemy import Column, Integer, MetaData, String, Table

metadata = MetaData()

users_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100)),
    Column("email", String(100)),
    Column("created_at", String),
    Column("updated_at", String),
)
