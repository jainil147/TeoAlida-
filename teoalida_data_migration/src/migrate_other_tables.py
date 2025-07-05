from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, DateTime, Uuid, Text, Date, DECIMAL, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID 
from db_connection import get_db_connection


Base = declarative_base()




class Users(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(15))
    country = Column(String(100))
    profile_image_url = Column(String(255))
    subscription_type = Column(String(255), nullable=False, default='Free')
    status = Column(String(255), nullable=False, default='inactive')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Nvd_cve_records(Base):
    __tablename__ = 'nvd_cve_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cve_id = Column(String(50), unique=True, nullable=False)
    assigner_org_id = Column(String(100), nullable=False)
    assigner_short_name = Column(String(50), nullable=False)
    requester_user_id = Column(String(100))
    serial = Column(Integer)
    state = Column(String(20), nullable=False)
    title = Column(Text, nullable=False)
    date_public = Column(DateTime)
    date_updated = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(255))
    cvss_v3_vector = Column(String(255))
    cvss_v3_base_score = Column(DECIMAL(3, 1))
    cvss_v4_vector = Column(String(255))
    cvss_v4_base_score = Column(DECIMAL(3, 1))
    cwe_id = Column(Integer, ForeignKey('cwe_records.id'))
    solutions = Column(Text)
    workarounds = Column(Text)
    references = Column(JSON)
    taxonomy_mappings = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)



class Master_vuln_records(Base):
    __tablename__ = 'master_vuln_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vuln_id = Column(Text)
    status = Column(String(20), nullable=False)
    title = Column(Text, nullable=False)
    opencti_id = Column(String(100))
    severity = Column(String(255), nullable=False)
    description_expert = Column(Text, nullable=False)
    description_non_expert = Column(Text, nullable=False)
    date_discovered = Column(Date, nullable=False)
    date_reported = Column(Date)
    how_it_affects = Column(Text, nullable=False)
    what_can_be_done = Column(Text, nullable=False)
    fix_details = Column(Text, nullable=False)
    source_id_1 = Column(UUID, ForeignKey('nvd_cve_records.id'), nullable=False) # Changed to UUID
    source_id_2 = Column(UUID, ForeignKey('vulndb_records.id'), nullable=False) # Changed to UUID
    source_id_3 = Column(UUID, nullable=False) # Changed to UUID
    source_id_4 = Column(UUID, nullable=False) # Changed to UUID
    source_id_5 = Column(UUID, nullable=False) # Changed to UUID
    source_id_6 = Column(UUID, nullable=False) # Changed to UUID
    source_id_7 = Column(UUID, nullable=False) # Changed to UUID
    source_id_8 = Column(UUID, nullable=False) # Changed to UUID
    source_id_9 = Column(UUID, nullable=False) # Changed to UUID
    source_id_10 = Column(UUID, nullable=False) # Changed to UUID
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Vulndb_records(Base):
    __tablename__ = 'vulndb_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cve_id = Column(String(50), unique=True, nullable=False)
    assigner_org_id = Column(String(100), nullable=False)
    assigner_short_name = Column(String(50), nullable=False)
    requester_user_id = Column(String(100))
    serial = Column(Integer)
    state = Column(String(20), nullable=False)
    title = Column(Text, nullable=False)
    date_public = Column(DateTime)
    date_updated = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(255))
    cvss_v3_vector = Column(String(255))
    cvss_v3_base_score = Column(DECIMAL(3, 1))
    cvss_v4_vector = Column(String(255))
    cvss_v4_base_score = Column(DECIMAL(3, 1))
    cwe_id = Column(Integer, ForeignKey('cwe_records.id'))
    solutions = Column(Text)
    workarounds = Column(Text)
    references = Column(JSON)
    taxonomy_mappings = Column(JSON)
    epss_score = Column(DECIMAL(1,3))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)



class Epss_scores(Base):
    __tablename__ = 'epss_scores'
    id = Column(Integer, primary_key=True)
    cve_id = Column(String(50), ForeignKey('nvd_cve_records.cve_id'), nullable=False)
    score_date = Column(Date, nullable=False)
    epss_score = Column(DECIMAL(4, 3), nullable=False)
    percentile = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Cwe_records(Base):
    __tablename__ = 'cwe_records'
    id = Column(Integer, primary_key=True)
    cwe_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    weakness_abstraction = Column(String(50))
    related_weaknesses = Column(Text)
    applicable_platforms = Column(Text)
    likelihood_of_exploit = Column(String(255))
    consequences = Column(Text)
    mitigation = Column(Text)
    examples = Column(Text)
    references = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


    

engine = get_db_connection() #Example, change this.
Base.metadata.create_all(engine)

print("Tables created successfully")