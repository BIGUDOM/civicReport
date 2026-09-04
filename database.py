import mysql.connector
from flask import g, current_app


def get_db_connection():
    """
    Get a MySQL connection for the current Flask request.
    Reuse the connection if one already exists.
    """

    if 'db' not in g:

        try:
            g.db = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                port=int(current_app.config['DB_PORT']),
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME'],
                autocommit=True
            )

        except mysql.connector.Error as e:
            print("MYSQL CONNECTION ERROR:", e)
            raise

    return g.db


def get_cursor():
    """
    Return a dictionary cursor.
    """

    db = get_db_connection()

    if not db.is_connected():
        print("Database connection was closed. Reconnecting...")
        db.reconnect(attempts=3, delay=1)

    return db.cursor(dictionary=True)


def close_db(e=None):
    """
    Close the database connection after every request.
    """

    db = g.pop('db', None)

    if db is not None:
        try:
            if db.is_connected():
                db.close()
        except mysql.connector.Error as e:
            print("MYSQL CLOSE ERROR:", e)


def init_db(app):
    """
    Register Flask database teardown.
    """

    app.teardown_appcontext(close_db)