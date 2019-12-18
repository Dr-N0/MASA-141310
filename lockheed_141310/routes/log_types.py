from uuid import UUID
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from lockheed_141310.models import CMLogTypes, db

log_types_bp = Blueprint('log_types', __name__)


# pylint: disable=inconsistent-return-statements
@log_types_bp.route('/<cm_uuid>', methods=['GET', 'POST'])
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
        log_type = None
        description = None

        if request.is_json:
            if new_log_type := request.json.get('log_type'):
                log_type = new_log_type
            else:
                return jsonify({
                    "status": "error",
                    "message": "missing log type"
                }), 422
            if new_description := request.json.get('description'):
                description = new_description
        else:
            return jsonify({
                "status": "error",
                "message": "missing data"
            }), 422

        existing_log_type = CMLogTypes.query.filter_by(cm_uuid=cm_uuid, log_type=log_type).first()
        if existing_log_type:
            existing_log_type.description = description
            db.session.commit()
            return jsonify({
                "status": "success",
                "data": existing_log_type.to_dict()
            }), 200
        return jsonify({
            "status": "success",
            "data": CMLogTypes.create(UUID(cm_uuid), log_type, description)
        }), 201
