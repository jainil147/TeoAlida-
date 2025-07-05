import pandas as pd
import uuid
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Date
from sqlalchemy import text
from models import Base
from models.manufacturer import Manufacturer
from models.model import Model
from db_connection import get_db_connection
from utils import log_message


def get_valid_countries(session):
    result = session.execute(text("SELECT unnest(enum_range(NULL::countries))")).fetchall()
    return set(row[0] for row in result)


def transform_model_data(data, session):
    log_message("Transforming Model data...")

    column_mapping = {
        "Make": "manufacturer_short_name",
        "Model": "name",
        "Year": "year",
        "Country of origin": "operating_country",
        "Trim (description)": "description"
    }

    data.rename(columns=column_mapping, inplace=True)

    required_columns = ["id", "manufacturer", "name", "year", "operating_country", "description"]

    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    data["id"] = data["id"].apply(lambda x: uuid.uuid4() if pd.isna(x) else uuid.UUID(str(x)))

    manufacturer_ids = []
    for manufacturer_short_name in data["manufacturer_short_name"]:
        if pd.isna(manufacturer_short_name):
            manufacturer_ids.append(None)
            continue
        manufacturer = session.query(Manufacturer).filter_by(short_name=manufacturer_short_name).first()
        if manufacturer:
            manufacturer_ids.append(manufacturer.id)
        else:
            log_message(f"Manufacturer '{manufacturer_short_name}' not found.")
            manufacturer_ids.append(None)

    data["manufacturer"] = [uuid.UUID(str(x)) if x else None for x in manufacturer_ids]
    valid_countries = get_valid_countries(session)
    data["operating_country"] = data["operating_country"].astype(str).str.extract(r'/?([A-Za-z\s]+)$')[0].str.strip()
    data["operating_country"] = data["operating_country"].apply(
    lambda country: country if country in valid_countries else None
)
    data["year"] = pd.to_datetime(data["year"], errors="coerce").dt.to_period("Y").dt.to_timestamp()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()

    data = data[required_columns + ["created_at", "updated_at"]]

    return data

def migrate_models(file_path):
    try:
        log_message("Loading Excel data...")
        data = pd.read_excel(file_path)
        data = data.drop_duplicates()

        engine = get_db_connection()
        Session = sessionmaker(bind=engine)
        session = Session()

        log_message("Creating tables if not exist...")
        Base.metadata.create_all(engine)

        transformed_data = transform_model_data(data.copy(), session)
        transformed_data = transformed_data.dropna(subset=["manufacturer"])

        log_message("Inserting data into 'model' table...")

        transformed_data.to_sql(
            "model",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            dtype={
                "id": UUID,
                "manufacturer": UUID,
                "year": Date
            }
        )

        log_message("Migration successful.")

    except Exception as e:
        log_message(f"Migration failed: {e}")
        raise

    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    migrate_models("../data/teoalida_data.xlsx")
