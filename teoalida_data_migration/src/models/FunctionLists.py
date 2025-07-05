# models/function_lists.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from models import Base
from sqlalchemy.orm import relationship

class FunctionList(Base):
    __tablename__ = 'function_lists'

    FunctionListID = Column(Integer, primary_key=True, autoincrement=True)
    EEArchitectureID = Column(UUID(as_uuid=True), ForeignKey('ee_architectures.id'), nullable=False)
    Name = Column(String(255), nullable=False)
    Description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    ee_architecture = relationship("EEArchitecture", back_populates="function_lists")  # Fix

