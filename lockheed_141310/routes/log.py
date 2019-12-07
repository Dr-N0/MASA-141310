from flask import Blueprint, request, jsonify

from lockheed_141310 import db
from lockheed_141310.models import CMLog, CMMeta

log_bp = Blueprint('log_bp', __name__)


# pylint: disable=inconsistent-return-statements
@log_bp.route('/<cm_uuid>/<log_type>', methods=['GET', 'POST'])
def log(cm_uuid: str, log_type: str):
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


@log_bp.route('/create_log')
def create_log():
    cm_uuid = CMMeta.query.first().uuid
    new_log = CMLog(cm_uuid, "test", {"data": "test"})
    db.session.add(new_log)
    db.session.commit()
    return jsonify({"status": "success"}), 200
