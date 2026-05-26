from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------------
# DATABASE
# ----------------------
DATABASE_URL = "sqlite:///./invoices.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ----------------------
# USERS TABLE
# ----------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


# ----------------------
# INVOICES TABLE (USER-BASED)
# ----------------------
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client = Column(String, index=True)
    amount = Column(Float)

    # 👇 LINK NA USERA (SAAAS CORE)
    user_id = Column(Integer, index=True)