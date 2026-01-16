# app/db/connection.py
#
# Database connection manager for SQLite.
# Provides thread-safe connection pooling and schema initialization.
#

import sqlite3
import os
from pathlib import Path
from typing import Optional
import threading


class DatabaseManager:
    # Singleton database manager for SQLite connections
    
    _instance: Optional['DatabaseManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = self._get_db_path()
            self.schema_path = Path(__file__).parent / "schema.sql"
            self.initialized = False
    
    def _get_db_path(self) -> str:
        # Get database path, create directory if needed
        db_dir = os.getenv("QUOTA_DB_DIR", "./data")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, "quota.db")
    
    def get_connection(self) -> sqlite3.Connection:
        # Get a new database connection
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    
    def initialize_schema(self):
        # Initialize database schema from SQL file
        if self.initialized:
            return
        
        with self._lock:
            if self.initialized:
                return
            
            conn = self.get_connection()
            try:
                with open(self.schema_path, 'r') as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
                self.initialized = True
                print(f"✅ Database initialized at {self.db_path}")
            except Exception as e:
                print(f"❌ Failed to initialize database: {e}")
                raise
            finally:
                conn.close()
    
    def reset_database(self):
        # Reset database (for testing only)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.initialized = False
        self.initialize_schema()


# Global instance
db_manager = DatabaseManager()

