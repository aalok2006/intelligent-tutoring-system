# Example Service File
from ..database import db
from ..models.user import User

class UserService:
    def create_user(self, username, email, password):
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            # Potentially return None or raise a specific exception
            return None

        new_user = User(username=username, email=email)
        new_user.set_password(password) # Hash the password

        db.session.add(new_user)
        db.session.commit()

        # In a real scenario, trigger diagnostic assessment flow here (Phase 1 Workflow 4.1)
        # This might involve creating a DiagnosticAssessment record for the user
        # And queuing a task for initial path generation *after* assessment completion.
        # from .assessment_service import AssessmentService
        # AssessmentService().assign_diagnostic(new_user.id)

        return new_user

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_user_by_username(self, username):
         return User.query.filter_by(username=username).first()

    # Add other user-related methods (update profile, set goals, etc.)
