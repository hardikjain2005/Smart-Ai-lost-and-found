# database

PostgreSQL support files. `init/*.sql` runs once, when the database volume is first created.

Tables (`users`, `items`, `claims`) are created by the backend at startup. A small additive helper in
`backend/app/db/migrations.py` adds newer columns to existing databases. A full migration framework
(Alembic) is not set up yet.
