import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ['DATABASE_URL']
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except:
    raise Exception('Connecting with database failed')

Base = declarative_base()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
