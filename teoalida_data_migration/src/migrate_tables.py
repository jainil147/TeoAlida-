from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, DateTime, Uuid, Text , Date
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID # only needed for postgresql
from db_connection import get_db_connection


Base = declarative_base()

class ECU_version(Base):
    __tablename__ = 'ECU_version'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=False)
    name = Column(String(255))
    functional_domain = Column(String(255)) # Or Enum, or table
    supplier = Column(UUID, ForeignKey('Supplier.id'))
    part_number = Column(String(100), unique=True)
    fcc_id = Column(String(100))
    software_BOM = Column(UUID(as_uuid=True), ForeignKey('Software_BOM.id'))
    hardware_BOM = Column(Integer, ForeignKey('Hardware_BOM.HardwareBOM_ID'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Supplier(Base):
    __tablename__ = 'Supplier'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_name = Column(String(255))
    full_name = Column(String(255))
    duns_number = Column(String(50))
    supplier_type = Column(String(255))
    stock_symbol = Column(String(50))
    trading_market = Column(String(100))
    website_url = Column(String(255))
    hq_country = Column(String(100))
    established_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Vehicles(Base):
    __tablename__ = 'Vehicles'
    id = Column(Integer, primary_key=True)

class Software_BOM(Base):
    __tablename__ = 'Software_BOM'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sw_version_id = Column(String(50))
    software_pkg = Column(UUID, ForeignKey('Software_Library.id'))
    source_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Software_Library(Base):
    __tablename__ = 'Software_Library'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    software_name = Column(String(255))
    software_version = Column(String(50))
    software_vendor = Column(UUID, ForeignKey('Supplier.id'))
    software_type = Column(String(255)) # or enum
    hash_value = Column(String(255))
    hash_type = Column(String(50))
    purl = Column(String(255))
    license_type = Column(String(100))
    license_url = Column(String(255))
    release_date = Column(Date)
    end_of_life_date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Hardware_BOM(Base):
    __tablename__ = 'Hardware_BOM'
    HardwareBOM_ID = Column(Integer, primary_key=True)
    hardware_pkg = Column(UUID, ForeignKey('Hardware_Library.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Hardware_Library(Base):
    __tablename__ = 'Hardware_Library'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hardware_name = Column(String(255), nullable=False)
    hardware_type = Column(String(255)) # or enum
    hardware_manufacturer = Column(UUID, ForeignKey('Supplier.id'))
    hardware_partnumber = Column(String(100))
    hardware_version = Column(String(50))


# Example Usage (replace with your database connection string)
engine = get_db_connection() #Example, change this.
Base.metadata.create_all(engine)

print("Tables created successfully")