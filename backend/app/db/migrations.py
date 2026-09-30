"""Minimal additive schema upgrades for databases created before a column existed.

`Base.metadata.create_all` creates missing tables but never alters existing ones. Until Alembic is
introduced, new columns are added here (idempotently, never dropping or rewriting data).
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# (table, column, DDL type + default). Existing rows receive the default.
ADDITIVE_COLUMNS = [
    ("items", "visibility", "VARCHAR(10) NOT NULL DEFAULT 'PUBLIC'"),
]


def apply_additive_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, column, ddl in ADDITIVE_COLUMNS:
            if table in inspector.get_table_names() and column not in {
                c["name"] for c in inspector.get_columns(table)
            }:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
