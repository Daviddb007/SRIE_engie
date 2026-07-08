import json
import pytest


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


def test_index_contains_stonelytics(client):
    response = client.get('/')
    assert b'Stonelytics' in response.data


def test_contacto_missing_fields(client):
    response = client.post('/contacto',
                           data=json.dumps({'name': 'Test'}),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['ok'] is False


def test_contacto_valid_submission(client):
    payload = {
        'name': 'Juan Perez',
        'email': 'juan@test.com',
        'business': 'Restaurante',
        'whatsapp': '+573001234567',
        'message': 'Quiero un micrositio',
    }
    response = client.post('/contacto',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
