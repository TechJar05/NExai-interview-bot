from flask import Flask, render_template, session
from flask_session import Session
import os
import logging
from logging.handlers import RotatingFileHandler

# Import Blueprints
from routes import register_routes

from utils.helpers import init_interview_data

# Initialize the Flask application
def create_app():
    app = Flask(__name__)

    # Secret key for session handling
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # Session config
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_NAME'] = 'session'
    session_dir = os.path.join(os.getcwd(), 'flask_session_data')
    os.makedirs(session_dir, exist_ok=True)
    app.config['SESSION_FILE_DIR'] = session_dir

    # Initialize session
    Session(app)

    # Logging configuration
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, 'interview_app.log')
    handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Avoid duplicate handlers
    if not app.logger.handlers:
        app.logger.addHandler(handler)

    app.logger.setLevel(logging.DEBUG)

    # Register Blueprints
    # Register all routes using centralized function
    register_routes(app)

    # Root Route
    @app.route('/')
    def home():
        app.logger.info("Home page accessed")
        session.clear()
        session['interview_data'] = init_interview_data()

        data = {
            "user_name": "Guest",
            "email": "",
            "match_score": "",
            "jd_text": "",
            "resume_text": ""
        }

        return render_template('index.html', data=data)

    # Custom 404 Error
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
