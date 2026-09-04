import os

from flask import Flask, jsonify, send_from_directory,render_template
from flask_cors import CORS
from dotenv import load_dotenv

from config import Config
from database import init_db
from routes import register_routes
from socket_instance import socketio
from socket_events import register_socket_events


load_dotenv()


app = Flask(__name__)

app.config.from_object(Config)

CORS(
    app,
    supports_credentials=True
)


# Initialize Socket.IO with Flask
socketio.init_app(
    app,
    cors_allowed_origins="*"
)


init_db(app)

register_routes(app)

register_socket_events(socketio)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test-db')
def test_db():

    try:
        from database import get_cursor

        cursor = get_cursor()

        cursor.execute("SELECT 1 AS test")

        result = cursor.fetchone()

        cursor.close()

        return jsonify({
            "success": True,
            "database": result
        })

    except Exception as e:

        print("DATABASE TEST ERROR:", repr(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/uploads/<path:filename>')
def serve_upload(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


@app.route('/api/health')
def health_check():

    return jsonify({
        "status": "ok",
        "message": "CivicReport API is running"
    })


if __name__ == '__main__':

    port = int(
        os.environ.get(
            'PORT',
            5000
        )
    )

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=True
    )