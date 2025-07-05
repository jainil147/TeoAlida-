from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP, func, Enum
from sqlalchemy.orm import relationship
from models import Base
from enum import Enum as PyEnum

# Define an Enum for Domain (if needed)
class DomainEnum(PyEnum):
    ADAS = "ADAS"
    Infotainment = "Infotainment"
    Security = "Security"
    Safety = "Safety"
    Powertrain = "Powertrain"
    Other = "Other"

class Function(Base):
    __tablename__ = 'functions'  # Table name should match your DB schema

    id = Column(Integer, primary_key=True, autoincrement=True)
    function_list_id = Column(Integer, ForeignKey('functionlists.functionlistid'), nullable=False)
    order = Column(Integer, nullable=True)
    name = Column(String(255), unique=True, nullable=False)
    domain = Column(Enum(DomainEnum), nullable=True)  # Enum for categorized domains
    safety_relevant = Column(Boolean, default=False)
    security_relevant = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    introduced_year = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())  # Auto timestamp
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship to FunctionList (without redefining it)
    function_list = relationship("FunctionList", back_populates="functions")
