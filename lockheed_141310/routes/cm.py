from uuid import UUID
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin

from lockheed_141310.models import db, CMMeta

cm_bp = Blueprint('cm_bp', __name__)


# pylint: disable=inconsistent-return-statements
@cm_bp.route('/', methods=['GET', 'POST'])
@jwt_required
@cross_origin(supports_credentials=True)
def control_modules():
    if request.method == 'GET':
        limit = 20
        offset = 0
        if new_limit := request.args.get('limit'):
            limit = int(new_limit)
        if new_offset := request.args.get('offset'):
            offset = int(new_offset)

        all_modules = CMMeta.query\
            .limit(limit)\
            .offset(offset * limit)\
            .all()

        return jsonify({
            "status": "success",
            "data": [cm.to_dict() for cm in all_modules]
        }), 200
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "content-type must be application/json"
            }), 415

        name = request.json.get("name")

        new_cm = CMMeta.create(name)
        return jsonify({
            "status": "success",
            "data": new_cm
        }), 201


# pylint: disable=inconsistent-return-statements
@cm_bp.route('/name/<cm_name>', methods=['GET', 'DELETE'])
@jwt_required
@cross_origin(supports_credentials=True)
def name_cm_name(cm_name: str):
    if request.method == 'GET':
        requested_cm = CMMeta.query.filter_by(name=cm_name).first()
        if not requested_cm:
            return jsonify({
                "status": "error",
                "message": "control module not found"
            }), 404
        return jsonify({
            "status": "success",
            "data": requested_cm.to_dict()
        }), 200
    if request.method == 'DELETE':
        # :TODO: create a permission for deleting control modules
        requested_cm = CMMeta.query.filter_by(name=cm_name)
        if not requested_cm.first():
            return jsonify({
                "status": "error",
                "message": "control module not found"
            }), 404

        requested_cm.delete()
        db.session.commit()

        return jsonify({"status": "success"}), 200


# pylint: disable=inconsistent-return-statements
@cm_bp.route('/id/<cm_uuid>', methods=['GET', 'DELETE'])
@jwt_required
@cross_origin(supports_credentials=True)
def id_cm_name(cm_uuid: str):
    try:
        cm_uuid = UUID(cm_uuid)
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "not a valid control module id"
        }), 422
    if request.method == 'GET':
        requested_cm = CMMeta.query.filter_by(uuid=cm_uuid).first()
        if not requested_cm:
            return jsonify({
                "status": "error",
                "message": "control module not found"
            }), 404
        return jsonify({
            "status": "success",
            "data": requested_cm.to_dict()
        }), 200
    if request.method == 'DELETE':
        # :TODO: create a permission for deleting control modules
        requested_cm = CMMeta.query.filter_by(uuid=cm_uuid)
        if not requested_cm.first():
            return jsonify({
                "status": "error",
                "message": "control module not found"
            }), 404

        requested_cm.delete()
        db.session.commit()

        return jsonify({"status": "success"}), 200
