import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.engine_types import Base, EngineType
from datetime import datetime
from db_connection import get_db_connection

def transform_engine_types_data(data):
    """Transform data to match EngineTypes schema."""

    # Map columns from Excel to database fields
    column_mapping = {
        "Engine type": "name",
        "Trim (description)": "description",
        "Horsepower (HP)": "power_output_hp",
        "Kilowatts": "power_output_kw",
        "Cylinders": "cylinder_count",
        "EPA electricity range (mi)": "electric_motor_count",
        "Battery capacity (kWh)": "battery_capacity_kwh",
    }

    data.rename(columns=column_mapping, inplace=True)

    # Ensure all required columns exist
    required_columns = [
        "name", "description", "displacement", "configuration",
        "power_output_hp", "power_output_kw", "torque_nm",
        "aspiration", "cylinder_count", "electric_motor_count",
        "battery_capacity_kwh"
    ]

    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    # Keep only the required columns
    data = data[required_columns]

    # Convert numeric fields and fill NaNs
    data["power_output_hp"] = pd.to_numeric(data["power_output_hp"], errors="coerce").fillna(0).astype(int)
    data["power_output_kw"] = pd.to_numeric(data["power_output_kw"], errors="coerce").fillna(0).astype(int)
    data["cylinder_count"] = pd.to_numeric(data["cylinder_count"], errors="coerce").fillna(0).astype(int)
    data["electric_motor_count"] = pd.to_numeric(data["electric_motor_count"], errors="coerce").fillna(0).astype(int)
    data["battery_capacity_kwh"] = pd.to_numeric(data["battery_capacity_kwh"], errors="coerce")

    # Drop rows where 'name' is missing (NOT NULL constraint)
    missing_name_rows = data[data["name"].isnull()]
    if not missing_name_rows.empty:
        print(f"⚠️  Skipping {len(missing_name_rows)} rows with missing 'name'")
        # Optional: Save skipped rows for review
        # missing_name_rows.to_csv("skipped_engine_types.csv", index=False)

    data = data[data["name"].notnull()]  # Remove rows with null 'name'

    # Add timestamps
    now = datetime.now()
    data["created_at"] = now
    data["updated_at"] = now

    return data

def migrate_engine_types(file_path):
    """Load Excel data and migrate to PostgreSQL EngineTypes table."""
    try:
        print("📥 Loading data from Excel...")
        data = pd.read_excel(file_path)

        print("🧹 Removing duplicate rows...")
        data = data.drop_duplicates()

        print("🔄 Transforming data...")
        transformed_data = transform_engine_types_data(data)

        engine = get_db_connection()
        Session = sessionmaker(bind=engine)
        session = Session()

        print("🛠️ Creating tables if they don't exist...")
        Base.metadata.create_all(engine)

        print("🚀 Inserting data into PostgreSQL EngineTypes table...")
        transformed_data.to_sql("engine_types", con=engine, if_exists="append", index=False, chunksize=1000)

        print("✅ Data successfully migrated to PostgreSQL.")
        session.close()

    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_engine_types("../data/teoalida_data.xlsx")
