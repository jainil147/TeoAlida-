import pandas as pd
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from utils import log_message
from db_connection import get_db_connection

def transform_trans_types_data(data):
    """Transform data to match TransTypes table schema and extract the last word from trans_type."""
    log_message("Transforming Transmission Type data...")

    column_mapping = {
        "Transmission": "description",
    }

    # Rename columns based on mapping
    data.rename(columns=column_mapping, inplace=True)

    required_columns = ["trans_type", "description", "gear_count"]

    # Add missing columns
    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    # Convert 'gear_count' from description
    data["gear_count"] = data["description"].str.extract(r'(\d+)')
    data["gear_count"] = pd.to_numeric(data["gear_count"], errors="coerce")
    data["gear_count"] = data["gear_count"].astype("Int64")  # Nullable integer type
    data = data.astype(object).where(pd.notna(data), None)  # Replace NaN with None

    # **Extract only the last word from the trans_type field**
    data["trans_type"] = data["description"].str.split().str[-1]

    # Add timestamps
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()

    # Drop duplicates based on 'trans_type' to ensure unique entries
    data.drop_duplicates(subset=["trans_type"], inplace=True)

    # Ensure 'trans_type' is not null
    data = data[data["trans_type"].notnull()]

    # Select required columns (excluding 'id' because it's auto-incremented)
    data = data[required_columns + ["created_at", "updated_at"]]

    return data


# ✅ Data Migration Function for Transmission Types
def migrate_trans_types(file_path):
    """Load Excel data and migrate to PostgreSQL TransTypes table."""
    try:
        log_message("Loading data from Excel...")
        data = pd.read_excel(file_path)

        # Remove duplicate rows
        log_message("Removing duplicate rows...")
        data = data.drop_duplicates()

        # Transform data to match database schema
        transformed_data = transform_trans_types_data(data)

        engine = get_db_connection()

        # Create a session for SQLAlchemy
        Session = sessionmaker(bind=engine)
        session = Session()

        # Import TransType model inside the function to avoid circular import
        from models.trans_types import Base, TransType

        # Create the table if it doesn't exist
        log_message("Creating table if it doesn't exist...")
        Base.metadata.create_all(engine)

        # Create a list of TransType objects to insert
        trans_types = []
        for index, row in transformed_data.iterrows():
            trans_type = TransType(
                trans_type=row['trans_type'],
                description=row['description'],
                gear_count=row['gear_count'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            trans_types.append(trans_type)

        # Bulk insert using SQLAlchemy ORM
        log_message("Inserting data into PostgreSQL TransTypes table...")
        session.bulk_save_objects(trans_types)
        session.commit()

        log_message("✅ Data successfully migrated to PostgreSQL.")

    except Exception as e:
        log_message(f"❌ Error during migration: {str(e)}")
        raise

    finally:
        session.close()

if __name__ == "__main__":
    migrate_trans_types("../data/teoalida_data.xlsx")  # Change path as needed
