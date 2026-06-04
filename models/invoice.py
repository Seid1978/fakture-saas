from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # BUSINESS DATA
    # =========================
    client = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    # =========================
    # STATUS (SAAS WORKFLOW)
    # =========================
    status = Column(String, default="Pending")  # Pending, Paid, Cancelled

    # =========================
    # OPTIONAL BUSINESS FIELD (preporučeno)
    # =========================
    description = Column(String, nullable=True)

    # =========================
    # OWNER LINK (MULTI-TENANT SAAS)
    # =========================
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship(
        "User",
        back_populates="invoices"
    )

    # =========================
    # TIMESTAMP
    # =========================
    created_at = Column(DateTime, default=datetime.utcnow)