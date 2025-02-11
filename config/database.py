import os
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DATABASE_PATH = 'auth.db'

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db_connection():
    """Create a database connection"""
    if not os.path.exists(DATABASE_PATH):
        init_db()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = dict_factory
    return conn

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS THONGTINNGUOIDUNG")
        cursor.execute("DROP TABLE IF EXISTS NGUOIDUNG")
        
        # Create NGUOIDUNG table with standardized column names
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS NGUOIDUNG (
            TenDangNhap VARCHAR(50) PRIMARY KEY,
            Email VARCHAR(100) UNIQUE NOT NULL,
            MatKhau VARCHAR(255) NOT NULL,
            Quyen INTEGER NOT NULL DEFAULT 2 CHECK (Quyen IN (0, 1, 2))
        )
        """)
        
        # Create THONGTINNGUOIDUNG table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS THONGTINNGUOIDUNG (
            TenDangNhap VARCHAR(50) PRIMARY KEY,
            HoTen NVARCHAR(100),
            NgaySinh DATE,
            SoDienThoai VARCHAR(15),
            FOREIGN KEY (TenDangNhap) REFERENCES NGUOIDUNG(TenDangNhap)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
        """)

        # Insert default admin account
        cursor.execute("""
        INSERT OR IGNORE INTO NGUOIDUNG (TenDangNhap, Email, MatKhau, Quyen)
        VALUES ('admin', 'admin@example.com', '123456', 0)
        """)

        cursor.execute("""
        INSERT OR IGNORE INTO THONGTINNGUOIDUNG (TenDangNhap, HoTen)
        VALUES ('admin', 'Administrator')
        """)

        conn.commit()
        logger.info("Database initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
