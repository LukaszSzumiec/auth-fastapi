from fastapi import Depends, HTTPException, status, APIRouter, Security
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

from ..scheme import User, UserCreate, Token, TokenData
from .crud import get_user, create_user, get_user_by_username
from ..database import get_db
from ..utils import verify_password, oauth2_scheme


SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')
SECRET_REFRESH = os.environ.get('SECRET_REFRESH', 'refresh_secret')

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 1440

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

def authenticate_user(db, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1420)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_REFRESH, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        _id: int = int(payload.get('sub'))
        if _id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, id=_id)
    except JWTError:
        raise credentials_exception
    user = get_user(db, id=_id)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


# def auth_by_refresh_token(token: str, db):
#     payload = jwt.decode(str(token), SECRET_REFRESH, algorithms=[ALGORITHM])
#     try:
#         _id: int = int(payload.get('sub'))
#         if _id is None:
#             raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail='No',
#         headers={'WWW-Authenticate': 'Bearer'},
#     )
#     except JWTError:
#         raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail='No 2',
#         headers={'WWW-Authenticate': 'Bearer'},
#     )
#     user = get_user(db, id=_id)
#     if user is None:
#         raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail='No 3',
#         headers={'WWW-Authenticate': 'Bearer'},
#     )
#     return user
