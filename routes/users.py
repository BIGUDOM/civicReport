from flask import Blueprint, request, jsonify, g
from services.auth_service import require_auth, update_user_profile

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@require_auth
def get_profile():
    return jsonify({"success": True, "user": g.current_user}), 200

@users_bp.route('/me', methods=['PUT'])
@require_auth
def update_profile():
    data = request.get_json()
    update_data = {k: v for k, v in data.items() if k in ['full_name', 'phone']}
    result = update_user_profile(g.current_user['id'], update_data)
    return jsonify(result), 200 if result['success'] else 400