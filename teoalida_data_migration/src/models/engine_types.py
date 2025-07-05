from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from models import Base

class EngineType(Base):
    """Define EngineTypes table."""
    __tablename__ = 'engine_types'

    EngineTypeID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    displacement = Column(Float)
    configuration = Column(String(50))
    power_output_hp = Column(Integer)
    power_output_kw = Column(Integer)
    torque_nm = Column(Integer)
    aspiration = Column(String(50))
    cylinder_count = Column(Integer)
    electric_motor_count = Column(Integer)
    battery_capacity_kwh = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<EngineType(name='{self.name}')>"

