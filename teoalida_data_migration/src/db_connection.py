import json
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()


def get_db_connection():
    """Connect to the database using the configuration file."""
    with open("../config/config.json", "r") as file:
        config = json.load(file)
    
        db_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
        
    return create_engine(db_url)

