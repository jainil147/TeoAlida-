import pandas as pd
import time
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from db_connection import get_db_connection
from models import Base
from models.model import Model
from models.fuel_types import FuelType
from models.engine_types import EngineType
from models.body_types import BodyType
from models.vehicles import Vehicle
from models.trans_types import TransType
from models.drive_train_types import DrivetrainType

def log_message(message):
    print(f"[{datetime.now()}] {message}")

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

def ensure_session_alive(session, engine):
    try:
        session.execute(text("SELECT 1"))
        return session
    except OperationalError:
        log_message("Session is invalid. Recreating session...")
        session.rollback()
        session.close()
        return get_session(engine)

def get_valid_enum(session, enum_name):
    try:
        result = session.execute(text(f'SELECT unnest(enum_range(NULL::{enum_name}))')).fetchall()
        return set(row[0] for row in result)
    except Exception as e:
        log_message(f"Error fetching enum '{enum_name}': {e}")
        return set()

def cache_existing(session, model_class, field_name, id_field="id"):
    """Cache existing objects from DB as {field_value: id} dict."""
    records = session.query(model_class).all()
    return {getattr(r, field_name): getattr(r, id_field) for r in records}

def bulk_get_or_create(session, model_class, field_name, values, id_field="id"):
    """
    Given a set of values, check which exist in DB, insert missing ones,
    then return mapping value -> id for all.
    """
    existing = cache_existing(session, model_class, field_name, id_field)
    to_create = [v for v in values if v and v not in existing]

    if to_create:
        session.bulk_save_objects([model_class(**{field_name: v}) for v in to_create])
        session.commit()

    # Refresh cache after insert
    existing.update(cache_existing(session, model_class, field_name, id_field))
    return existing

def normalize_drive_type(drive_type):
    if pd.isna(drive_type) or not isinstance(drive_type, str):
        return None
    return ''.join(word[0].upper() for word in drive_type.strip().split())

def transform_vehicle_data(df, session, engine, valid_fuel_types, valid_trans_types, valid_body_types):
    log_message("Transforming vehicle data...")

    df = df.rename(columns={
        "Model": "model_name",
        "Trim": "trim",
        "Engine type ": "engine_type_name",
        "Fuel type": "fuel_type_name",
        "Transmission": "trans_type_name",
        "Drive type": "drivetrain_type_name",
        "Body type": "body_type_name",
        "Car classification": "vehicle_type",
        "Image URL": "vehicle_image",
    })

    # Pre-collect all unique values for lookups
    model_names = set(df["model_name"].dropna().unique())
    engine_type_names = set(df["engine_type_name"].dropna().unique())

    fuel_type_names = set(
        v.strip() for v in df["fuel_type_name"].dropna().unique()
        if v.strip() in valid_fuel_types
    )
    trans_type_names = set(
        v.strip() for v in df["trans_type_name"].dropna().unique()
        if v.strip() in valid_trans_types
    )
    drivetrain_names = set(
        normalize_drive_type(v) for v in df["drivetrain_type_name"].dropna().unique()
    )
    drivetrain_names.discard(None)

    body_type_names = set(
        v.strip() for v in df["body_type_name"].dropna().unique()
        if v.strip() in valid_body_types
    )

    # Bulk get or create mappings
    model_map = bulk_get_or_create(session, Model, "name", model_names)
    engine_type_map = bulk_get_or_create(session, EngineType, "name", engine_type_names, "EngineTypeID")
    fuel_type_map = bulk_get_or_create(session, FuelType, "FuelType", fuel_type_names, "FuelTypeID")
    trans_type_map = bulk_get_or_create(session, TransType, "TransType", trans_type_names, "TransTypeID")
    drivetrain_map = bulk_get_or_create(session, DrivetrainType, "Type", drivetrain_names, "DrivetrainTypeID")
    body_type_map = bulk_get_or_create(session, BodyType, "Type", body_type_names)

    vehicles = []

    for _, row in df.iterrows():
        model_id = model_map.get(row.get("model_name"))
        engine_type_id = engine_type_map.get(row.get("engine_type_name"))

        fuel_raw = row.get("fuel_type_name")
        fuel_type_id = fuel_type_map.get(fuel_raw.strip()) if isinstance(fuel_raw, str) else None

        trans_raw = row.get("trans_type_name")
        trans_type_id = trans_type_map.get(trans_raw.strip()) if isinstance(trans_raw, str) else None

        drive_raw = row.get("drivetrain_type_name")
        drivetrain_type_name = normalize_drive_type(drive_raw)
        drivetrain_type_id = drivetrain_map.get(drivetrain_type_name)

        body_raw = row.get("body_type_name")
        body_type_id = body_type_map.get(body_raw.strip()) if isinstance(body_raw, str) else None

        vehicle = Vehicle(
            trim=row.get("trim"),
            model_id=model_id,
            engine_type=engine_type_id,
            vehicle_type=row.get("vehicle_type"),
            fuel_type=fuel_type_id,
            vehicle_image=row.get("vehicle_image"),
            transmission=trans_type_id,
            drivetrain=drivetrain_type_id,
            body_type=body_type_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        vehicles.append(vehicle)

    log_message("Vehicle data transformation complete.")
    return vehicles

def migrate_vehicle_data(file_path):
    session = None
    try:
        log_message("Loading data from Excel...")
        data = pd.read_excel(file_path).drop_duplicates()

        engine = get_db_connection()
        session = get_session(engine)

        log_message("Fetching valid enum values...")
        valid_fuel_types = get_valid_enum(session, '"enum_fuel_types_FuelType"')
        valid_trans_types = get_valid_enum(session, '"enum_trans_types_TransType"')
        valid_body_types = get_valid_enum(session, '"enum_body_types_Type"')

        log_message("Creating tables if not exist...")
        Base.metadata.create_all(engine)

        vehicles = transform_vehicle_data(data, session, engine, valid_fuel_types, valid_trans_types, valid_body_types)

        log_message(f"Inserting {len(vehicles)} vehicle records in bulk...")
        batch_size = 500  # optional batch size, adjust if needed
        for i in range(0, len(vehicles), batch_size):
            batch = vehicles[i:i+batch_size]
            session.bulk_save_objects(batch)
            session.commit()
            log_message(f"Inserted batch {i // batch_size + 1}")

        log_message("Data migration completed successfully.")

    except FileNotFoundError:
        log_message(f"File not found: {file_path}")
    except Exception as e:
        log_message(f"Unexpected error: {e}")
        if session:
            session.rollback()
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    migrate_vehicle_data("../data/teoalida_data.xlsx")
