from fastapi import FastAPI

from .auth import router_auth
from .model import Base
from .database import engine


app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(router_auth, prefix='')
