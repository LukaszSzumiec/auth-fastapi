from datetime import timedelta
from fastapi import Depends, HTTPException, status, APIRouter, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from typing import Optional

from .auth import get_current_user, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, create_refresh_token, auth_by_refresh_token
from .crud import create_user
from ..database import get_db
from ..scheme import User, Token, UserCreate

router_auth = APIRouter()


# class Settings(BaseModel):
#     authjwt_secret_key: str = 'secret_key'

# @AuthJWT.load_config
# def get_config():
#     return Settings()


# @router_auth.exception_handler(AuthJWTException)
# def authjwt_exception_handler(request: Request, exc: AuthJWTException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={'detail': exc.message}
#     )


@router_auth.get('/api/users/me', response_model=User)
async def get_me(db = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Endpoint returns current logged user.

    Args:
        current_user: logged in User object.

    Returns:
        Returns logged in user instance.

    """
    return current_user


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
async def login(user: UserCreate = Depends(UserCreate.as_form), db=Depends(get_db)):
    user = authenticate_user(db, user.username, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={'sub': str(user.id)}, expires_delta=refresh_token_expires
    )
    response = JSONResponse(content={'access_token': access_token, 'success': True, 'expire_time': ACCESS_TOKEN_EXPIRE_MINUTES})
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return response


@router_auth.post('/api/refresh/')
async def refresh(refresh_token: Optional[str] = Cookie(None), db=Depends(get_db)):
    user = auth_by_refresh_token(refresh_token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
    )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.id}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'type': 'Bareer', 'success': True, 'expire_time': ACCESS_TOKEN_EXPIRE_MINUTES}
