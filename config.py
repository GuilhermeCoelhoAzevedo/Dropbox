import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    PROJECT_NAME = os.environ.get("PROJECT_NAME")
    PROJECT_STORAGE_BUCKET = os.environ.get("PROJECT_STORAGE_BUCKET")