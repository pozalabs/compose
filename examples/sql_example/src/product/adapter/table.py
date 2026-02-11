from sqlalchemy import Column, Float, Integer, MetaData, String, Table

metadata = MetaData()

products_table = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100)),
    Column("price", Float),
    Column("created_at", String),
    Column("updated_at", String),
)
