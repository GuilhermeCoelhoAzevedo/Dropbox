import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\x07;\x8ck\xdd`\xe8u\xb3\xa5i2\xdel\xca\xee\xcd\xa2\xcc\xb5(6&\xde'
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "E:\\Griffith\\CPA\\dropbox-309912-1595a846859a.json"
    