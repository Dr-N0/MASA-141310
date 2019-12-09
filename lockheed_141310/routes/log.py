from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from lockheed_141310.models import CMLog

log_bp = Blueprint('log_bp', __name__)


# pylint: disable=inconsistent-return-statements
@log_bp.route('/<cm_uuid>/<log_type>', methods=['GET', 'POST'])
@jwt_required
def log(cm_uuid: str, log_type: str):
    """
    :GET: returns the specified number of logs matching the specified log type
    :POST: inserts log with data into the database
    """
    if request.method == 'GET':
        limit = 20
        offset = 0
        if limit_arg := request.args.get('limit'):
            limit = limit_arg
        if offset_arg := request.args.get('offset'):
            offset = offset_arg
        query = CMLog.query.filter_by(uuid=cm_uuid, log_type=log_type)\
            .order_by(CMLog.timestamp.desc())\
            .limit(limit)\
            .offset(offset*limit)\
            .all()
        return jsonify([cm_log.to_json() for cm_log in query.all()]), 200
    if request.method == 'POST':
        pass
