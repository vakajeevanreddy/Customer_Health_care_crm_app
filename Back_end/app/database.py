from fastapi import Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

SQL_SCHEME_DATABASE = "sqlite:///./healthcare_crm.db"

engine = create_engine(SQL_SCHEME_DATABASE, connect_args={"check_same_thread": False})
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Assesment_Record(Base):
    __tablename__ = "assesment_history"
    
    id = Column(Integer, primary_key=True, index=True)
    assesment_timestamp = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    Patient_name = Column(String, index=True)
    age = Column(Integer)
    medical_condition = Column(String)
    billing_amount = Column(Float)
    probability = Column(Float)
    risk_status = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()