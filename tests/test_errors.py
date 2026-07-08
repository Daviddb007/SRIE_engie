"""Tests for error handlers and AppError hierarchy."""
import pytest
from core.errors import (
    AppError, NotFoundError, ValidationError,
    AuthenticationError, ConflictError,
)


def test_app_error_defaults():
    err = AppError()
    assert err.status_code == 500
    assert err.message == 'Internal server error'
    assert err.to_dict() == {'error': 'Internal server error'}


def test_app_error_custom():
    err = AppError(message='Custom msg', status_code=418)
    assert err.status_code == 418
    assert err.message == 'Custom msg'


def test_not_found_error():
    err = NotFoundError('Missing')
    assert err.status_code == 404
    assert err.message == 'Missing'


def test_validation_error():
    err = ValidationError('Bad input')
    assert err.status_code == 400
    assert err.message == 'Bad input'


def test_authentication_error():
    err = AuthenticationError()
    assert err.status_code == 401


def test_conflict_error():
    err = ConflictError('Duplicate')
    assert err.status_code == 409


def test_error_handlers_return_html(client):
    response = client.get('/nonexistent-path')
    assert response.status_code == 404
