from werkzeug.security import generate_password_hash, check_password_hash
from database import get_cursor
from functools import wraps
from flask import request, jsonify, g
import secrets

def generate_token(): return secrets.token_urlsafe(32)

def register_user(data):
    if not all([data.get('full_name'), data.get('email'), data.get('phone'), data.get('password')]):
        return {"success": False, "message": "All fields are required"}
    cursor = get_cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
    if cursor.fetchone(): return {"success": False, "message": "Email already registered"}
    
    token = generate_token()
    try:
        cursor.execute("INSERT INTO users (full_name, email, phone, password_hash, api_token) VALUES (%s, %s, %s, %s, %s)",
                      (data['full_name'], data['email'], data['phone'], generate_password_hash(data['password']), token))
        cursor.execute("SELECT id, full_name, email, phone, created_at FROM users WHERE email = %s", (data['email'],))
        return {"success": True, "message": "User registered successfully", "user": cursor.fetchone(), "token": token}
    except Exception: return {"success": False, "message": "Registration failed"}

def login_user(data):
    cursor = get_cursor()
    cursor.execute("SELECT id, full_name, email, phone, password_hash, api_token FROM users WHERE email = %s", (data['email'],))
    user = cursor.fetchone()
    if not user or not check_password_hash(user['password_hash'], data['password']):
        return {"success": False, "message": "Invalid email or password"}
    
    new_token = generate_token()
    cursor.execute("UPDATE users SET api_token = %s WHERE id = %s", (new_token, user['id']))
    return {"success": True, "message": "Login successful", "user": {"id": user['id'], "full_name": user['full_name'], "email": user['email'], "phone": user['phone']}, "token": new_token}

def get_user_by_token(token):
    cursor = get_cursor()
    cursor.execute("SELECT id, full_name, email, phone, created_at FROM users WHERE api_token = %s", (token,))
    return cursor.fetchone()

def update_user_profile(user_id, data):
    cursor = get_cursor()
    fields, values = [], []
    for key, value in data.items():
        fields.append(f"{key} = %s")
        values.append(value)
    values.append(user_id)
    try:
        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = %s", tuple(values))
        cursor.execute("SELECT id, full_name, email, phone, created_at FROM users WHERE id = %s", (user_id,))
        return {"success": True, "message": "Profile updated", "user": cursor.fetchone()}
    except Exception: return {"success": False, "message": "Update failed"}

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Missing or invalid authorization header"}), 401
        user = get_user_by_token(auth_header.split(' ')[1])
        if not user: return jsonify({"success": False, "message": "Invalid or expired token"}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function