from database import get_cursor

def create_notification(user_id, title, description, incident_id=None):
    cursor = get_cursor()
    cursor.execute("INSERT INTO notifications (user_id, title, description, incident_id) VALUES (%s, %s, %s, %s)", (user_id, title, description, incident_id))
    return cursor.lastrowid

def get_user_notifications(user_id):
    cursor = get_cursor()
    cursor.execute("""SELECT id, title, description, incident_id, is_read, created_at FROM notifications
        WHERE user_id = %s ORDER BY created_at DESC LIMIT 50""", (user_id,))
    return cursor.fetchall()

def mark_notification_read(notification_id, user_id):
    cursor = get_cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = %s AND user_id = %s", (notification_id, user_id))
    return cursor.rowcount > 0

def mark_all_notifications_read(user_id):
    cursor = get_cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0", (user_id,))
    return cursor.rowcount