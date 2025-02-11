import os
from dotenv import load_dotenv
from flask import Flask, send_from_directory, render_template, redirect, session
from flask_cors import CORS
from config.database import init_db
from routes.auth import auth
from functools import wraps

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    
    # Enable CORS
    CORS(app)
    
    # Set up session configuration
    app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
    
    # Configure Google OAuth
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only
    
    # Initialize database
    init_db()
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/api')
    # Dashboard routes
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
        
    @app.route('/admin')
    def admin_dashboard():
        return render_template('dashboard.html')
        
    @app.route('/staff')
    def staff_dashboard():
        return render_template('dashboard.html')

    # Root route redirects to login
    @app.route('/')
    def root():
        return render_template('login.html')
        
    # Login page
    @app.route('/login')
    def login():
        return render_template('login.html')
        
    # Signup page
    @app.route('/signup')
    def signup():
        return render_template('signup.html')
    
    # Error handlers
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Internal server error'}, 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Run the app
    app.run(host='127.0.0.1', port=5000, debug=True)