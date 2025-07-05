import pandas as pd
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from utils import log_message
from db_connection import get_db_connection

# Data Transformation Function for BodyTypes
def transform_body_types_data(data):
    """Transform data to match BodyTypes table schema."""
    log_message("Transforming Body Type data...")

    column_mapping = {
        "Body type": "type",  # Assuming column name in Excel
        "Trim (description)": "description",
        "Doors": "doors",
        "Total seating": "seating_capacity_range",
        "Cargo capacity (cu ft)": "cargo_capacity",  # we need in form of - small, medium, large but data has capacity in cubic
        "Car classification": "common_use_cases",
    }

    # Rename columns based on mapping
    data.rename(columns=column_mapping, inplace=True)

    required_columns = ["type", "description", "doors", "seating_capacity_range", "cargo_capacity", "common_use_cases"]

    # Add missing columns
    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    # Convert 'doors' to integer
    data["doors"] = pd.to_numeric(data["doors"], errors="coerce").astype("Int64")

    # Add timestamps
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()

    # Drop duplicates based on 'type' to ensure unique entries
    data.drop_duplicates(subset=["type"], inplace=True)

    # Ensure 'type' is not null
    data = data[data["type"].notnull()]

    # Select required columns (excluding 'id' because it's auto-incremented)
    data = data[required_columns + ["created_at", "updated_at"]]

    data = data.astype(object).where(pd.notna(data), None)


    return data

# Data Migration Function for BodyTypes
def migrate_body_types(file_path):
    """Load Excel data and migrate to PostgreSQL BodyTypes table using the BodyType model."""
    try:
        log_message("Loading data from Excel...")
        data = pd.read_excel(file_path)

        # Remove duplicate rows
        log_message("Removing duplicate rows...")
        data = data.drop_duplicates()

        # Transform data to match database schema
        transformed_data = transform_body_types_data(data)

        engine = get_db_connection()

        # Create a session for SQLAlchemy
        Session = sessionmaker(bind=engine)
        session = Session()

        # Import BodyType model inside the function to avoid circular import
        from models.body_types import Base, BodyType

        # Create the table if it doesn't exist
        log_message("Creating table if it doesn't exist...")
        Base.metadata.create_all(engine)

        # Create a list of BodyType objects to insert
        body_types = []
        for index, row in transformed_data.iterrows():
            body_type = BodyType(
                type=row['type'],
                description=row['description'],
                doors=row['doors'],
                seating_capacity_range=row['seating_capacity_range'],
                cargo_capacity=row['cargo_capacity'],
                common_use_cases=row['common_use_cases'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            body_types.append(body_type)

        # Bulk insert using SQLAlchemy ORM
        log_message("Inserting data into PostgreSQL BodyTypes table...")
        session.bulk_save_objects(body_types)
        session.commit()

        log_message("Data successfully migrated to PostgreSQL.")

    except Exception as e:
        log_message(f"Error during migration: {str(e)}")
        raise

    finally:
        session.close()

if __name__ == "__main__":
    migrate_body_types("../data/teoalida_data.xlsx")
