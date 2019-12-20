from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from lockheed_141310 import ph
from lockheed_141310.models import db, Users, Roles
from lockheed_141310.utils import has_role_by_name

users_bp = Blueprint('users_bp', __name__)


# pylint: disable=inconsistent-return-statements
@users_bp.route('/username/<username>', methods=['GET', 'DELETE'])
@jwt_required
def username_route(username: str):
    if request.method == 'GET':
        if user := Users.query.filter_by(username=username).first():
            return jsonify({
                "status": "success",
                "data": user.to_dict()
            }), 200
        return jsonify({
            "status": "error",
            "message": "user doesn't exist"
        }), 404
    if request.method == 'DELETE':
        if not has_role_by_name('owner'):
            return jsonify({
                "status": "error",
                "message": "only the owner can delete users"
            }), 403
        user = Users.query.filter_by(username=username)
        if user.first():
            user.delete()
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "user successfully deleted"
            }), 200
        return jsonify({
            "status": "error",
            "message": "user doesn't exist"
        }), 404


@users_bp.route('/', methods=['GET', 'POST'])
@jwt_required
def users_route():
    if request.method == 'GET':
        limit = 20
        offset = 0
        if limit_arg := request.args.get('limit'):
            limit = limit_arg
        if offset_arg := request.args.get('offset'):
            offset = offset_arg
        users = Users.query \
            .limit(limit) \
            .offset(offset * limit) \
            .all()
        returnval = dict()
        returnval['status'] = 'success'
        returnval['data'] = []
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "roles": user.roles()
            }
            returnval['data'].append(user_data)

        return jsonify(returnval), 200
    if request.method == 'POST':
        if not has_role_by_name('is_admin'):
            return jsonify({
                "status": "error",
                "message": "only admins can create users"
            }), 403
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "content-type must be application/json"
            }), 415
        username = request.json.get('username')
        password = request.json.get('password')

        if not username and password:
            return jsonify({
                "status": "error",
                "message": "missing username or password"
            }), 422

        new_user = Users.create(username, ph.hash(password))
        new_user['status'] = 'success'
        return jsonify(new_user), 201


# pylint: disable=inconsistent-return-statements
@users_bp.route('/username/<username>/roles', methods=['GET', 'POST'])
@jwt_required
def all_roles_route(username: str):
    if request.method == 'GET':
        target_user = Users.query.filter_by(username=username).first()
        if target_user:
            return jsonify({
                "status": "success",
                "data": target_user.roles()
            }), 200
        return jsonify({
            "status": "error",
            "message": "user doesn't exist"
        }), 404
    if request.method == 'POST':
        if not has_role_by_name('is_admin'):
            return jsonify({
                "status": "error",
                "message": "missing required permissions"
            }), 403
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "content-type must be application/json"
            }), 415
        role_id = request.json.get('role_id')
        if not role_id:
            return jsonify({
                "status": "error",
                "message": "missing role_id"
            }), 422
        target_user = Users.query.filter_by(username=get_jwt_identity()).first()
        Roles.create(target_user.id, role_id)
        return jsonify({
            "status": "success",
            "data": target_user.to_dict()
        }), 201


# pylint: disable=inconsistent-return-statements
@users_bp.route('/username/<username>/roles/<role_id>', methods=['POST'])
@jwt_required
def add_user_to_role(username: str, role_id: str):
    if request.method == 'POST':
        if not has_role_by_name('is_admin'):
            return jsonify({
                "status": "error",
                "message": "missing required permissions"
            }), 403
        current_user = Users.query.filter_by(username=username).first()
        if not current_user:
            return jsonify({
                "status": "error",
                "message": "user doesn't exist"
            }), 404
        Roles.create(current_user.id, int(role_id))
        return jsonify({
            "status": "success",
            "data": current_user.to_dict
        }), 201
