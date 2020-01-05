from uuid import UUID
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin

from lockheed_141310.models import CMLog, CMLogTypes, CMMeta
from lockheed_141310.utils import has_permission_by_name

log_bp = Blueprint('log_bp', __name__)


# pylint: disable=inconsistent-return-statements
@log_bp.route('/id/<cm_uuid>', methods=['GET', 'POST'])
@jwt_required
@cross_origin(supports_credentials=True)
def uuid_log(cm_uuid: str):
    """
    :GET: returns the most recent logs for the specified control module. accepts the following url parameters
        - limit: the number of logs that should be returned
        - offset: offset the number of logs that should be returned
        - log_type: the type of log that should be returned
    :POST: inserts log with data into the database
    """
    if request.method == 'GET':
        limit = 20
        offset = 0
        log_type = None
        if limit_arg := request.args.get('limit'):
            limit = int(limit_arg)
        if offset_arg := request.args.get('offset'):
            offset = offset_arg
        if log_type_arg := request.args.get('log_type'):
            log_type = log_type_arg
        if log_type:
            logs = CMLog.query.filter_by(cm_uuid=cm_uuid, log_type=log_type)
        else:
            logs = CMLog.query.filter_by(cm_uuid=cm_uuid)
        logs = logs.order_by(CMLog.timestamp.desc())\
            .limit(limit)\
            .offset(offset*limit)\
            .all()
        return jsonify({
            "status": "success",
            "cm_uuid": cm_uuid,
            "data": [current_log.to_dict() for current_log in logs]
        }), 200
    if request.method == 'POST':
        if not has_permission_by_name("post_log"):
            return jsonify({
                "status": "error",
                "message": "you aren't allowed to do that"
            }), 403
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "content-type must be application/json"
            }), 415
        if not CMMeta.query.filter_by(uuid=cm_uuid).first():
            return jsonify({
                'status': 'error',
                'message': 'invalid control module uuid'
            }), 404

        log_type = request.json.get('log_type')
        data = request.json.get('data')

        if not log_type and data:
            return jsonify({
                "status": "error",
                "message": "missing log_type or data"
            }), 422

        if not CMLogTypes.query.filter_by(cm_uuid=cm_uuid, log_type=log_type).first():
            CMLogTypes.create(cm_uuid, log_type)
        return jsonify(CMLog.create(UUID(cm_uuid), log_type, request.json.get("data"))), 201


@log_bp.route('/name/<cm_name>', methods=['GET', 'POST'])
@jwt_required
@cross_origin(supports_credentials=True)
def name_log(cm_name: str):
    cm_uuid = str(CMMeta.query.filter_by(name=cm_name).first().uuid)
    return uuid_log(cm_uuid)
