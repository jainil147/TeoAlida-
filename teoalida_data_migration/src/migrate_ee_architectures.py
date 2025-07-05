import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from models.EE_architechures import Base, EEArchitecture
from datetime import datetime
from db_connection import get_db_connection
import uuid

def extract_ee_architectures_data(data):
    """Extract and transform EE architecture data from the car dataset."""

    # ✅ Map dataset columns to EE_Architectures table
    column_mapping = {
        "Year": "introduced_year",
        "Platform code / generation number": "version",
        "Drive type": "type",
        "Fuel type": "communication_protocols",
        "Review": "description",
        "Pros": "supported_feature_list",
    }
    data.rename(columns=column_mapping, inplace=True)

    # ✅ Ensure required columns exist
    required_columns = [
        "introduced_year",
        "version",
        "type",
        "communication_protocols",
        "description",
        "supported_feature_list",
    ]
    for col in required_columns:
        if col not in data.columns:
            data[col] = None

    # ✅ Assign EE Architecture type
    data["type"] = data["type"].apply(lambda x: "Domain-Based" if "all wheel drive" in str(x).lower() else "Centralized")

    # ✅ Assign communication protocols
    data["communication_protocols"] = data["communication_protocols"].apply(lambda x: "CAN, LIN, Ethernet" if "electric" in str(x).lower() else "CAN, LIN")

    # ✅ Assign version number (assume BMW G20 platform is v1.2)
    data["version"] = data["version"].apply(lambda x: 1.2 if str(x) == "G20" else 1.0)

    # ✅ Assign default timestamps
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()

    return data

def migrate_ee_architectures(file_path):
    """Load EE architecture data from Excel and insert it into PostgreSQL."""
    try:
        # ✅ Ensure file exists
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return

        print(f"Loading EE architecture data from {file_path}...")
        data = pd.read_excel(file_path)

        # ✅ Remove duplicates
        print("Removing duplicate rows...")
        data = data.drop_duplicates()

        # ✅ Transform data
        transformed_data = extract_ee_architectures_data(data)

        # ✅ Connect to database
        engine = get_db_connection()
        Session = sessionmaker(bind=engine)
        session = Session()

        # ✅ Create tables if they don't exist
        Base.metadata.create_all(engine)

        print("Adding EE Architecture data to PostgreSQL...")

        # ✅ Insert data into EE_Architectures table
        for _, row in transformed_data.iterrows():
            new_entry = EEArchitecture(
                id=uuid.uuid4(),  # Generate unique ID
                introduced_year=row["introduced_year"],
                version=row["version"],
                type=row["type"],
                communication_protocols=row["communication_protocols"],
                description=row["description"],
                supported_feature_list=row["supported_feature_list"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            session.add(new_entry)

        session.commit()
        print("✅ EE Architecture data successfully added.")

        session.close()

    except Exception as e:
        print(f"❌ Error adding EE Architecture data: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_ee_architectures("../data/teoalida_data.xlsx")
