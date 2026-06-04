from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    client = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    # SaaS v5: workflow
    status = Column(String, default="Pending")  # Pending, Paid, Cancelled

    user_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)