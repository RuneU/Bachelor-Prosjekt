import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, url_for
from app import app # Replace with your actual app import
from blueprints.admin_reg.routes import handle_form

# Fixture to set up the Flask test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test form validation
def test_handle_form_missing_required_fields(client, mocker):
    mock_conn = mocker.patch('sql.db_connection.connection_def')
    response = client.post('/blueprints/admin_reg/handle_form', data={})
    assert response.status_code == 400
    assert b"Lokasjon and Status are required fields" in response.data

# Test successful insert logic
def test_handle_form_insert_success(client, mocker):
    mock_conn = MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchval.side_effect = [1, 0]  # Mock KriseID and EvakuertID

    data = {
        'lokasjon': 'Test Location',
        'status': 'Active',
        'krise_type': 'Type',
        'krise_navn': 'Name',
        'annen_info': 'Info',
        'evak_fnavn': 'Fornavn',
        'evak_mnavn': 'Mellomnavn',
        'evak_enavn': 'Etternavn',
        'evak_tlf': '12345678',
        'evak_adresse': 'Address',
        'kon_fnavn': 'KonFornavn',
        'kon_mnavn': 'KonMellomnavn',
        'kon_enavn': 'KonEtternavn',
        'kon_tlf': '87654321',
    }
    response = client.post('/handle_form', data=data)
    assert response.status_code == 302  # Redirect to index
    mock_conn.commit.assert_called_once()

# Test successful update logic
def test_handle_form_update_success(client, mocker):
    mock_conn = MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value

    data = {
        'evakuert_id': '1',
        'krise_id': '1',
        'kontakt_person_id': '1',
        'status_id': '1',
        'lokasjon': 'Updated Location',
        'status': 'Inactive',
        'krise_type': 'Updated Type',
        'krise_navn': 'Updated Name',
        'annen_info': 'Updated Info',
        'evak_fnavn': 'Updated Fornavn',
        'evak_mnavn': 'Updated Mellomnavn',
        'evak_enavn': 'Updated Etternavn',
        'evak_tlf': '87654321',
        'evak_adresse': 'Updated Address',
        'kon_fnavn': 'Updated KonFornavn',
        'kon_mnavn': 'Updated KonMellomnavn',
        'kon_enavn': 'Updated KonEtternavn',
        'kon_tlf': '12345678',
    }
    response = client.post('/handle_form', data=data)
    assert response.status_code == 302
    mock_conn.commit.assert_called_once()

# Test database error handling
def test_handle_form_database_error(client, mocker):
    mock_conn = MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = Exception("DB Error")

    data = {
        'lokasjon': 'Test',
        'status': 'Active',
        'krise_type': 'Type',
        'krise_navn': 'Name',
        'annen_info': 'Info',
        'evak_fnavn': 'Fornavn',
        'evak_mnavn': 'Mellomnavn',
        'evak_enavn': 'Etternavn',
        'evak_tlf': '12345678',
        'evak_adresse': 'Address',
        'kon_fnavn': 'KonFornavn',
        'kon_mnavn': 'KonMellomnavn',
        'kon_enavn': 'KonEtternavn',
        'kon_tlf': '87654321',
    }
    response = client.post('/handle_form', data=data)
    assert response.status_code == 500
    mock_conn.rollback.assert_called_once()

# Test invalid integer input
def test_handle_form_invalid_integer(client, mocker):
    mock_conn = MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value

    data = {
        'lokasjon': 'Test',
        'status': 'Active',
        'evak_tlf': 'invalid',
        'krise_type': 'Type',
        'krise_navn': 'Name',
        'annen_info': 'Info',
        'evak_fnavn': 'Fornavn',
        'evak_mnavn': 'Mellomnavn',
        'evak_enavn': 'Etternavn',
        'evak_adresse': 'Address',
        'kon_fnavn': 'KonFornavn',
        'kon_mnavn': 'KonMellomnavn',
        'kon_enavn': 'KonEtternavn',
        'kon_tlf': '87654321',
    }
    response = client.post('/handle_form', data=data)
    assert response.status_code == 302  # Assuming DB allows NULL for invalid integers
    mock_conn.commit.assert_called_once()

# Test GET request with valid evakuert_id
def test_adminreg_with_id_valid(client, mocker):
    mock_conn = MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = [
        1, 1, 1, 1, 'Ola', 'None', 'Nordmann',
        '12345678', 'Storgata 1, Oslo', 'Anne', 'None',
        'Larsen', '22334455', 'Brann', 'Bybrann i Oslo', 'Oslo',
        'Noe har skjedd', 'Velg Status'
    ]

    response = client.get('/1')
    assert response.status_code == 200
    assert b"admin-reg.html" in response.data

# Test GET request with invalid evakuert_id
def test_adminreg_with_id_not_found(client, mocker):
    mock_conn = MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None

    response = client.get('/999')
    assert response.status_code == 404