import sqlalchemy
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, default=4, autoincrement=True, primary_key=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    scopes = sqlalchemy.Column(sqlalchemy.String)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean)
