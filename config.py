import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar' # ¡Cambia esto en producción!
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///polleria.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False