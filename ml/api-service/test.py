from app import app
import pytest


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_datasets_list():
    response = app.test_client().get('/datasets/list')
    assert response.status_code == 200

def test_get_models():
    response = app.test_client().get('/models/list')
    assert response.status_code == 200
