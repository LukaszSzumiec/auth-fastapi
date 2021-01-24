from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from have_a_nice_day.src.database import Base, get_db
from have_a_nice_day.src.main import app

SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db


def set_up_register_user():
    response = client.post('/api/register',
                           data={
                               'username': 'test',
                               'password': 'test'
                           },
                           )
    assert response.status_code == 200


def set_up_login():
    response = client.post('/api/token',
                           data={
                               'username': 'test',
                               'password': 'test'
                           },
                           )
    return response.json().get('access_token')


def test_get_me():
    set_up_register_user()
    access_token = set_up_login()
    response = client.get('/api/users/me',
                          headers={'Authorization':
                                       f'Bearer {access_token}'
                                   })
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('username') == 'test'


def test_get_me_no_token():
    resonse = client.get(
        '/api/users/me',
        headers={'bareer': 'notoken.no.token'}
    )
    assert resonse.status_code == 401


def test_register_new_user():
    response = client.post('/api/register',
                           data={
                               'username': 'new_user',
                               'password': 'test'
                           },
                           )
    assert response.status_code == 200


def test_login():
    response = client.post('/api/token',
                           data={
                               'username': 'test',
                               'password': 'test'
                           }
                           )
    assert response.status_code == 200
