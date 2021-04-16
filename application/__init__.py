from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config
from google.cloud import datastore, storage
import local_constants

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect()
csrf.init_app(app)

client          = datastore.Client()
storage_client  = storage.Client(project=local_constants.PROJECT_NAME)
bucket          = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)

from application import routes