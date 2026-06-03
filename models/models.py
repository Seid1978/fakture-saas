from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# 👤 USER TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

    password = Column(String)  # or hashed_password (better)
    role = Column(String, default="user")

    # 🔗 relationship
    invoices = relationship("Invoice", backref="owner")


# 📄 INVOICE TABLE
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Float)

    status = Column(String, default="Pending")

    user_id = Column(Integer, ForeignKey("users.id"))