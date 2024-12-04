import sqlite3
from sqlite3 import Error
import os
from . import init_db

# Get the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'devices.db')

def get_db():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

if not os.path.exists(DB_PATH):
    init_db()