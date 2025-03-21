import os
from dotenv import load_dotenv


load_dotenv()
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not AZURE_CONNECTION_STRING:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set or is empty!")

print("Azure Connection String:", AZURE_CONNECTION_STRING)
