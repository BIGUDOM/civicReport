from flask import Blueprint, jsonify, g
from services.incident_service import get_user_incidents
from services.auth_service import require_auth

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/my', methods=['GET'])
@require_auth
def get_my_reports():
    return jsonify({"success": True, "reports": get_user_incidents(g.current_user['id'])}), 200