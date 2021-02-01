from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import model
from ..scheme import UserCreate
from ..utils import get_password_hash


def get_user(db: Session, id: int):
    return db.query(model.User).filter(model.User.id == id).first()


def get_user_by_username(db: Session, username: int):
    print(username)
    user = db.query(model.User).filter(model.User.username == username).first()
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    try:
        hashed_password = get_password_hash(user.password)
        db_user = model.User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        return None
