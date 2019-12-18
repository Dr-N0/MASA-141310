from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.dialects.postgresql import UUID

from lockheed_141310.models import CMLog, CMLogTypes, CMMeta

log_bp = Blueprint('log_bp', __name__)


# pylint: disable=inconsistent-return-statements
@log_bp.route('/<cm_uuid>', methods=['GET', 'POST'])
@jwt_required
def log(cm_uuid: UUID):
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
        log_type = "%"
        if limit_arg := request.args.get('limit'):
            limit = limit_arg
        if offset_arg := request.args.get('offset'):
            offset = offset_arg
        if log_type_arg := request.args.get('log_type'):
            log_type = log_type_arg
        logs = CMLog.query.filter_by(cm_uuid=cm_uuid, log_type=log_type)\
            .order_by(CMLog.timestamp.desc())\
            .limit(limit)\
            .offset(offset*limit)\
            .all()
        returnval = dict()
        returnval['cm_uuid'] = logs[0].cm_uuid
        returnval['status'] = 'success'
        returnval['data'] = []
        for current_log in logs:
            log_data = {
                'id': current_log.id,
                'log_type': current_log.log_type,
                'timestamp': current_log.timestamp,
                'data': current_log.data
            }
            returnval['data'].append(log_data)

        return jsonify(returnval), 200
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "missing json"
            }), 415
        if not CMMeta.query.filter_by(uuid=cm_uuid).first():
            return jsonify({
                'status': 'error',
                'message': 'invalid control module uuid'
            }), 404

        log_type = request.json.get('log_type')
        data = request.json.get('data')

        error = False
        missing = None
        if not log_type:
            error = True
            missing = "log_type"
        if not data:
            error = True
            missing = "data"
        if error:
            return jsonify({
                "status": "error",
                "message": "missing " + missing
            }), 422

        if not CMLogTypes.query.filter_by(cm_uuid=cm_uuid, log_type=log_type).first():
            CMLogTypes.create(cm_uuid, log_type)
        return jsonify(CMLog.create(cm_uuid, log_type, request.json.get("data"))), 201
