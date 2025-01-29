import os
import sys
import unittest
import pyodbc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.db_connection import connection_string

class TestAzureMySQLConnection(unittest.TestCase):
    def test_database_connection(self):
        conn = None
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1, "Query should return 1")
        except pyodbc.Error as e:
            self.fail(f"Failed to connect or execute query: {e}")
        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
    unittest.main()