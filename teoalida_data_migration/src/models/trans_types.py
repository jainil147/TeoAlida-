from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from models import Base

class TransType(Base):
    """Define TransTypes table."""
    __tablename__ = 'trans_types'

    TransTypeID = Column(Integer, primary_key=True, autoincrement=True)  # ✅ Auto-increment primary key
    TransType = Column(String(100), nullable=False, unique=True)  # ✅ Unique transmission type
    description = Column(String) 
    gear_count = Column(Integer)  
    created_at = Column(DateTime, default=datetime.now)  # ✅ Timestamp for record creation
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # ✅ Auto-update timestamp

    def __repr__(self):
        return f"<TransType(trans_type='{self.trans_type}')>"
