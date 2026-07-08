import json
import pytest


@pytest.fixture
def client(app):
    return app.test_client()


def test_quiz_page_returns_200(client):
    response = client.get('/demo/growth')
    assert response.status_code == 200


def test_quiz_page_contains_form(client):
    response = client.get('/demo/growth')
    assert b'quiz-step' in response.data


def test_quiz_submit_missing_contact(client):
    payload = {
        'answers': [{'step': 1, 'value': 'restaurante'}],
        'contact': {'name': '', 'email': ''},
    }
    response = client.post('/demo/growth/submit',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 400


def test_quiz_submit_valid(client):
    payload = {
        'answers': [
            {'step': 1, 'value': 'restaurante'},
            {'step': 2, 'value': 'presencia'},
            {'step': 3, 'value': 'no'},
            {'step': 4, 'value': 'basico'},
            {'step': 5, 'value': 'no'},
            {'step': 6, 'value': 'ninguna'},
            {'step': 7, 'value': 'no'},
        ],
        'contact': {
            'name': 'Juan Perez',
            'email': 'juan@test.com',
            'phone': '+573001234567',
        },
    }
    response = client.post('/demo/growth/submit',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    assert data['plan']['name'] == 'Start'
    assert data['points'] == 4
