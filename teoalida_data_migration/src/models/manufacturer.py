import uuid
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models import Base
from models import model

class Manufacturer(Base):
    """Define Manufacturer table with primary key."""
    __tablename__ = 'manufacturers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_name = Column(String)
    long_name = Column(String)
    country = Column(String)
    logo_url = Column(String)
    established_year = Column(Integer)
    contact_info = Column(String)
    duns_number = Column(String)
    stock_symbol = Column(String)
    trading_market = Column(String)
    website_url = Column(String)
    headquarters_address = Column(String)
    additional_info = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    models = relationship("Model", back_populates="manufacturer_relation")
