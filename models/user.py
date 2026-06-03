from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # auth
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)

    # stripe
    stripe_customer_id = Column(String, nullable=True)

    # SaaS v3 tracking
    invoice_count = Column(Integer, default=0)

    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # relations
    invoices = relationship("Invoice", back_populates="owner")