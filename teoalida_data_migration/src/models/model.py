import uuid
from sqlalchemy import Column, String, Date, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models import Base
from .manufacturer import Manufacturer  # Import Manufacturer class here
from sqlalchemy import Integer


class Model(Base):
    """Define the Model table."""
    __tablename__ = 'models'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manufacturer_id = Column(UUID(as_uuid=True), ForeignKey('manufacturers.id'))  # Foreign key reference to manufacturers
    name = Column(String(255), nullable=False)
    year = Column(Integer)
    operating_country = Column(String)  # Or use an Enum or a separate table for countries
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    manufacturer_relation = relationship("Manufacturer", back_populates="models")
