from sqlalchemy import Column, String, ForeignKey, DateTime, Integer,Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db_connection import Base
import uuid
from datetime import datetime
from db_connection import get_db_connection


class EEArchitecture(Base):
    __tablename__ = 'ee_architectures'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    introduced_year = Column(Integer, nullable=False)
    version = Column(Float)
    type = Column(String(50), nullable=False)
    communication_protocols = Column(Text)
    description = Column(Text)
    supported_feature_list = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # Relationship with FunctionList
    function_lists = relationship("FunctionList", back_populates="ee_architecture")


class FunctionList(Base):
    __tablename__ = 'function_lists'

    FunctionListID = Column(Integer, primary_key=True, autoincrement=True)
    EEArchitectureID = Column(UUID(as_uuid=True), ForeignKey('ee_architectures.id'), nullable=False)
    Name = Column(String(255), nullable=False)
    Description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    ee_architecture = relationship("EEArchitecture", back_populates="function_lists")  # Fix

def create_tables():
    """Creates EEArchitecture and FunctionList tables in the database."""
    try:
        # Get database connection
        engine = get_db_connection()

        # Create tables
        Base.metadata.create_all(engine)

        print("Tables 'ee_architectures' and 'function_lists' created successfully.")

    except Exception as e:
        print(f"Error creating tables: {str(e)}")

if __name__ == "__main__":
    create_tables()