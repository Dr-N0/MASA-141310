from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from lockheed_141310.models import CMLog, CMLogTypes, db

log_types_bp = Blueprint('log_types', __name__)


# pylint: disable=inconsistent-return-statements
@log_types_bp.route('/<cm_uuid>', methods=['GET', 'POST', 'DELETE'])
@jwt_required
def log_types_route(cm_uuid: str):
    if request.method == 'GET':
        log_types = CMLogTypes.query.filter_by(cm_uuid=cm_uuid).all()
        data = []
        for log_type in log_types:
            data.append({
                "id": log_type.id,
                "log_type": log_type.log_type,
                "description": log_type.description
            })
        return jsonify({
            "status": "success",
            "data": data
        }), 200
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "content-type must be application/json"
            }), 415

        new_log_type = request.json.get('log_type')
        new_description = request.json.get('description')

        if not new_log_type:
            return jsonify({
                "status": "error",
                "message": "missing log_type"
            }), 422

        existing_log_type = CMLogTypes.query.filter_by(cm_uuid=cm_uuid, log_type=new_log_type).first()
        if existing_log_type:
            existing_log_type.description = new_description
            db.session.commit()
            return jsonify({
                "status": "success",
                "data": existing_log_type.to_dict()
            }), 200

        return jsonify({
            "status": "success",
            "data": CMLogTypes.create(cm_uuid, new_log_type, new_description)
        }), 201


# pylint: disable=inconsistent-return-statements
@log_types_bp.route('/<cm_uuid>/<log_type>', methods=['GET', 'DELETE'])
@jwt_required
def single_log_type(cm_uuid: str, log_type: str):
    if request.method == 'GET':
        if requested_type := CMLogTypes.query.filter_by(cm_uuid=cm_uuid, log_type=log_type).first():
            return jsonify({
                "status": "success",
                "data": requested_type.to_dict()
            }), 200
        return jsonify({
            "status": "error",
            "message": "nonexistent log type"
        }), 404
    if request.method == 'DELETE':
        requested_type = CMLogTypes.query.filter_by(cm_uuid=cm_uuid, log_type=log_type)
        if requested_type.first():
            if CMLog.query.filter_by(cm_uuid=cm_uuid, log_type=log_type).all():
                return jsonify({
                    "status": "error",
                    "message": "there are logs associated with this log type"
                }), 409
            requested_type.delete()
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "log type deleted"
            }), 200
        return jsonify({
            "status": "error",
            "message": "nonexistent log type"
        }), 404
