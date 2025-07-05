from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from models import Base


class DrivetrainType(Base):
    __tablename__ = 'drive_train_types'

    DrivetrainTypeID = Column(Integer, primary_key=True, autoincrement=True)  # Primary key, auto-incrementing
    Type = Column(String(255), nullable=False, unique=True)  # Not null, unique
    description = Column(Text, nullable=True)  # Detailed description of the drivetrain type
    use_case = Column(Text, nullable=True)  # Common use cases or applications
    created_at = Column(DateTime, default=datetime.utcnow)  # Record creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Record last update timestamp

    def __repr__(self):
        return f"<DrivetrainType(type='{self.type}')>"

