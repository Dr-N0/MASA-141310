from os import environ, path, getcwd

APP_NAME = environ.get('141310_APP_NAME', 'lockheed_141310')
DEBUG = environ.get('141310_DEBUG', False)
IP = environ.get('141310_IP', '0.0.0.0')
PORT = environ.get('141310_PORT', 8080)

JWT_SECRET_KEY = environ.get('141310_JWT_SECRET_KEY', 'ligma42069;sugma')
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_CSRF_PROTECT = False  # temporary

JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:////{}'.format(path.join(getcwd(), 'data.db')))
