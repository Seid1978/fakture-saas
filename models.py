from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# -----------------------
# USER MODEL
# -----------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    invoices = relationship("Invoice", back_populates="owner")


# -----------------------
# INVOICE MODEL
# -----------------------
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    client = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="pending")

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="invoices")