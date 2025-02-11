from config.database import get_db_connection
import bcrypt
import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self, id=None, name=None, email=None, password=None, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.created_at = created_at

    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt)
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise Exception("Error securing password")

    @staticmethod
    def check_password(password, hashed):
        """Verify a password against a hash"""
        try:
            if isinstance(password, str):
                password = password.encode('utf-8')
            if isinstance(hashed, str):
                hashed = hashed.encode('utf-8')
            return bcrypt.checkpw(password, hashed)
        except Exception as e:
            logger.error(f"Error checking password: {str(e)}")
            return False

    @staticmethod
    def find_by_email(email):
        """Find a user by email"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.*, t.HoTen 
                FROM NGUOIDUNG n 
                LEFT JOIN THONGTINNGUOIDUNG t ON n.TenDangNhap = t.TenDangNhap 
                WHERE n.Email = ?
            """, (email,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Database error in find_by_email: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def find_by_username(username):
        """Find a user by username"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.*, t.HoTen 
                FROM NGUOIDUNG n 
                LEFT JOIN THONGTINNGUOIDUNG t ON n.TenDangNhap = t.TenDangNhap 
                WHERE n.TenDangNhap = ?
            """, (username,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Database error in find_by_username: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def create(user_data):
        """Create a new user"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert into NGUOIDUNG table
            cursor.execute("""
                INSERT INTO NGUOIDUNG (TenDangNhap, Email, MatKhau, Quyen)
                VALUES (?, ?, ?, ?)
            """, (user_data['TenDangNhap'], user_data['Email'], 
                  user_data['MatKhau'], user_data.get('Quyen', 2)))
            
            # Insert into THONGTINNGUOIDUNG table
            cursor.execute("""
                INSERT INTO THONGTINNGUOIDUNG (TenDangNhap, HoTen)
                VALUES (?, ?)
            """, (user_data['TenDangNhap'], user_data.get('HoTen', '')))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error in create: {str(e)}")
            raise Exception("Error creating user")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def username_exists(username):
        """Check if username exists"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM NGUOIDUNG WHERE TenDangNhap = ?", (username,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Database error in username_exists: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def email_exists(email):
        """Check if email exists"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM NGUOIDUNG WHERE Email = ?", (email,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Database error in email_exists: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_remember_token(username, token, expires_at):
        """Update or create remember me token for user"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First, try to create the table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS REMEMBER_TOKENS (
                    TenDangNhap TEXT PRIMARY KEY,
                    Token TEXT NOT NULL,
                    ExpiresAt DATETIME NOT NULL,
                    FOREIGN KEY (TenDangNhap) REFERENCES NGUOIDUNG(TenDangNhap)
                )
            """)
            
            # Then, insert or replace the token
            cursor.execute("""
                INSERT OR REPLACE INTO REMEMBER_TOKENS (TenDangNhap, Token, ExpiresAt)
                VALUES (?, ?, ?)
            """, (username, token, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error in update_remember_token: {str(e)}")
            raise Exception("Error updating remember token")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def verify_remember_token(username, token):
        """Verify a remember me token"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ExpiresAt FROM REMEMBER_TOKENS
                WHERE TenDangNhap = ? AND Token = ?
                AND datetime(ExpiresAt) > datetime('now')
            """, (username, token))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Database error in verify_remember_token: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def clear_remember_token(username):
        """Clear remember me token for user"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM REMEMBER_TOKENS WHERE TenDangNhap = ?", (username,))
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error in clear_remember_token: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()