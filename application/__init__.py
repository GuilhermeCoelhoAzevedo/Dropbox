from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config
from google.cloud import datastore, storage
from authlib.integrations.flask_client import OAuth

# --- Authlib OAuth Setup ---
def register_google_oauth(app):
    if not app.config['GOOGLE_CLIENT_ID']:
        raise RuntimeError(
            "Missing Google OAuth credentials. Please set GOOGLE_CLIENT_ID in your .flaskenv file."
        )

    if not app.config['GOOGLE_CLIENT_SECRET']:
        raise RuntimeError(
            "Missing Google OAuth credentials. Please set GOOGLE_CLIENT_SECRET in your .flaskenv file."
        )

    if not app.config['GOOGLE_PROJECT_ID']:
        raise RuntimeError(
            "Missing Google OAuth credentials. Please set GOOGLE_PROJECT_ID in your .flaskenv file."
        )

    if not app.config['GOOGLE_PROJECT_STORAGE_BUCKET']:
        raise RuntimeError(
            "Missing Google OAuth credentials. Please set GOOGLE_PROJECT_STORAGE_BUCKET in your .flaskenv file."
        )

    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    return google

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect()
csrf.init_app(app)

google          = register_google_oauth(app)
client          = datastore.Client(project=app.config['GOOGLE_PROJECT_ID'])
storage_client  = storage.Client(project=app.config['GOOGLE_PROJECT_ID'])
bucket          = storage_client.bucket(app.config['GOOGLE_PROJECT_STORAGE_BUCKET'])

from application import routes