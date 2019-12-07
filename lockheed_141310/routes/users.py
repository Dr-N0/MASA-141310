from flask import Blueprint, jsonify, request

from lockheed_141310.models import Users

users_bp = Blueprint('users_bp', __name__)


# pylint: disable=inconsistent-return-statements
@users_bp.route('/<username>/roles/<role_name>', methods=['GET', 'POST'])
def add_user_to_role(username: str, role_name: str):
    if request.method == 'GET':
        user = Users.query.filter_by(username=username).first()
        if user.has_role(role_name):
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error"}), 200
