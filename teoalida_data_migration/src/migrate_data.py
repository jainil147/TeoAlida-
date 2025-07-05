import pandas as pd
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils import log_message
from db_connection import get_db_connection
from sqlalchemy.dialects.postgresql import UUID
import re

# Define the base class for SQLAlchemy models
Base = declarative_base()

class Manufacturer(Base):
    """Define Manufacturer table with primary key."""
    __tablename__ = 'manufacturers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_name = Column(String(255))
    long_name = Column(Text)
    country = Column(String(255))
    logo_url = Column(String(255))  # Updated field type to String(255)
    established_year = Column(Integer)
    contact_info = Column(Text)
    duns_number = Column(String(255))
    stock_symbol = Column(String(50))
    trading_market = Column(String(100))
    website_url = Column(Text)
    headquarters_address = Column(Text)
    additional_info = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


def is_valid_url(url):
    """Validate if the given string is a valid URL."""
    return bool(re.match(r'^https?://[^\s]+$', str(url)))


def transform_manufacturers_data(data):
    """Transform data to match the Manufacturers table schema."""
    log_message("Transforming Manufacturer data...")

    # Mapping Excel columns to DB columns
    column_mapping = {
        "ID": "id",
        "Make": "short_name",
        "Country of origin": "country",
        "Image URL": "logo_url",
        "Year": "established_year",
        "Source URL": "website_url",
        "Trim (description)": "additional_info",
    }

    # Rename columns
    data.rename(columns=column_mapping, inplace=True)

    # Define required columns
    required_columns = [
        "id", "short_name", "long_name", "country", "logo_url",
        "established_year", "contact_info", "duns_number",
        "stock_symbol", "trading_market", "website_url",
        "headquarters_address", "additional_info"
    ]

    # Add missing columns with None
    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    # Handle missing IDs
    data["id"] = data["id"].apply(lambda x: str(uuid.uuid4()) if pd.isna(x) or len(str(x)) != 36 else str(x))

    # Convert year
    data["established_year"] = pd.to_numeric(data["established_year"], errors="coerce").astype("Int64")

    # Truncate strings to avoid errors on remaining String(N) fields
    MAX_LENGTHS = {
        "short_name": 255,
        "country": 255,
        "duns_number": 255,
        "stock_symbol": 50,
        "trading_market": 100,
        "logo_url": 255  # Set limit for logo_url field
    }

    for col, max_len in MAX_LENGTHS.items():
        if col in data.columns:
            data[col] = data[col].astype(str).str.slice(0, max_len)

    # Validate and clean logo_url
    if "logo_url" in data.columns:
        data["logo_url"] = data["logo_url"].fillna("").apply(lambda x: x if is_valid_url(x) else None)

    # Add timestamps
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()

    return data[required_columns + ["created_at", "updated_at"]]


def migrate_manufacturers(file_path):
    """Load Excel data and migrate to PostgreSQL Manufacturers table."""
    try:
        log_message("Loading data from Excel...")
        data = pd.read_excel(file_path)

        log_message("Removing duplicate rows...")
        data = data.drop_duplicates()

        transformed_data = transform_manufacturers_data(data)

        engine = get_db_connection()

        Base.metadata.create_all(engine)

        log_message("Inserting data into PostgreSQL Manufacturers table in chunks...")
        transformed_data.to_sql("manufacturers", con=engine, if_exists="append", index=False, chunksize=1000)

        log_message("Data successfully migrated to PostgreSQL.")

    except Exception as e:
        log_message(f"Error during migration: {str(e)}")
        raise


if __name__ == "__main__":
    migrate_manufacturers("../data/teoalida_data.xlsx")
