from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
from models.user import User
import bcrypt
import logging
import secrets
import datetime
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import os
import json
import pathlib

# Google OAuth config
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/callback/google')

# OAuth flow configuration
client_config = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [GOOGLE_REDIRECT_URI]
    }
}

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Get user input
        username = data.get('TenDangNhap', '')
        email = data.get('Email', '')
        password = data.get('MatKhau', '')

        if not password:
            return jsonify({'error': 'Mật khẩu không được để trống'}), 400

        # Find user by username or email
        user = None
        if email:
            user = User.find_by_email(email)
        elif username:
            user = User.find_by_username(username)

        if not user:
            return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401

        # Verify password
        if not User.check_password(password, user['MatKhau']):
            return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401

        # Generate remember me token if requested
        remember_me = data.get('remember_me', False)
        remember_token = None
        
        if remember_me:
            # Generate a secure token
            remember_token = secrets.token_urlsafe(32)
            expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
            
            # Store token in user record
            User.update_remember_token(user['TenDangNhap'], remember_token, expires_at)

        response_data = {
            'success': True,
            'TenDangNhap': user['TenDangNhap'],
            'Quyen': user['Quyen'],
            'HoTen': user.get('HoTen', ''),
        }

        if remember_token:
            response_data['remember_token'] = remember_token

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi. Vui lòng thử lại sau.'}), 500

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in ['TenDangNhap', 'Email', 'MatKhau']):
            return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400

        # Check if username exists
        if User.username_exists(data['TenDangNhap']):
            return jsonify({'error': 'Tên đăng nhập đã tồn tại'}), 400

        # Check if email exists
        if User.email_exists(data['Email']):
            return jsonify({'error': 'Email đã được sử dụng'}), 400

        # Hash password
        hashed_password = User.hash_password(data['MatKhau'])

        # Create new user
        user_data = {
            'TenDangNhap': data['TenDangNhap'],
            'Email': data['Email'],
            'MatKhau': hashed_password,
            'Quyen': 2  # Default role for new users
        }

        User.create(user_data)
        
        return jsonify({
            'success': True,
            'message': 'Đăng ký thành công'
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi. Vui lòng thử lại sau.'}), 500

@auth.route('/check-email', methods=['POST'])
def check_email():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        exists = User.email_exists(email)
        return jsonify({'exists': exists})

    except Exception as e:
        logger.error(f"Email check error: {str(e)}")
        return jsonify({'error': 'Email check failed'}), 500

@auth.route('/login/google')
def google_login():
    try:
        # Create the flow using the client secrets
        flow = Flow.from_client_config(
            client_config,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']
        )
        
        # Set the redirect URI
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Generate URL for request to Google's OAuth 2.0 server
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store the state in the session
        session['state'] = state
        
        # Redirect to Google's OAuth 2.0 server
        return jsonify({'redirect_url': authorization_url})
        
    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        return jsonify({'error': 'Failed to initialize Google login'}), 500

@auth.route('/callback/google')
def google_callback():
    try:
        # Create flow from client secrets
        flow = Flow.from_client_config(
            client_config,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'],
            state=session.get('state', None)
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Use the authorization server's response to fetch the OAuth 2.0 tokens
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        
        # Get credentials from flow
        credentials = flow.credentials
        
        # Get user info from Google
        request_session = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, request_session, GOOGLE_CLIENT_ID
        )
        
        # Extract user information
        email = id_info.get('email')
        name = id_info.get('name', '')
        
        # Check if user exists
        user = User.find_by_email(email)
        
        if not user:
            # Create new user
            user_data = {
                'TenDangNhap': email.split('@')[0],  # Use part before @ as username
                'Email': email,
                'MatKhau': bcrypt.hashpw(secrets.token_urlsafe(32).encode(), bcrypt.gensalt()),  # Random secure password
                'HoTen': name,
                'Quyen': 2  # Default role for Google-authenticated users
            }
            User.create(user_data)
            user = User.find_by_email(email)
        
        # Generate response data
        response_data = {
            'success': True,
            'TenDangNhap': user['TenDangNhap'],
            'Quyen': user['Quyen'],
            'HoTen': user.get('HoTen', ''),
        }
        
        # Redirect to appropriate dashboard with user data
        redirect_path = '/dashboard'
        if user['Quyen'] == 0:
            redirect_path = '/admin'
        elif user['Quyen'] == 1:
            redirect_path = '/staff'
            
        return redirect(f"{redirect_path}?data={json.dumps(response_data)}")
        
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        return redirect('/login?error=google_auth_failed')

@auth.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@auth.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500