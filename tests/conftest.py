import pytest

@pytest.fixture()
def app():

    yield app

@pytest.fixture()
def client(app):
    app.test_client()