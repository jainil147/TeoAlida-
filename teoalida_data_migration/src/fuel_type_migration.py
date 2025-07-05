import pandas as pd
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from utils import log_message
from db_connection import get_db_connection

# Data Transformation Function for FuelTypes
def transform_fuel_types_data(data):
    """Transform data to match FuelTypes table schema."""
    log_message("Transforming Fuel Type data...")

    column_mapping = {
        "Fuel type": "fuel_type",  # Assuming column name in Excel
        "Trim (description)": "description",
    }

    # Rename columns based on mapping
    data.rename(columns=column_mapping, inplace=True)

    required_columns = ["fuel_type", "description"]

    # Add missing columns
    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    # Add timestamps
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()

    # Drop duplicates based on 'fuel_type' to ensure unique entries
    data.drop_duplicates(subset=["fuel_type"], inplace=True)

    # Ensure 'fuel_type' is not null
    data = data[data["fuel_type"].notnull()]

    # Select required columns (excluding 'id' because it's auto-incremented)
    data = data[required_columns + ["created_at", "updated_at"]]

    return data

# Data Migration Function for FuelTypes
def migrate_fuel_types(file_path):
    """Load Excel data and migrate to PostgreSQL FuelTypes table using the FuelType model."""
    try:
        log_message("Loading data from Excel...")
        data = pd.read_excel(file_path)

        # Remove duplicate rows
        log_message("Removing duplicate rows...")
        data = data.drop_duplicates()

        # Transform data to match database schema
        transformed_data = transform_fuel_types_data(data)

        engine = get_db_connection()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Import FuelType model inside the function to avoid circular import
        from models.fuel_types import Base, FuelType

        # Create the table if it doesn't exist
        log_message("Creating table if it doesn't exist...")
        Base.metadata.create_all(engine)

        # Fetch existing fuel_type values from the database
        existing_fuel_types = session.query(FuelType.fuel_type).all()
        existing_fuel_types_set = set(ft[0] for ft in existing_fuel_types)

        # Only insert new, non-duplicate fuel types
        fuel_types = []
        for _, row in transformed_data.iterrows():
            if row["fuel_type"] not in existing_fuel_types_set:
                fuel_type = FuelType(
                    fuel_type=row['fuel_type'],
                    description=row['description'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                fuel_types.append(fuel_type)

        # Bulk insert using SQLAlchemy ORM
        if fuel_types:
            log_message(f"Inserting {len(fuel_types)} new fuel types into PostgreSQL...")
            session.bulk_save_objects(fuel_types)
            session.commit()
            log_message("Data successfully migrated to PostgreSQL.")
        else:
            log_message("No new fuel types to insert. Skipping insert.")

    except Exception as e:
        log_message(f"Error during migration: {str(e)}")
        raise

    finally:
        session.close()

if __name__ == "__main__":
    migrate_fuel_types("../data/teoalida_data.xlsx")
