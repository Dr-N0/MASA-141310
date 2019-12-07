from functools import wraps
from flask_jwt_extended import get_jwt_claims
from flask import jsonify

from lockheed_141310 import jwt, ph, blacklist
from lockheed_141310.models import Users, Roles, RoleDefinitions


def authenticate(username: str, password: str):
    user = Users.query.filter_by(username=username).first()
    if not user:
        return False
    return ph.verify(user.password, password)


@jwt.user_claims_loader
def add_claims_to_access_token(user: Users):
    roles = [role.get_name() for role in Roles.query.filter_by(user_id=user.id).all()]
    return {'roles': roles}


@jwt.user_identity_loader
def user_identity_lookup(user: Users):
    return user.username


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


def requires_permissions(required_permission):
    def requires(func):
        @wraps(func)
        def wrapper():
            role_names = get_jwt_claims()['roles']
            for role_name in role_names:
                role = RoleDefinitions.query.filter_by(name=role_name).first()
                if role.has_permission(required_permission):
                    return func()
            return jsonify({
                "status": "error",
                "message": "missing permissions"
            }), 403
        return wrapper
    return requires
