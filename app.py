import os
from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

# --- App Initialization ---
app = Flask(__name__, static_folder='static', template_folder='templates')
# Load configuration
app.config.from_object('backend.config.Config')

# --- Extensions Initialization ---
from .database import db, migrate # Import after app config
db.init_app(app) # Initialize SQLAlchemy with the app

# JWT Manager
jwt = JWTManager(app)

# SocketIO - Configure for production with message queue for scalability
# Need to specify cors_allowed_origins="*" or specific origins for frontend
socketio = SocketIO(app,
                    cors_allowed_origins="*", # BE CAREFUL with production, use specific origins
                    message_queue=app.config['CELERY_BROKER_URL'], # Use Redis as message queue
                    manage_session=False # Let Flask handle sessions if needed, or JWT
                   )

# --- Register Blueprints (APIs) ---
from .api.auth import auth_bp
from .api.learning_path import learning_path_bp
# Import and register other blueprints as they are created
# from .api.content import content_bp
# from .api.assessment import assessment_bp
# from .api.chat import chat_bp
# from .api.competitive import competitive_bp

app.register_blueprint(auth_bp)
app.register_blueprint(learning_path_bp)
# app.register_blueprint(content_bp)
# app.register_blueprint(assessment_bp)
# app.register_blueprint(chat_bp)
# app.register_blueprint(competitive_bp)


# --- Register SocketIO Event Handlers ---
# Import the sockets file to register its handlers
from . import sockets # This imports sockets.py and runs its code, registering handlers


# --- Celery Setup ---
from .tasks import celery
# The celery app is initialized in tasks.py, just need to ensure it's imported here.

# --- Routes ---
# Serve the static index.html file as the entry point
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Route to serve other static files (CSS, JS) - Flask does this automatically from static_folder
# @app.route('/<path:filename>')
# def static_files(filename):
#     return send_from_directory(app.static_folder, filename)


# --- Database Migration Command ---
# This allows running flask db init, flask db migrate, flask db upgrade
# from the terminal. Need to define the `flask` command entry point.
# See README instructions later.
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': models.user.User, 'ContentItem': models.content.ContentItem, # etc. import models
            'LearningPath': models.learning_path.LearningPath, 'PathNode': models.learning_path.PathNode}

# --- Running the App (for local development) ---
# Use 'flask run' or a dedicated runner script with gunicorn for production
if __name__ == '__main__':
    # For development, run with Flask's development server and SocketIO
    # For production, use gunicorn running `wsgi.py` and SocketIO needs specific config
    # This runs the web server and the SocketIO server together
    socketio.run(app, debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
