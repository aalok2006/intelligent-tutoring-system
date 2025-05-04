from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .app import app # Import app instance

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Will Import models here so Alembic picks them up
# from .models import user, content, learning_path, chat, interactions, competitive
