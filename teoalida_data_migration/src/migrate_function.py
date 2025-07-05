# import pandas as pd
# from datetime import datetime
# from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Boolean, DateTime, Text
# from sqlalchemy.orm import sessionmaker, declarative_base
# from db_connection import get_db_connection  # Assuming you have this
# from models.FunctionLists import FunctionList # Assuming you have this

# # --- Base Model ---
# Base = declarative_base()

# class Function(Base):
#     __tablename__ = 'functions'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     function_list_id = Column(Integer, ForeignKey('function_lists.FunctionListID'), nullable=False)
#     order = Column(Integer)
#     name = Column(String(255), unique=True, nullable=False)
#     domain = Column(String(255))
#     safety_relevant = Column(Boolean, default=False)
#     security_relevant = Column(Boolean, default=False)
#     description = Column(Text)
#     introduced_year = Column(Integer)
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# # --- Logging ---
# def log_message(message):
#     print(f"[{datetime.now()}] {message}")

# # --- Helper Function ---
# def get_or_create(session, model_class, filter_by_field, value, pk_field):
#     """Ensure an entry exists and return its primary key."""
#     if pd.isna(value) or value is None:
#         return None

#     existing_entry = session.query(model_class).filter(getattr(model_class, filter_by_field) == value).first()

#     if not existing_entry:
#         new_entry = model_class(**{filter_by_field: value})
#         session.add(new_entry)
#         session.commit()
#         log_message(f"Created new {model_class.__tablename__}: {value}")
#         return getattr(new_entry, pk_field)

#     return getattr(existing_entry, pk_field)

# # --- Data Transformation ---
# def transform_function_data(data, session):
#     """Transform Excel data to match the Function table schema."""
#     log_message("Transforming function data...")

#     functions_to_insert = []

#     for index, row in data.iterrows():
#         function_list_id = get_or_create(session, FunctionList, "name", row["function_list_name"], pk_field="FunctionListID")

#         if function_list_id is None:
#             log_message(f"Skipping row {index} due to missing FunctionList.")
#             continue

#         try:
#             function = Function(
#                 function_list_id=function_list_id,
#                 order=row.get("order"),
#                 name=row.get("function_name"),
#                 domain=row.get("domain"),
#                 safety_relevant=row.get("safety_relevant", False),
#                 security_relevant=row.get("security_relevant", False),
#                 description=row.get("description"),
#                 introduced_year=row.get("year"), # Directly using 'year'
#                 created_at=datetime.now(),
#                 updated_at=datetime.now()
#             )
#             functions_to_insert.append(function)
#         except Exception as e:
#             log_message(f"Error processing row {index}: {e}")

#     log_message("Function data transformation complete.")
#     return functions_to_insert

# # --- Data Migration ---
# def migrate_function_data(file_path):
#     """Load Excel data and insert into the database."""
#     session = None
#     try:
#         log_message("Loading data from Excel...")
#         data = pd.read_excel(file_path)
#         data = data.drop_duplicates()

#         engine = get_db_connection()
#         Session = sessionmaker(bind=engine)
#         session = Session()

#         # Create tables if they don't exist
#         log_message("Ensuring required tables exist...")
#         Base.metadata.create_all(engine)

#         transformed_functions = transform_function_data(data.copy(), session)

#         if transformed_functions:
#             log_message(f"Inserting {len(transformed_functions)} function records...")
#             try:
#                 session.bulk_save_objects(transformed_functions)
#                 session.commit()
#                 log_message(f"✅ Successfully inserted {len(transformed_functions)} records.")
#             except Exception as e:
#                 session.rollback()
#                 log_message(f"❌ Error inserting functions: {e}")
#         else:
#             log_message("⚠️ No functions inserted (possibly due to missing lookups).")

#     except FileNotFoundError:
#         log_message(f"❌ Error: File not found at {file_path}")
#     except Exception as e:
#         if session:
#             session.rollback()
#         log_message(f"❌ Unexpected error: {e}")
#     finally:
#         if session:
#             session.close()

# if __name__ == "__main__":
#     migrate_function_data("../data/teoalida_data.xlsx")

from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from db_connection import get_db_connection
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()

# FunctionList MUST be defined BEFORE Function
class FunctionList(Base):
    __tablename__ = 'function_lists'

    FunctionListID = Column(Integer, primary_key=True, autoincrement=True)
    EEArchitectureID = Column(UUID(as_uuid=True), ForeignKey('ee_architectures.id'), nullable=False)
    Name = Column(String(255), nullable=False)
    Description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Function(Base):
    __tablename__ = 'functions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    function_list_id = Column(Integer, ForeignKey('function_lists.FunctionListID'), nullable=False)
    order = Column(Integer)
    name = Column(String(255), unique=True, nullable=False)
    domain = Column(String(255))
    safety_relevant = Column(Boolean, default=False)
    security_relevant = Column(Boolean, default=False)
    description = Column(Text)
    introduced_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

engine = get_db_connection()
Base.metadata.create_all(engine)

print("Tables created successfully")