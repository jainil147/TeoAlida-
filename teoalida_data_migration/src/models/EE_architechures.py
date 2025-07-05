# models/ee_architectures.py
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from models import Base
from sqlalchemy.orm import relationship

class EEArchitecture(Base):
    __tablename__ = 'ee_architectures'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    introduced_year = Column(Integer, nullable=False)
    version = Column(Float)
    type = Column(String(50), nullable=False)
    communication_protocols = Column(Text)
    description = Column(Text)
    supported_feature_list = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

