import pytest
from cryptography.fernet import Fernet

from app import create_app
from app.extensions import db as _db
from config import TestingConfig


@pytest.fixture(scope='session')
def app():
    TestingConfig.FERNET_KEY = Fernet.generate_key().decode('utf-8')
    TestingConfig.SECRET_KEY = 'test-secret-key'
    application = create_app(TestingConfig)
    yield application


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    return app.test_client()


@pytest.fixture
def runner(app, db):
    return app.test_cli_runner()
