from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from lockheed_141310.models import Users, Roles
from lockheed_141310.utils import has_role_by_name

users_bp = Blueprint('users_bp', __name__)


# pylint: disable=inconsistent-return-statements
@users_bp.route('/<username>/roles/<role_id>', methods=['GET', 'POST'])
@jwt_required
def add_user_to_role(username: str, role_id: int):
    if request.method == 'GET':
        user = Users.query.filter_by(username=username).first()
        if user.has_role_name(role_id):
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error"}), 200
    if request.method == 'POST':
        if not has_role_by_name('is_admin'):
            return jsonify({
                "status": "error",
                "message": "missing required permissions"
            }), 403
        current_user_id = Users.query.filter_by(username=get_jwt_identity()).first().id
        Roles.create(current_user_id, role_id)
        return jsonify({
            "status": "success"
        }), 201
