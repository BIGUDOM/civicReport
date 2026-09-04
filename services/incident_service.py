from database import get_cursor
from socket_instance import socketio

def get_incidents(category_id=None):
    cursor = get_cursor()
    query = """SELECT i.id, i.title, i.description, i.location, i.latitude, i.longitude, i.status, i.created_at, c.name as category_name, u.full_name as reporter_name, ii.image_path
        FROM incidents i LEFT JOIN categories c ON i.category_id = c.id LEFT JOIN users u ON i.user_id = u.id LEFT JOIN incident_images ii ON i.id = ii.incident_id"""
    params = []
    if category_id:
        query += " WHERE i.category_id = %s"
        params.append(category_id)
    query += " ORDER BY i.created_at DESC"
    cursor.execute(query, tuple(params))
    incidents = cursor.fetchall()
    for inc in incidents: inc['image_url'] = f"/uploads/{inc['image_path']}" if inc['image_path'] else None
    return incidents

def get_incident_by_id(incident_id):
    cursor = get_cursor()
    cursor.execute("""SELECT i.id, i.title, i.description, i.location, i.latitude, i.longitude, i.status, i.created_at, c.name as category_name, u.full_name as reporter_name, ii.image_path
        FROM incidents i LEFT JOIN categories c ON i.category_id = c.id LEFT JOIN users u ON i.user_id = u.id LEFT JOIN incident_images ii ON i.id = ii.incident_id WHERE i.id = %s""", (incident_id,))
    incident = cursor.fetchone()
    if incident: incident['image_url'] = f"/uploads/{incident['image_path']}" if incident['image_path'] else None
    return incident

def create_incident(data):
    cursor = get_cursor()
    try:
        cursor.execute("""INSERT INTO incidents (user_id, category_id, title, description, location, latitude, longitude, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')""",
            (data['user_id'], data['category_id'], data['title'], data['description'], data['location'], data['latitude'], data['longitude']))
        incident_id = cursor.lastrowid
        if data.get('image_path'):
            cursor.execute("INSERT INTO incident_images (incident_id, image_path) VALUES (%s, %s)", (incident_id, data['image_path']))
        
        cursor.execute("SELECT id FROM users WHERE id != %s", (data['user_id'],))
        from services.notification_service import create_notification
        for user in cursor.fetchall():
            create_notification(user['id'], 'New Incident Reported', f"A new incident '{data['title']}' has been reported.", incident_id)
        
        socketio.emit('new_incident', get_incident_by_id(incident_id))
        return {"success": True, "message": "Incident created successfully", "incident": get_incident_by_id(incident_id)}
    except Exception as e: return {"success": False, "message": f"Failed to create incident: {str(e)}"}

def update_incident(incident_id, user_id, data):
    cursor = get_cursor()
    cursor.execute("SELECT user_id FROM incidents WHERE id = %s", (incident_id,))
    incident = cursor.fetchone()
    if not incident or incident['user_id'] != user_id: return {"success": False, "message": "Unauthorized"}
    fields, values = [], []
    for key, value in data.items():
        if key in ['title', 'description', 'location', 'latitude', 'longitude', 'status']:
            fields.append(f"{key} = %s"); values.append(value)
    if not fields: return {"success": False, "message": "No valid fields to update"}
    values.append(incident_id)
    cursor.execute(f"UPDATE incidents SET {', '.join(fields)} WHERE id = %s", tuple(values))
    return {"success": True, "message": "Incident updated", "incident": get_incident_by_id(incident_id)}

def delete_incident(incident_id):
    get_cursor().execute("DELETE FROM incidents WHERE id = %s", (incident_id,))
    return {"success": True, "message": "Incident deleted"}

def get_categories():
    cursor = get_cursor()
    cursor.execute("SELECT id, name, description FROM categories ORDER BY name")
    return cursor.fetchall()

def get_user_incidents(user_id):
    cursor = get_cursor()
    cursor.execute("""SELECT i.id, i.title, i.location, i.status, i.created_at, c.name as category_name
        FROM incidents i LEFT JOIN categories c ON i.category_id = c.id WHERE i.user_id = %s ORDER BY i.created_at DESC""", (user_id,))
    return cursor.fetchall()

def create_category(data):
    cursor = get_cursor()
    cursor.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", (data.get('name'), data.get('description', '')))
    return {"success": True, "message": "Category created", "id": cursor.lastrowid}

def update_category(category_id, data):
    get_cursor().execute("UPDATE categories SET name = %s, description = %s WHERE id = %s", (data.get('name'), data.get('description', ''), category_id))
    return {"success": True, "message": "Category updated"}

def delete_category(category_id):
    get_cursor().execute("DELETE FROM categories WHERE id = %s", (category_id,))
    return {"success": True, "message": "Category deleted"}