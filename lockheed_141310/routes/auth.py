from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, \
    jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims, get_raw_jwt

from lockheed_141310 import blacklist
from lockheed_141310.utils import authenticate
from lockheed_141310.models import Users

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"status": "error",
                        "message": "missing json in request"}), 422
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"status": "error",
                        "message": "missing username parameter"}), 422
    if not password:
        return jsonify({"status": "error",
                        "message": "missing password parameter"}), 422
    if not authenticate(username, password):
        return jsonify({"status": "error",
                        "message": "invalid credentials"}), 422
    user = Users.query.filter_by(username=username).first()
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)

    resp = jsonify({"status": "success"})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    return resp, 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_username = get_jwt_identity()
    current_user = Users.query.filter_by(username=current_username).first()
    access_token = create_access_token(identity=current_user)

    resp = jsonify({"status": "success"})
    set_access_cookies(resp, access_token)
    return resp, 200


@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    print(blacklist)
    return jsonify({"status": "success",
                    "message": "token successfully revoked"}), 200


@auth_bp.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({
        'identity': get_jwt_identity(),
        'roles': get_jwt_claims()['roles']
    }), 200
