import pandas as pd
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from utils import log_message
from db_connection import get_db_connection

def transform_drivetrain_types_data(data):
    """Transform data to match DrivetrainTypes table schema."""
    log_message("Transforming Drivetrain Type data...")

    column_mapping = {
        "Drive type": "type",
        "Car classification": "use_case"
    }

    # Rename columns based on mapping
    data.rename(columns=column_mapping, inplace=True)

    required_columns = ["type", "description", "use_case"]

    # Add missing columns
    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    # Add timestamps
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()

    # Remove duplicates based on 'type'
    data.drop_duplicates(subset=["type"], inplace=True)

    # Remove rows where 'type' is NULL or empty
    data = data[data["type"].notnull() & (data["type"] != "")]

    # **Print data for debugging**
    print("\n🔍 Transformed Drivetrain Types Data:\n", data)

    return data

# ✅ Data Migration Function for Drivetrain Types
def migrate_drivetrain_types(file_path):
    """Load Excel data and migrate to PostgreSQL DrivetrainTypes table."""
    try:
        log_message("📂 Loading data from Excel...")
        data = pd.read_excel(file_path)

        # Print raw data for debugging
        print("\n📊 Raw Data from Excel:\n", data.head())

        # Remove duplicate rows
        log_message("🔍 Removing duplicate rows...")
        data = data.drop_duplicates()

        # Transform data to match database schema
        transformed_data = transform_drivetrain_types_data(data)

        # **Check if there is data to insert**
        if transformed_data.empty:
            log_message("⚠️ No valid data found in Excel! Aborting migration.")
            return

        engine = get_db_connection()

        # Create a session for SQLAlchemy
        Session = sessionmaker(bind=engine)
        session = Session()

        # Import DrivetrainType model inside the function to avoid circular import
        from models.drive_train_types import Base, DrivetrainType

        # Create the table if it doesn't exist
        log_message("🛠️ Creating table if it doesn't exist...")
        Base.metadata.create_all(engine)

        # Create a list of DrivetrainType objects to insert
        drivetrain_types = []
        for index, row in transformed_data.iterrows():
            drivetrain_type = DrivetrainType(
                type=row['type'],
                description=row['description'],
                use_case=row['use_case'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            drivetrain_types.append(drivetrain_type)

        # **Print objects before inserting**
        print("\n🚀 Prepared Data for Insertion:")
        for dt in drivetrain_types:
            print(f"Type: {dt.type}, Use Case: {dt.use_case}, Description: {dt.description}")

        # **Check if list is empty before inserting**
        if not drivetrain_types:
            log_message("⚠️ No data to insert into DrivetrainTypes table! Aborting.")
            return

        # Bulk insert using SQLAlchemy ORM
        log_message("💾 Inserting data into PostgreSQL DrivetrainTypes table...")
        session.bulk_save_objects(drivetrain_types)
        session.flush()  # **Force insert before commit**
        session.commit()

        log_message("✅ Data successfully migrated to PostgreSQL!")

    except Exception as e:
        log_message(f"❌ Error during migration: {str(e)}")
        session.rollback()
        raise

    finally:
        session.close()

if __name__ == "__main__":
    migrate_drivetrain_types("../data/teoalida_data.xlsx")
