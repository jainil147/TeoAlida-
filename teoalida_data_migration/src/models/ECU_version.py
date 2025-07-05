from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from models import Base  # Ensure Base is imported from your models package


class ECUVersion(Base):
    """Define ECU_version table."""
    __tablename__ = 'ECU_version'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=False)
    name = Column(String(255), nullable=True)
    
    functional_domain = Column(String(100), nullable=True)  # Assuming enum or text — update if you have an enum type defined
    
    # supplier = Column(Integer, ForeignKey('supplier.id'), nullable=True)
    
    part_number = Column(String(100), unique=True, nullable=True)
    
    fcc_id = Column(String(100), nullable=True)
    
    # software_BOM = Column(String, ForeignKey('software_BOM.id'), nullable=True)
    # hardware_BOM = Column(Integer, ForeignKey('hardware_BOM.HardwareBOM_ID'), nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<ECUVersion(part_number='{self.part_number}', name='{self.name}')>"
    
