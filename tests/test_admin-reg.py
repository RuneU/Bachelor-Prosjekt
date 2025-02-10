import os
import sys
import unittest
import pyodbc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.db_connection import connection_string


def test_handle_form_missing_required_fields(client, mocker):
    moc_conn = mocker.patch('sql.db_connection.connection_def')
    response = client.post('/handle_form', data={})
    assert response.status_code == 400
    assert b"Lokasjon and Status are required fields" in response.data


def test_handle_form_insert_success(client, mocker):
    mock_conn = mocker.MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchval.side_effect = [1, 0]  # Mock KriseID and EvakuertID

    data = {
        'lokasjon': 'Test Location',
        'status': 'Active',
        # Include other required form fields...
    }
    response = client.post('/handle_form', data=data)
    assert response.status_code == 302  # Redirect to index
    mock_conn.commit.assert_called_once()

def test_handle_form_update_success(client, mocker):
    mock_conn = mocker.MagicMock()
    mocker.patch('sql.db_connection.connection_def', return_value=mock_conn)
    mock_cursor = mock_conn.cursor.return_value

    data = {
        'evakuert_id': '1',
        'lokasjon': 'Updated Location',
        'status': 'Inactive',
        # Include other form fields...
    }
    response = client.post('/handle_form', data=data)
    assert response.status_code == 302
    mock_conn.commit.assert_called_once()