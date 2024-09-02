import os
from secret import config

class Config:
    SECRET_KEY = config.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = config.get('DATABASE_URL', 'sqlite:///quiz.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Solana API configuration
    SOLANA_URL = config.get('SOLANA_URL', 'https://api.mainnet-beta.solana.com')
    SOLANA_PRIVATE_KEY = config.get('SOLANA_PRIVATE_KEY')
