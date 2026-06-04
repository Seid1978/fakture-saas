from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from database import Base
import models  # IMPORTANT: load all models (User, Invoice, etc.)

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# TARGET METADATA (CRITICAL)
target_metadata = Base.metadata


# =========================
# OFFLINE MODE
# =========================
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


# =========================
# ONLINE MODE
# =========================
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


# =========================
# RUN MODE CHECK
# =========================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()