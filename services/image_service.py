import os
import uuid
from flask import current_app

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    if not file or not file.filename: return {"success": False, "message": "No file provided"}
    if not allowed_file(file.filename): return {"success": False, "message": "Invalid file type. Allowed: png, jpg, jpeg"}
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    try:
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return {"success": True, "filename": filename}
    except Exception as e: return {"success": False, "message": f"Failed to save image: {str(e)}"}

def delete_image(filename):
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath): os.remove(filepath)
        return True
    except Exception: return False