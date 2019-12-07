from flask import Blueprint, request, jsonify

from lockheed_141310 import db
from lockheed_141310.models import RoleDefinitions


role_bp = Blueprint('role_bp', __name__)


# pylint: disable=inconsistent-return-statements
@role_bp.route('/<name>', methods=['GET', 'POST', 'DELETE'])
def role(name):
    if request.method == 'GET':
        requested_role = RoleDefinitions.query.filter_by(name=name).first()
        if requested_role:
            return jsonify({"status": "success",
                            "role": requested_role}), 200
        return jsonify({"status": "error"}), 404
    if request.method == 'POST':
        if RoleDefinitions.query.filter_by(name=name).first():
            return jsonify({"status": "error",
                            "message": "definition already exists"}), 409
        if request.is_json:
            is_owner = request.json.get("is_owner", False)
            is_admin = request.json.get("is_admin", False)
            get_log = request.json.get("get_log", False)
            post_log = request.json.get("post_log", False)
        else:
            is_owner = request.args.get("is_owner", False)
            is_admin = request.args.get("is_admin", False)
            get_log = request.args.get("get_log", False)
            post_log = request.args.get("post_log", False)
        RoleDefinitions.create(name,
                               is_owner=bool(is_owner),
                               is_admin=bool(is_admin),
                               get_log=bool(get_log),
                               post_log=bool(post_log))
        requested_role = RoleDefinitions.query.filter_by(name=name).first()
        return jsonify(requested_role.to_json()), 201
    if request.method == 'DELETE':
        requested_role = RoleDefinitions.query.filter_by(name=name).first()
        if not requested_role:
            return jsonify({"status": "error"}), 404
        db.session.remove(requested_role)
        db.session.commit()
        return jsonify({"status": "success"}), 200
