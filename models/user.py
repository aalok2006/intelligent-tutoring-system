from ..database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    profile_data = db.Column(db.JSONB, default={}) # Store JSON for flexibility
    pseudonym = db.Column(db.String(80), nullable=True)

    # Relationships (define in respective model files and link back)
    # goals = db.relationship('LearningGoal', backref='user', lazy='dynamic')
    # learning_paths = db.relationship('LearningPath', backref='user', lazy='dynamic')
    # interactions = db.relationship('UserInteraction', backref='user', lazy='dynamic')
    # chat_messages = db.relationship('ChatMessage', backref='sender', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_profile_data(self, data):
         # Simple validation/update
         if isinstance(data, dict):
             current_data = self.profile_data if self.profile_data is not None else {}
             current_data.update(data)
             self.profile_data = current_data
             return True
         return False # Or raise error

    # Add other models (content, assessment, learning_path, path_node, etc.) similarly
    # Example placeholder for content.py
    # class ContentItem(db.Model):
    #     __tablename__ = 'content_items'
    #     id = db.Column(db.Integer, primary_key=True)
    #     type = db.Column(db.String(50), nullable=False)
    #     title = db.Column(db.String(200), nullable=False)
    #     content_data = db.Column(db.JSONB, default={})
    #     metadata = db.Column(db.JSONB, default={})
    #     # Add relationships
