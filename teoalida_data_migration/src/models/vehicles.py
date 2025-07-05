import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, ForeignKeyConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models import Base


class Vehicle(Base):
    """Define Vehicles table."""
    __tablename__ = 'vehicles'

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    model_id = Column(Integer, ForeignKey('model.id'), nullable=False)
    vin_filter = Column(String(17), nullable=False, unique=True)
    trim = Column(String(50))
    engine_type = Column(Integer, ForeignKey('engine_types.EngineTypeID'))
    powertrain_type = Column(String(50))
    vehicle_type = Column(String(50))
    fuel_type = Column(Integer, ForeignKey('fuel_types.FuelTypeID'))
    transmission = Column(Integer, ForeignKey('trans_types.TransTypeID'))
    drivetrain = Column(Integer, ForeignKey('drive_train_types.DrivetrainTypeID'))
    body_type = Column(Integer, ForeignKey('body_types.id'))
    vehicle_image = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


