from flask_socketio import emit, join_room
from services.auth_service import get_user_by_token

def register_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect(auth):
        token = auth.get('token') if auth else None
        if token:
            user = get_user_by_token(token)
            if user: join_room(f"user_{user['id']}")

    @socketio.on('disconnect')
    def handle_disconnect(): pass