from sqlalchemy import Column, Integer, String, Boolean
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
    # SAAS LIMITS (V4)
    # =========================
    invoice_limit = Column(Integer, default=5)

    # =========================
    # STRIPE / LEMON SQUEEZY SUPPORT
    # =========================
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)