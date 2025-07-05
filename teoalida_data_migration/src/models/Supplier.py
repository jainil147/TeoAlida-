from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from models import Base  # Ensure Base is imported from your models package

class Supplier(Base):
    """Define Supplier table."""
    __tablename__ = 'supplier'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    short_name = Column(String(100), nullable=False)  # Short name or abbreviation (e.g., Bosch)
    full_name = Column(String(255), nullable=False)   # Full legal name
    duns_number = Column(String(50), unique=True, nullable=True)  # DUNS number

    supplier_type = Column(String(50), nullable=False)  # Type of supplier (could be enum in future)

    stock_symbol = Column(String(50), nullable=True)     # Stock ticker symbol
    trading_market = Column(String(100), nullable=True)  # Stock market

    website_url = Column(String(255), nullable=True)     # Official website

    hq_country = Column(String(100), nullable=False)     # Country of operation
    established_year = Column(Integer, nullable=True)    # Year founded

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Supplier(short_name='{self.short_name}', full_name='{self.full_name}')>"
