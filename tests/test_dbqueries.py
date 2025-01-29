import os
import sys
import unittest
import pyodbc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.db_connection import connection_string

class TestDatabaseQueries(unittest.TestCase):
    def setUp(self):
        # Connect to the database
        self.conn = pyodbc.connect(
            connection_string
        )
        self.cursor = self.conn.cursor()

    def tearDown(self):
        # Clean up and close the connection
        self.cursor.close()
        self.conn.close()

    def test_insert_and_delete_evakuerte(self):
        # Test data for insertion
        test_data = {
            'Fornavn': 'Test',
            'Etternavn': 'User',
            'Telefonnummer': 12345678,
            'Adresse': 'Test Address',
            'KriseID': None  # Use a valid KriseID if required by your schema
        }

        # --- INSERT TEST ---
        # Insert the test record into Evakuerte
        insert_query = """
            INSERT INTO Evakuerte (Fornavn, Etternavn, Telefonnummer, Adresse, KriseID)
            VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(insert_query, 
                            test_data['Fornavn'], 
                            test_data['Etternavn'], 
                            test_data['Telefonnummer'], 
                            test_data['Adresse'], 
                            test_data['KriseID'])
        self.conn.commit()

        # Check if the insert was successful by querying the table
        self.cursor.execute("SELECT * FROM Evakuerte WHERE Fornavn = ? AND Etternavn = ?", 
                            test_data['Fornavn'], test_data['Etternavn'])
        result = self.cursor.fetchone()
        print(f"Inserted record: {result}")  # Debug output

        # Get the EvakuertID directly from the result
        if result:
            evakuert_id = result[0]  # Assuming EvakuertID is the first column in the result
            self.assertIsNotNone(evakuert_id, "Failed to insert record")
        else:
            self.fail("Failed to insert record into database")

        # --- DELETE TEST ---
        # Delete the test record
        delete_query = "DELETE FROM Evakuerte WHERE EvakuertID = ?"
        self.cursor.execute(delete_query, evakuert_id)
        self.conn.commit()

        # Verify the record is deleted
        self.cursor.execute("SELECT * FROM Evakuerte WHERE EvakuertID = ?", evakuert_id)
        result = self.cursor.fetchone()
        self.assertIsNone(result, "Record was not deleted")


if __name__ == '__main__':
    unittest.main()
