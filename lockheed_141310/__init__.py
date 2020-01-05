from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from argon2 import PasswordHasher

import config

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(config)
db = SQLAlchemy(app)
jwt = JWTManager(app)
ph = PasswordHasher()
blacklist = set()  # TODO: make this a tabley boi

# pylint: disable=wrong-import-position
from lockheed_141310.routes import log_bp, auth_bp, role_bp, users_bp, log_types_bp, cm_bp
# pylint: enable=wrong-import-position

app.register_blueprint(log_bp, url_prefix='/logs')
app.register_blueprint(log_types_bp, url_prefix='/log_types')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(role_bp, url_prefix='/roles')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(cm_bp, url_prefix='/cm')
