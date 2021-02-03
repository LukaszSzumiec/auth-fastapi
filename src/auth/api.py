from datetime import timedelta
from fastapi import Depends, HTTPException, status, APIRouter, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .crud import create_user
from ..database import get_db
from ..scheme import User, Token, UserCreate, UserLogin

router_auth = APIRouter()


@router_auth.post('/api/register/', response_model=User)
async def register_user(form_data: UserCreate = Depends(UserCreate.as_form), db=Depends(get_db)):
    """Register new user.

    Args:
        form_data: UserCreate form data.
        db: database Session object.

    Returns:
        Returns user instance or error message.
    """
    user = create_user(db, form_data)
    if not user:
        raise HTTPException(status_code=409, detail='Username already registered.')
    return user


@router_auth.post('/api/token/')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print(user.scopes.split(' '))
    access_token = create_access_token(data={'sub': str(user.id), 'scopes': user.scopes.split(' ')}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'type': 'Bareer', 'success': True, 'expire_time': ACCESS_TOKEN_EXPIRE_MINUTES}


@router_auth.get('/api/refresh')
async def refresh(db = Depends(get_db), current_user: User = Depends(get_current_user)):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': str(current_user.id), 'scopes': current_user.scopes.split(' ')}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'type': 'Bareer', 'success': True, 'expire_time': ACCESS_TOKEN_EXPIRE_MINUTES}
