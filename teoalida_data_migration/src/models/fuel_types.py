from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from models import Base

class FuelType(Base):
    """Define FuelTypes table."""
    __tablename__ = 'fuel_types'

    FuelTypeID = Column(Integer, primary_key=True, autoincrement=True)
    FuelType = Column(String, nullable=False, unique=True)  # Fuel type (e.g., Petrol, Diesel, Electric)
    description = Column(Text)  # Description of the fuel type
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<FuelType(fuel_type='{self.fuel_type}')>"

