import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file in local dev

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_fallback' # IMPORTANT: Change this!
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/ai_platform_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    # AI Tutor Configuration
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://api.openai.com/v1') # Or other LLM endpoint
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo') # Or other model
