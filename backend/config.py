import os
from datetime import timedelta


class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/eventdb')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'eventdb')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # CORS Configuration
    CORS_ORIGINS = ["*"]  # In production, specify your frontend domains

    # Other configurations
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/eventdb')


class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI = os.getenv('MONGO_URI')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/eventdb_test')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}