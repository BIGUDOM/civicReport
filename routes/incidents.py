from flask import Blueprint, request, jsonify, g
from services.incident_service import get_incidents, get_incident_by_id, create_incident, update_incident, delete_incident
from services.auth_service import require_auth
from services.image_service import save_image, delete_image

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('', methods=['GET'])
def list_incidents():
    return jsonify({"success": True, "incidents": get_incidents(request.args.get('category_id'))}), 200

@incidents_bp.route('/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    incident = get_incident_by_id(incident_id)
    return jsonify({"success": True, "incident": incident}), 200 if incident else (jsonify({"success": False, "message": "Incident not found"}), 404)

@incidents_bp.route('', methods=['POST'])
@require_auth
def create_new_incident():
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    description = request.form.get('description')
    location = request.form.get('location_text') or request.form.get('location')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    image = request.files.get('image')
    
    if not all([title, category_id, description, location, latitude, longitude]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    image_path = None
    if image and image.filename != '':
        result = save_image(image)
        if not result['success']: return jsonify(result), 400
        image_path = result['filename']
    
    result = create_incident({
        'user_id': g.current_user['id'], 'category_id': category_id, 'title': title,
        'description': description, 'location': location, 'latitude': latitude,
        'longitude': longitude, 'image_path': image_path
    })
    return jsonify(result), 201 if result['success'] else 400

@incidents_bp.route('/<int:incident_id>', methods=['PUT'])
@require_auth
def update_existing_incident(incident_id):
    result = update_incident(incident_id, g.current_user['id'], request.get_json())
    return jsonify(result), 200 if result['success'] else 400

@incidents_bp.route('/<int:incident_id>', methods=['DELETE'])
@require_auth
def delete_existing_incident(incident_id):
    incident = get_incident_by_id(incident_id)
    if not incident or incident['user_id'] != g.current_user['id']:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if incident['image_path']: delete_image(incident['image_path'])
    result = delete_incident(incident_id)
    return jsonify(result), 200 if result['success'] else 400