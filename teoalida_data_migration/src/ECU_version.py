import pandas as pd
import time
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from db_connection import get_db_connection
from models import Base
from models.ECU_version import ECUVersion
from models.model import Model
from models.vehicles import Vehicle
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

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

def get_vehicle_id(session, model_name, year=None):
    try:
        model = session.query(Model).filter(Model.name.ilike(f"%{model_name.strip()}%")).first()
        if not model:
            log_message(f"[Warning] No model found matching '{model_name}'")
            return None
        vehicle = session.query(Vehicle).filter(Vehicle.model_id == model.id).first()
        if vehicle:
            return vehicle.id
        else:
            log_message(f"[Warning] No vehicle found for model '{model_name}'")
    except Exception as e:
        log_message(f"[Error] get_vehicle_id: {e}")
        session.rollback()
    return None

def scrape_ecu_data(make, model, year, driver):
    base_url = f"https://{make.lower()}.oempartsonline.com/search"
    url = f"{base_url}?search_str=ECU&make={make}&model={model}&year={year}"

    log_message(f"Scraping ECU for {make} {model} {year} at URL: {url}")

    try:
        driver.get(url)
        time.sleep(8)
    except Exception as e:
        log_message(f"[Skipped] Failed to load page: {e}")
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_blocks = soup.select(".product-details-col")

    results = []
    for block in product_blocks:
        try:
            title_el = block.select_one(".product-title a h2")
            part_number_el = block.select_one(".catalog-product-id a")

            part = {
                "name": title_el.text.strip() if title_el else None,
                "part_number": part_number_el.text.strip() if part_number_el else None,
            }

            if part["name"] and part["part_number"]:
                results.append(part)
            else:
                log_message("[Warning] Incomplete part skipped.")
        except Exception as e:
            log_message(f"[Warning] Block error: {e}")

    log_message(f"Found {len(results)} ECU parts")
    return results

def migrate_ecu_data_from_excel(vehicle_excel_path):
    engine = get_db_connection()
    session = get_session(engine)
    Base.metadata.create_all(engine)

    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = uc.Chrome(version_main=137, options=options)

    try:
        df_vehicles = pd.read_excel(vehicle_excel_path)
        log_message(f"Loaded {len(df_vehicles)} rows from Excel")

        df_vehicles = df_vehicles.drop_duplicates(subset=["Model", "Year", "Make"])
        log_message(f"After dropping duplicates, {len(df_vehicles)} rows remain")

        vehicle_cache = {}

        for idx, row in df_vehicles.iterrows():
            model = str(row.get("Model")).strip()
            year = row.get("Year")
            make = str(row.get("Make")).strip()

            log_message(f"Row {idx}: Model={model}, Year={year}, Make={make}")

            if not all([model, year, make]):
                log_message(f"[Skipped] Missing required fields at row {idx}")
                continue

            cache_key = f"{model}|{year}"
            vehicle_id = vehicle_cache.get(cache_key)

            if not vehicle_id:
                session = ensure_session_alive(session, engine)
                vehicle_id = get_vehicle_id(session, model, year)
                if vehicle_id is None:
                    log_message(f"[Skipped] No vehicle_id found for row {idx}")
                    continue
                vehicle_cache[cache_key] = vehicle_id

            ecus = scrape_ecu_data(make, model, year, driver)

            for ecu in ecus:
                part_number = ecu["part_number"]

                # Check if already exists
                if session.query(ECUVersion).filter_by(part_number=part_number).first():
                    log_message(f"[Duplicate] Skipped {part_number}")
                    continue

                ecu_record = ECUVersion(
                    vehicle_id=vehicle_id,
                    name=ecu["name"],
                    part_number=part_number,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                try:
                    session.add(ecu_record)
                    session.commit()
                    log_message(f"[Inserted] {part_number} for {make} {model} {year}")
                except Exception as e:
                    session.rollback()
                    log_message(f"[Error] Insert failed for {part_number}: {e}")

        log_message("✅ ECU data migration completed.")

    except Exception as e:
        log_message(f"[Error] Migration failed: {e}")
        session.rollback()
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        session.close()

if __name__ == "__main__":
    migrate_ecu_data_from_excel("../data/teoalida_data.xlsx")
