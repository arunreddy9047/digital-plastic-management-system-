import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'eplastic-secret-key-12345'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///e_plastic.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
