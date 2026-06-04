from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # AUTH
    # =========================
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # =========================
    # SAAS FLAGS
    # =========================
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)

    # =========================
    # SAAS LIMITS
    # =========================
    invoice_limit = Column(Integer, default=5)

    # =========================
    # STRIPE / SUBSCRIPTION
    # =========================
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # =========================
    # RELATION TO INVOICES (CRITICAL FOR SAAS)
    # =========================
    invoices = relationship(
        "Invoice",
        back_populates="owner",
        cascade="all, delete"
    )