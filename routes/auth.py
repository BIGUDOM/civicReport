from flask import Blueprint, request, jsonify, g
from services.auth_service import register_user, login_user, get_user_by_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    result = register_user(request.get_json())
    return jsonify(result), 201 if result['success'] else 400

@auth_bp.route('/login', methods=['POST'])
def login():
    result = login_user(request.get_json())
    return jsonify(result), 200 if result['success'] else 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

@auth_bp.route('/me', methods=['GET'])
def get_me():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token: return jsonify({"success": False, "message": "Unauthorized"}), 401
    user = get_user_by_token(token)
    return jsonify({"success": True, "user": user}), 200 if user else (jsonify({"success": False, "message": "Invalid token"}), 401)