import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aegisguard-super-secret-key-2026')
    # Place your serviceAccountKey.json in the root folder or set path below
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', 'serviceAccountKey.json')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DB_URL', 'https://your-firebase-project.firebaseio.com/')