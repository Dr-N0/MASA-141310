from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin

from lockheed_141310 import db
from lockheed_141310.models import RoleDefinitions, Roles
from lockheed_141310.utils import has_permission_by_name


role_bp = Blueprint('role_bp', __name__)


# pylint: disable=inconsistent-return-statements
@role_bp.route('/', methods=['GET', 'POST'])
@jwt_required
def roles():
    """
    :GET: gets a list of the available roles
    :POST: creates a new role
    """
    if request.method == 'GET':
        limit = 20
        offset = 0
        if limit_arg := request.args.get('limit'):
            limit = int(limit_arg)
        if offset_arg := request.args.get('offset'):
            offset = offset_arg
        role_definitions = RoleDefinitions.query \
            .limit(limit) \
            .offset(offset * limit) \
            .all()
        return jsonify({
            "status": "success",
            "data": [role_definition.to_dict() for role_definition in role_definitions]
        }), 200
    if request.method == 'POST':
        if not has_permission_by_name("create_role"):
            return jsonify({
                "status": "error",
                "message": "you aren't allowed to do that"
            }), 403

        json = request.json
        name = json.get("name")
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "content-type must be application/json"
            }), 415
        if RoleDefinitions.query.filter_by(name=name).first():
            return jsonify({
                "status": "error",
                "message": "log type already exists"
            }), 409

        get_log = json.get("get_log", False)
        post_log = json.get("post_log", False)
        create_user = json.get("create_user", False)
        delete_user = json.get("delete_user", False)
        create_role = json.get("create_role", False)
        delete_role = json.get("delete_role", False)

        if not name:
            return jsonify({
                "status": "error",
                "message": "missing name parameter"
            }), 422

        new_definition = RoleDefinitions.create(
            name,
            get_log=bool(get_log), post_log=bool(post_log),
            create_user=bool(create_user), delete_user=bool(delete_user),
            create_role=bool(create_role), delete_role=bool(delete_role)
        )

        return jsonify({
            "status": "success",
            "data": new_definition
        }), 200


# pylint: disable=inconsistent-return-statements
@role_bp.route('/name/<name>', methods=['PUT', 'DELETE'])
@jwt_required
@cross_origin(supports_credentials=True)
def role(name):
    """
    :PUT: update a role definition
    :DELETE: deletes the specified role definition
    """
    if request.method == 'PUT':
        if not has_permission_by_name("create_role") and has_permission_by_name("delete_role"):
            return jsonify({
                "status": "error",
                "message": "you aren't allowed to do that"
            }), 403

        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "content-type must be application/json"
            }), 415
        json = request.json

        role_definition = RoleDefinitions.query.filter_by(name=name).first()
        if not role_definition:
            return jsonify({
                "status": "error",
                "message": "role definition doesn't exist"
            }), 404

        # :TODO: this is pretty ridiculous, should write a class method to do this
        if new_get_log := json.get("get_log") is not None:
            role_definition.get_log = new_get_log
        if json.get("post_log") is not None:
            role_definition.post_log = json.get("post_log")
        if json.get("create_user") is not None:
            role_definition.create_user = json.get("create_user")
        if json.get("delete_user") is not None:
            role_definition.delete_user = json.get("delete_user")
        if json.get("create_role") is not None:
            role_definition.create_role = json.get("create_role")
        if json.get("delete_role") is not None:
            role_definition.delete_role = json.get("delete_role")

        db.session.commit()

        return jsonify({
            "status": "success",
            "data": role_definition.to_dict()
        }), 200

    if request.method == 'DELETE':
        if not has_permission_by_name("delete_role"):
            return jsonify({
                "status": "error",
                "message": "you aren't allowed to do that"
            }), 403

        role_definition = RoleDefinitions.query.filter_by(name=name)
        if not role_definition.first():
            return jsonify({
                "status": "error",
                "message": "role definition doesn't exist"
            }), 404

        Roles.query.filter_by(role_id=role_definition.first().id).delete()
        role_definition.delete()
        db.session.commit()

        return jsonify({"status": "success"}), 200
