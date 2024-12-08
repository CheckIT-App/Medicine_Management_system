import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.database import Base, DATABASE_URL  # Import your Base and DATABASE_URL
from app.models import * 
# Config object from alembic.ini
config = context.config

# Set the sqlalchemy.url dynamically
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# If logging is configured in alembic.ini, set it up
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata to use for 'autogenerate' support
target_metadata = Base.metadata
print(Base.metadata.tables.keys())
def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    Run migrations in 'online' mode.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
