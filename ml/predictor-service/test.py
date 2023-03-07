from app import app
import pytest


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_delete():
    response = app.test_client().get('/delete?name=some_name')
    assert response.status_code == 200


def test_get_models():
    response = app.test_client().get('/get_models?user=123456')
    assert response.status_code == 200
