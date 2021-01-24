from datetime import timedelta
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from .auth import get_current_user, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .crud import create_user
from ..database import get_db
from ..scheme import User, Token, UserCreate

router_auth = APIRouter()


@router_auth.get("/api/users/me", response_model=User)
async def get_me(db = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Endpoint returns current logged user.

    Args:
        current_user: logged in User object.

    Returns:
        Returns logged in user instance.

    """
    return current_user


@router_auth.post('/api/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """Log in user.

    Args:
        form_data: User login form data.
        db: database Session object.

    Returns:
        Returns access token or error message.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router_auth.post('/api/register', response_model=User)
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
