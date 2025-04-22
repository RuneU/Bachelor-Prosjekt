# common_imports.py

import os
import sys
import cv2
import json
import base64
import time
import logging
import requests
import numpy as np
import pyodbc
import mysql.connector
import face_recognition as face
from io import BytesIO
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Flask imports
from flask import (
    Flask, Response, request, render_template,
    jsonify, redirect, url_for, session,
    send_from_directory, send_file
)

# Custom modules and project-specific paths
sys.dont_write_bytecode = True
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))

from sql.db_connection import connection_string
from translations import translations
from rfid_module import (
    RFIDregister, scan_rfid, scan_rfid_with_history,
    get_evakuert_id_by_chipid
)
from pyfingerprint.pyfingerprint import PyFingerprint
