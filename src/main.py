from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router_auth
from .model import Base
from .database import engine

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    'localhost:3000',
    'http://localhost:3000/',
    'http://localhost:3000/',
    'http://localhost:3000'
]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(router_auth, prefix='')
