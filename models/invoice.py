from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    client = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="Pending")
    date = Column(String, nullable=True)

    # 🔗 owner (FK)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # 🔥 relationship (BITNO ZA SAAS)
    owner = relationship("User", back_populates="invoices")