from flask import Blueprint, request, jsonify
from services.incident_service import get_categories, create_category, update_category, delete_category
from services.auth_service import require_auth

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('', methods=['GET'])
def list_categories():
    return jsonify({"success": True, "categories": get_categories()}), 200

@categories_bp.route('', methods=['POST'])
@require_auth
def create_new_category():
    result = create_category(request.get_json())
    return jsonify(result), 201 if result['success'] else 400

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@require_auth
def update_existing_category(category_id):
    result = update_category(category_id, request.get_json())
    return jsonify(result), 200 if result['success'] else 400

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@require_auth
def delete_existing_category(category_id):
    result = delete_category(category_id)
    return jsonify(result), 200 if result['success'] else 400