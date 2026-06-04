import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =========================
# DATABASE URL
# =========================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./faktura.db"  # default za development
)

# =========================
# ENGINE
# =========================
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# =========================
# SESSION
# =========================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =========================
# BASE (SINGLE SOURCE OF TRUTH)
# =========================
Base = declarative_base()

# =========================
# DEPENDENCY (FastAPI)
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()