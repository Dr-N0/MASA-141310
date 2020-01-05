from functools import wraps
from flask_jwt_extended import get_jwt_claims, get_jwt_identity
from flask import jsonify
from argon2.exceptions import VerifyMismatchError

from lockheed_141310 import jwt, ph, blacklist
from lockheed_141310.models import Users, Roles, RoleDefinitions


def authenticate(username: str, password: str):
    user = Users.query.filter_by(username=username).first()
    if not user:
        return False
    try:
        return ph.verify(user.password, password)
    except VerifyMismatchError:
        return False


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


def has_role_by_name(required_role: str) -> bool:
    """
    Determines if the current user has the required role, described by a string
    """
    if claims := get_jwt_claims():
        if required_role in claims['roles']:
            return True
    if identity := get_jwt_identity():
        current_user = Users.query.filter_by(username=identity).first()
        return bool(current_user.is_owner)
    return False


def has_permission_by_name(permission: str) -> bool:
    """
    Determines if the current user has the specified permission defined in their roles
    :param permission: name of desired permission
    :return: true if the user has the permission, false otherwise
    """
    if claims := get_jwt_claims():
        roles = claims['roles']
        for role_name in roles:
            role_definition = RoleDefinitions.query.filter_by(name=role_name).first()
            if role_definition.has_permission(permission):
                return True
    if identity := get_jwt_identity():
        current_user = Users.query.filter_by(username=identity).first()
        return bool(current_user.is_owner)
    return False
