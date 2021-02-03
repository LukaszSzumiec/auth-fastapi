from pydantic import BaseModel, Field
from fastapi import Form
from typing import Optional, List, Type
import inspect


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
            annotation=field.outer_type_,
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, 'as_form', _as_form)
    return cls


class Token(BaseModel):
    access_token: str
    token_type: str
    scopes: List[str] = []


class TokenData(BaseModel):
    id: Optional[int] = None
    scopes: List[str] = []


class UserBase(BaseModel):
    username: str = Field(...)


@as_form
class UserCreate(UserBase):
    password: str = Field(...)
    is_superuser: str = Field(...)


@as_form
class UserLogin(UserBase):
    password: str = Field(...)


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Success(BaseModel):
    success: bool
