from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from models import Base

class BodyType(Base):
    """Define BodyTypes table."""
    __tablename__ = 'body_types'

    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅ Ensure auto-increment
    Type = Column(String(100), nullable=False, unique=True)  
    description = Column(String)
    doors = Column(Integer)
    seating_capacity_range = Column(String(50))
    cargo_capacity = Column(String)
    common_use_cases = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<BodyType(type='{self.type}')>"
