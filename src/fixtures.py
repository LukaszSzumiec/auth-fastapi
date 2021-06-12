import os
import sqlalchemy
from sqlalchemy import create_engine
from fastapi import Depends
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


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

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password):
    return pwd_context.hash(password)


class User(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    scopes = sqlalchemy.Column(sqlalchemy.String)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean)

Base.metadata.create_all(bind=engine)

def create_user(user, db):
    try:
        hashed_password = get_password_hash(user.get('password'))
        db_user = User(id=user.get('id'), username=user.get('username'), hashed_password=hashed_password, scopes=user.get('scopes'), is_active=False)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        return None

users = [
    {
        'id': 1,
        'username': 'admin',
        'password': 'admin',
        'scopes': 'intelligent_admin',
    },
    {
        'id': 2,
        'username': 'user1',
        'password': 'user1',
        'scopes': 'intelligent_basic',
    },
    {
        'id': 3,
        'username': 'user2',
        'password': 'user2',
        'scopes': 'intelligent_basic',
    },
]

try:
    db = SessionLocal()
    for user in users:
        create_user(user, db)
except Exception as e:
    print(e)
finally:
        db.close()