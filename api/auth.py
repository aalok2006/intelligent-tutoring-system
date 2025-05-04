from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from ..database import db
from ..models.user import User
from ..services.user_service import UserService # Import user service

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Need to initialize JWTManager in app.py
# jwt = JWTManager(app)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing username, email or password'}), 400

    # Use the service layer for business logic
    user_service = UserService()
    user = user_service.create_user(username, email, password)

    if user:
        # Optional: Trigger initial path generation task here or in user_service
        # personalization_engine.generate_initial_path_task.delay(user.id, diagnostic_results=None) # Need diagnostic results
        return jsonify({'message': 'User created successfully'}), 201
    else:
        # Handle cases like username/email already exists (user_service should handle this)
        return jsonify({'message': 'User already exists or other creation error'}), 400 # Refine error handling

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Example protected route
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200
