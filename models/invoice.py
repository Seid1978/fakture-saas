from sqlalchemy import Column, Integer, String, Float
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client = Column(String)
    amount = Column(Float)
    status = Column(String, default="pending")