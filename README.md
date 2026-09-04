 
Got it. Your routes/__init__.py is fine. The problem is specifically the relationship between app.py, incident_service.py, and socket_events.py.

You do have a socket_events.py according to your app.py:

from socket_events import register_socket_events
So the file should be located here:

backend/
├── app.py
├── socket_events.py   ← this is the file
├── database.py
├── config.py
├── routes/
└── services/
The error happens because your incident_service.py is doing:

from app import socketio
That creates the circular import.

Best fix for your current project
You don't need to completely redesign your backend. Since your current app.py already creates socketio, the cleanest solution is to make socket_events.py responsible only for event registration and pass the Socket.IO instance into the functions that need it.

However, because incident_service.py needs to emit events, I recommend using a small separate Socket.IO module.

FILE 1 — Create this
backend/socket_instance.py
from flask_socketio import SocketIO


socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)
FILE 2 — Change app.py
Your current app.py:

from flask_socketio import SocketIO
and:

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
should be changed.

Use:

import os

from flask import Flask, jsonify, send_from_directory
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
The important difference is:

from socket_instance import socketio
instead of:

from flask_socketio import SocketIO
and:

socketio.init_app(app, cors_allowed_origins="*")
instead of creating it directly inside app.py.

FILE 3 — socket_events.py
You said you don't have this file, but your app.py currently contains:

from socket_events import register_socket_events
Therefore you need to create it.

Create:

backend/socket_events.py
with:

from flask import request


def register_socket_events(socketio):

    @socketio.on('connect')
    def handle_connect():

        print(
            f"Socket.IO client connected: {request.sid}"
        )


    @socketio.on('disconnect')
    def handle_disconnect():

        print(
            f"Socket.IO client disconnected: {request.sid}"
        )


    @socketio.on('join_incidents')
    def handle_join_incidents():

        print(
            f"Client joined incident updates: {request.sid}"
        )
This matches what your current app.py expects:

register_socket_events(socketio)
FILE 4 — Fix incident_service.py
This is the most important change.

Find this:

from app import socketio
Remove it.

Replace it with:

from socket_instance import socketio
So the beginning of your service should look like:

from database import get_db_connection
from socket_instance import socketio
depending on what your existing imports are.

Now your dependency flow becomes:

app.py
 │
 ├── routes
 │    └── incidents
 │         └── incident_service
 │
 └── socket_instance
       └── socketio
Instead of:

app.py
 ↓
routes
 ↓
incident_service
 ↓
app.py  ❌
Your routes/__init__.py is already correct
You don't need to change this:

from .auth import auth_bp
from .incidents import incidents_bp
from .categories import categories_bp
from .users import users_bp
from .reports import reports_bp


def register_routes(app):

    app.register_blueprint(
        auth_bp,
        url_prefix='/api/auth'
    )

    app.register_blueprint(
        incidents_bp,
        url_prefix='/api/incidents'
    )

    app.register_blueprint(
        categories_bp,
        url_prefix='/api/categories'
    )

    app.register_blueprint(
        users_bp,
        url_prefix='/api/users'
    )

    app.register_blueprint(
        reports_bp,
        url_prefix='/api/reports'
    )
That part is fine.

Final backend structure
You should now have:

CivicReport/
│
├── backend/
│   │
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── socket_instance.py       ← NEW
│   ├── socket_events.py         ← NEW
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── incidents.py
│   │   ├── categories.py
│   │   ├── users.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── incident_service.py
│   │   ├── image_service.py
│   │   └── notification_service.py
│   │
│   └── uploads/
│       └── incidents/
Then run:

python app.py
You should no longer get:

ImportError: cannot import name 'register_routes'
because incident_service.py will no longer cause Python to re-import app.py.

One caution
There may be another circular import elsewhere in the generated backend. If you make these changes and get another traceback, send me the new traceback plus the top ~20 lines of the file named in the traceback. We can fix the dependency chain one step at a time rather than rewriting your whole project.


Give me a read.md for these project 

Below is a complete README.md for your CivicReport project, covering the frontend, Flask API, MySQL database, Socket.IO, image uploads, geolocation, and Cordova packaging.

This README is also structured so that, when you eventually submit the project, the lecturer can quickly see what the application does, the technology stack, architecture, database design, API, and Cordova workflow.


127.0.0.1 - - [04/Sep/2026 13:49:50] "OPTIONS /api/categories HTTP/1.1" 200 -
127.0.0.1 - - [04/Sep/2026 13:49:50] "GET /api/categories HTTP/1.1" 500 -
Traceback (most recent call last):
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask\app.py", line 1478, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask_socketio\__init__.py", line 43, in __call__
    return super(_SocketIOMiddleware, self).__call__(environ,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\engineio\middleware.py", line 74, in __call__
    return self.wsgi_app(environ, start_response)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask\app.py", line 1458, in wsgi_app
    response = self.handle_exception(e)
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask_cors\extension.py", line 176, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask\app.py", line 1455, in wsgi_app
    response = self.full_dispatch_request()
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask\app.py", line 869, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask_cors\extension.py", line 176, in wrapped_function
    return cors_after_request(app.make_response(f(*args, **kwargs)))
                                                ~^^^^^^^^^^^^^^^^^
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask\app.py", line 867, in full_dispatch_request
    rv = self.dispatch_request()
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\venv\Lib\site-packages\flask\app.py", line 852, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\routes\categories.py", line 9, in list_categories
    return jsonify({"success": True, "categories": get_categories()}), 200
                                                   ~~~~~~~~~~~~~~^^
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\services\incident_service.py", line 64, in get_categories
    cursor = get_cursor()
  File "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio\CivicReport\CivicReport\backend\database.py", line 18, in get_cursor

The important part is at the bottom of the traceback:

categories.py → get_categories()
              → incident_service.py
              → database.py
              → get_cursor()
So CORS and Socket.IO are not the problem. Your GET /api/categories is reaching Flask correctly, but get_cursor() is failing.

I need to see the rest of the traceback because the actual MySQL error is cut off after:

backend\database.py", line 18, in get_cursor
Please send me these 2 files
1. database.py

Especially around:

def get_cursor():
2. services/incident_service.py

Especially:

def get_categories():
Also send the next few lines of the traceback after:

File "...backend\database.py", line 18, in get_cursor
That final line will tell us whether it's:

MySQL connection failure

connection pool problem

database doesn't exist

table doesn't exist

cursor creation problem

environment variable problem

closed connection

or something else.

Your route itself appears fine:

@app.route("/api/categories")
and the request is successfully reaching it:

"GET /api/categories HTTP/1.1" 500
So don't change routes/__init__.py or CORS yet. The problem is almost certainly inside your database connection/cursor code.


Yes — now we can see the likely problem.

Your incident_service.py is fine for the category query. The failure happens before cursor.execute(), here:

def get_categories():
    cursor = get_cursor()
and then:

def get_cursor():
    return get_db_connection().cursor(dictionary=True)
So the database connection itself is failing.

1. First, make database.py more robust
Replace your current database.py with this:

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
2. Check your Config
Your config.py should have something like:

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "civicreport")

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "uploads",
        "incidents"
    )
And your .env should look like:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=civicreport
Obviously use your actual MySQL password/database name.

3. Test the database independently
Before testing /api/categories, temporarily add this route to app.py:

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
Restart Flask:

python app.py
Then open:

http://127.0.0.1:5000/api/test-db
If everything is correct, you should get:

{
    "database": {
        "test": 1
    },
    "success": true
}
4. Then test categories
If /api/test-db works but:

GET /api/categories
still returns 500, then the next thing to check is the actual categories table.

Run this in MySQL:

USE civicreport;

SHOW TABLES;

DESCRIBE categories;

SELECT * FROM categories;
Your table should have at least:

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
And you can add some initial categories:

INSERT INTO categories (name, description)
VALUES
('Road Damage', 'Potholes, damaged roads and unsafe road conditions'),
('Street Lighting', 'Broken or non-functional street lights'),
('Waste Management', 'Illegal dumping and waste-related issues'),
('Water Supply', 'Water leaks and water supply problems'),
('Public Safety', 'Issues affecting public safety'),
('Traffic', 'Traffic-related problems'),
('Other', 'Other civic issues');
One more important improvement
Your incident_service.py currently has:

from socket_instance import socketio
That's okay with the circular-import fix we discussed.

But you should not leave database cursors open everywhere. For example:

def get_categories():
    cursor = get_cursor()
    cursor.execute("SELECT id, name, description FROM categories ORDER BY name")
    return cursor.fetchall()
is functional, but better is:

def get_categories():
    cursor = get_cursor()

    try:
        cursor.execute(
            "SELECT id, name, description FROM categories ORDER BY name"
        )

        return cursor.fetchall()

    finally:
        cursor.close()
Do the same for your other service functions.

Most importantly: run /api/test-db and send me the JSON/error it gives you. That will identify the exact MySQL problem instead of guessing.


error	"int() argument must be a string, a bytes-like object or a real number, not 'NoneType'"
success	false
error


Good — that error tells us exactly what is wrong.

int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
The problem is this line I suggested in database.py:

port=int(current_app.config['DB_PORT'])
DB_PORT is currently None.

So your .env/config.py isn't providing DB_PORT.

Fix your .env
Open:

backend/.env
Make sure you have:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=civicreport
If your MySQL password is empty:

DB_PASSWORD=
Fix config.py
Use this:

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "civicreport")

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "uploads",
        "incidents"
    )
Notice this:

os.getenv("DB_PORT", "3306")
The "3306" is the fallback if DB_PORT isn't present.

Important: .env location
Your structure should be approximately:

CivicReport/
│
├── backend/
│   ├── .env
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── socket_instance.py
│   ├── socket_events.py
│   ├── routes/
│   ├── services/
│   └── ...
│
└── frontend/
And you're running:

cd backend
python app.py
So backend/.env is the right place.

Then restart Flask
Stop it with:

CTRL + C
and run:

python app.py
Then test:

http://127.0.0.1:5000/api/test-db
You should now get:

{
    "success": true,
    "database": {
        "test": 1
    }
}
If you still get an error, send me your current config.py (you can replace the actual MySQL password with ********). That will show us why DB_PORT isn't being loaded.


how do i use cordova to package it into an adriod APK

Yes. Since your CivicReport frontend is already HTML5 + CSS3 + Vanilla JS, Cordova is a good fit for packaging it as an Android APK.

The important thing is that Cordova packages your frontend, while your Flask backend remains a separate server.

Your architecture will be:

CivicReport
│
├── frontend/www/          ← Cordova app
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── images/
│   └── ...
│
└── backend/               ← Flask API
    ├── app.py
    ├── routes/
    ├── services/
    └── ...
Then:

Android APK
    ↓
Cordova WebView
    ↓
HTML / CSS / JavaScript
    ↓
HTTP requests
    ↓
Flask API
    ↓
MySQL
1. Install Node.js
You already have Node installed from your previous Expo work, so check:

node -v
npm -v
Then install Cordova:

npm install -g cordova
Check:

cordova -v
2. Install Java JDK
Cordova Android requires Java.

Check:

java -version
If Java isn't installed, install a supported JDK such as JDK 17.

After installation:

java -version
should return something similar to:

openjdk version "17..."
3. Install Android Studio
Install Android Studio and make sure the Android SDK is installed.

Inside Android Studio, open:

SDK Manager

Make sure you have:

Android SDK

Android SDK Platform

Android SDK Build-Tools

Android SDK Command-line Tools

Android SDK Platform-Tools

You don't necessarily need to create the app in Android Studio. Cordova will generate the Android project for you.

4. Set Android environment variables
On Windows, you need Android's SDK location available to Cordova.

Typical location:

C:\Users\YOUR_USERNAME\AppData\Local\Android\Sdk
Set:

ANDROID_HOME
to your Android SDK directory.

For example:

ANDROID_HOME=C:\Users\YOUR_USERNAME\AppData\Local\Android\Sdk
And add these to your PATH:

%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\cmdline-tools\latest\bin
Then close and reopen PowerShell.

Test:

adb --version
and:

sdkmanager --version
5. Prepare your CivicReport frontend
Your frontend should be inside:

CivicReport/
└── frontend/
    └── www/
        ├── index.html
        ├── css/
        │   └── style.css
        ├── js/
        │   └── app.js
        └── images/
Cordova expects the web application inside its www directory.

If you already have a Cordova project, you can use that www folder.

6. Create the Cordova project
If you haven't created one yet, go to the directory where you want the mobile project:

cd "C:\Users\Elitebook 1040 G6\OneDrive\Desktop\web developmen\bincom-portfolio"
Create it:

cordova create CivicReportMobile com.civicreport.app CivicReport
You'll get:

CivicReportMobile/
├── config.xml
├── hooks/
├── platforms/
├── plugins/
└── www/
7. Copy your CivicReport frontend into Cordova
Copy your existing:

frontend/www/
into:

CivicReportMobile/www/
So ultimately:

CivicReportMobile/
│
├── config.xml
│
├── www/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── images/
│
├── platforms/
└── plugins/
Your index.html must be directly inside www:

www/index.html
not:

www/frontend/index.html
8. Add Android to Cordova
From inside the Cordova project:

cd CivicReportMobile
Run:

cordova platform add android
If everything is installed correctly, you'll see Android being added.

Then:

cordova requirements
This is an important command.

It checks whether your Java/Android SDK environment is ready.

You want the required components to show as installed.

9. Configure your Flask API URL
This is extremely important.

During development you might have:

const API_URL = "http://127.0.0.1:5000/api";
That will NOT work from an Android phone.

Why?

Because on the Android device:

127.0.0.1
means the Android device itself, not your Windows computer.

For a real APK, your Flask backend needs to be hosted somewhere accessible, for example your Render deployment.

Then use:

const API_URL = "https://your-civicreport-backend.onrender.com/api";
For example:

fetch(`${API_URL}/categories`)
Your final architecture becomes:

CivicReport APK
       │
       │ HTTPS
       ▼
Flask API on Render
       │
       ▼
     MySQL
This is what you should use for your assessment/demo if your backend is deployed.

10. Configure Cordova permissions
Open:

config.xml
You can have something like:

<?xml version='1.0' encoding='utf-8'?>
<widget id="com.civicreport.app"
        version="1.0.0"
        xmlns="http://www.w3.org/ns/widgets"
        xmlns:android="http://schemas.android.com/apk/res/android">

    <name>CivicReport</name>

    <description>
        Civic incident reporting mobile application
    </description>

    <author email="support@civicreport.app">
        CivicReport
    </author>

    <content src="index.html" />

    <access origin="*" />

    <allow-navigation href="*" />

    <preference name="AndroidXEnabled" value="true" />

    <preference name="Fullscreen" value="false" />

    <preference name="DisallowOverscroll" value="true" />

</widget>
For a production app, you should restrict network access instead of leaving everything open, but this is useful for getting the assessment project running.

11. Add camera and geolocation plugins
Your CivicReport app has incident photos and location reporting, so you'll probably need Cordova plugins.

For geolocation:

cordova plugin add cordova-plugin-geolocation
For camera:

cordova plugin add cordova-plugin-camera
For your existing HTML <input type="file" accept="image/*">, you may not need the camera plugin immediately. Android's file picker can often handle image selection.

12. Test the web application first
Before building an APK, make sure your frontend works in a browser.

For example:

index.html
should load correctly.

Test:

Login

Registration

Categories

Incident creation

Image upload

Location

My reports

Notifications

Socket.IO

And make sure the API URL points to your Flask backend.

13. Build the APK
From:

CivicReportMobile
run:

cordova build android
If successful, Cordova will generate an APK.

The debug APK is usually located around:

CivicReportMobile\platforms\android\app\build\outputs\apk\debug\app-debug.apk
You can verify it with:

dir platforms\android\app\build\outputs\apk\debug\
14. Install the APK on your Android phone
Enable Developer Options and USB debugging on your test phone.

Connect it to your computer.

Check:

adb devices
You should see your device.

Then:

cordova run android
Cordova will build and install the application.

Alternatively, you can take the generated:

app-debug.apk
and install it on your test device.

15. If you want to test directly from your computer
You can also use an Android emulator.

Open Android Studio → Device Manager → create an Android Virtual Device.

Start the emulator and then:

cordova run android
16. One big issue with your Socket.IO backend
Your CivicReport backend uses:

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)
That's fine for development.

Your mobile app's JavaScript can connect to the deployed Flask server:

const socket = io(API_BASE_URL, {
    transports: ["websocket", "polling"]
});
But make sure your deployed server supports WebSocket/Socket.IO correctly.

17. For your current project, I recommend this structure
Since you're already working on CivicReport, I'd organize it like this:

CivicReport/
│
├── mobile/
│   │
│   ├── config.xml
│   │
│   ├── www/
│   │   ├── index.html
│   │   │
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   ├── auth.css
│   │   │   ├── dashboard.css
│   │   │   └── reports.css
│   │   │
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   ├── auth.js
│   │   │   ├── dashboard.js
│   │   │   ├── reports.js
│   │   │   ├── api.js
│   │   │   └── socket.js
│   │   │
│   │   └── images/
│   │
│   ├── platforms/
│   └── plugins/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── socket_instance.py
│   ├── socket_events.py
│   │
│   ├── routes/
│   ├── services/
│   ├── uploads/
│   └── ...
│
└── database/
    └── schema.sql
The key point is:

Don't put Flask inside the APK.

The APK contains:

HTML
CSS
JavaScript
Cordova
while Flask/MySQL stay on the server.

The complete command sequence
Once Java + Android Studio + SDK are installed, the basic workflow is:

npm install -g cordova
cordova create CivicReportMobile com.civicreport.app CivicReport
cd CivicReportMobile
cordova platform add android
cordova requirements
Then put your frontend into:

CivicReportMobile/www/
Then:

cordova build android
And your APK will be generated under:

platforms\android\app\build\outputs\apk\debug\
One thing I would do before you build: get your Flask API working from the phone first. Since your current API is running on 127.0.0.1:5000, the APK won't be able to reach it unless you either use your computer's LAN IP while testing on the same Wi-Fi or deploy the Flask backend (e.g. to Render) and point the APK to that HTTPS URL.



CivicReport
CivicReport
Report incidents. Keep your community informed.
CivicReport is a mobile-first citizen incident reporting application developed as a Mobile App Development / Cross Platform Mobile Development assessment project.

The application allows citizens to report community incidents such as accidents, fires, theft, fighting, rioting, and other incidents. Users can provide descriptions, locations, GPS coordinates, and images.

The project uses a Vanilla JavaScript frontend, a Python Flask REST API, MySQL for persistent storage, and Socket.IO for real-time incident updates.

The frontend is designed to be packaged as an Android application using Apache Cordova.

Features
Authentication
User registration

User login

User logout

Password hashing

Protected API endpoints

Authentication state

User profile management

Incident Reporting
Users can:

Create incident reports

Select incident categories

Add incident descriptions

Enter locations

Capture latitude and longitude

Use device/browser geolocation

Upload incident images

View incident details

View report status

Incident Categories
The application supports:

Accident

Fighting

Rioting

Fire

Theft

Other

Categories are stored in MySQL and retrieved through the Flask API.

My Reports
Logged-in users can view incidents they personally submitted.

Notifications
Users can receive notifications when new incidents are reported.

Notifications support:

Read/unread state

Notification badge

Notification list

Real-time updates

Real-Time Updates
CivicReport uses Flask-SocketIO to notify connected users when a new incident is submitted.

For example:

User A submits an incident
        ↓
Flask API
        ↓
MySQL
        ↓
Socket.IO event
        ↓
Connected users
        ↓
Incident appears without refreshing
Image Uploads
Users can attach images to incident reports.

The Flask backend:

Accepts image uploads

Validates uploaded files

Generates safe filenames

Stores images on the server

Returns the image path to the frontend

Geolocation
The application can obtain the user's current location using the browser/Cordova geolocation API.

The following information can be stored:

Location

Latitude

Longitude

Technology Stack
Frontend
HTML5

CSS3

Vanilla JavaScript

No frontend framework is used.

The application does not use:

React

React Native

Vue

Angular

Bootstrap

Tailwind

jQuery

Backend
Python

Flask

Flask-CORS

Flask-SocketIO

MySQL Connector/Python

Werkzeug password hashing

python-dotenv

Mobile Packaging
Apache Cordova

Android platform

Database
MySQL

Project Architecture
                         CivicReport
                              │
                              ▼
                     Cordova Android App
                              │
                              ▼
                      HTML / CSS / JS
                              │
                     HTTP REST API
                              │
                              ▼
                       Python Flask
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       Authentication     Incidents        Categories
             │                │                │
             │                ├── Images       │
             │                └── Locations    │
             │                                 │
             └───────────────┬─────────────────┘
                             │
                             ▼
                           MySQL
                             │
                             │
                     Flask-SocketIO
                             │
                             ▼
                    Real-Time Updates
Project Structure
CivicReport/
│
├── frontend/
│   └── www/
│       │
│       ├── index.html
│       │
│       ├── css/
│       │   └── style.css
│       │
│       ├── js/
│       │   └── app.js
│       │
│       └── images/
│
│
├── backend/
│   │
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── socket_instance.py
│   ├── socket_events.py
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── incidents.py
│   │   ├── categories.py
│   │   ├── users.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── incident_service.py
│   │   ├── image_service.py
│   │   └── notification_service.py
│   │
│   ├── utils/
│   │   └── helpers.py
│   │
│   └── uploads/
│       └── incidents/
│
│
├── database/
│   └── schema.sql
│
├── config.xml
│
└── README.md
Frontend
The frontend is a single-page mobile-first application.

The main HTML structure is located in:

frontend/www/index.html
CSS is located in:

frontend/www/css/style.css
JavaScript is located in:

frontend/www/js/app.js
The frontend communicates with Flask using the JavaScript fetch() API.

Backend
The Flask backend provides the REST API consumed by the mobile application.

The main application entry point is:

backend/app.py
The backend is responsible for:

Authentication

Users

Incidents

Categories

Reports

Notifications

Image uploads

Geolocation data

Database operations

Socket.IO events

Database
CivicReport uses MySQL for persistent data storage.

The database schema is located at:

database/schema.sql
The main tables are:

users
categories
incidents
incident_images
notifications
Relationships:

users
 │
 ├────────────── incidents
 │                    │
 │                    └──────── incident_images
 │
 └────────────── notifications

categories
 │
 └────────────── incidents
API Endpoints
Authentication
Register
POST /api/auth/register
Creates a new CivicReport account.

Example request:

{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "08000000000",
    "password": "Password123"
}
Login
POST /api/auth/login
Authenticates an existing user.

Logout
POST /api/auth/logout
Logs the current user out.

Current User
GET /api/auth/me
Returns information about the authenticated user.

Categories
Get Categories
GET /api/categories
Returns available incident categories.

Incidents
Get Incidents
GET /api/incidents
Returns available incident reports.

Category filtering can be performed using query parameters where supported.

Example:

GET /api/incidents?category_id=1
Get Incident
GET /api/incidents/<id>
Returns information about a specific incident.

Create Incident
POST /api/incidents
Creates a new incident.

The request uses:

multipart/form-data
Example fields:

title
category_id
description
location
latitude
longitude
image
Update Incident
PUT /api/incidents/<id>
Updates an incident.

Delete Incident
DELETE /api/incidents/<id>
Deletes an incident where the authenticated user has permission to do so.

User Reports
Get My Reports
GET /api/reports/my
Returns incidents submitted by the authenticated user.

User Profile
Get Profile
GET /api/users/me
Returns the current user's profile.

Update Profile
PUT /api/users/me
Updates the current user's profile information.

Notifications
Get Notifications
GET /api/notifications
Returns notifications for the authenticated user.

Mark Notification as Read
PATCH /api/notifications/<id>/read
Marks a notification as read.

Mark All Notifications as Read
PATCH /api/notifications/read-all
Marks all notifications as read.

Socket.IO
CivicReport uses Socket.IO for real-time updates.

When an incident is successfully created, the Flask backend emits:

new_incident
Connected clients can listen for this event.

Example frontend logic:

socket.on("new_incident", function (incident) {
    console.log("New incident:", incident);

    // Update incident list
    // Update notification badge
    // Display notification
});
This allows users to see new incidents without manually refreshing the application.

Authentication Flow
The authentication flow is:

User
 │
 ▼
Login Form
 │
 ▼
JavaScript
 │
 │ POST /api/auth/login
 ▼
Flask
 │
 ▼
MySQL
 │
 ▼
Verify Password
 │
 ▼
Authentication Response
 │
 ▼
Frontend
 │
 ▼
Dashboard
Passwords are hashed before being stored in the database.

Plaintext passwords should never be stored in MySQL or localStorage.

Incident Reporting Flow
User
 │
 ▼
Report Incident
 │
 ├── Title
 ├── Category
 ├── Description
 ├── Location
 ├── Latitude
 ├── Longitude
 └── Image
 │
 ▼
JavaScript Validation
 │
 ▼
POST /api/incidents
 │
 ▼
Flask API
 │
 ├── Authenticate User
 ├── Validate Data
 ├── Validate Category
 ├── Process Image
 └── Save Incident
 │
 ▼
MySQL
 │
 ▼
Socket.IO
 │
 ▼
Connected Users
Environment Configuration
The backend uses environment variables.

Create:

backend/.env
based on:

backend/.env.example
Example:

DB_HOST=localhost
DB_PORT=3306
DB_NAME=civicreport
DB_USER=root
DB_PASSWORD=your_password

SECRET_KEY=your_secret_key

UPLOAD_FOLDER=uploads/incidents
Do not commit the real .env file to GitHub.

Installing the Backend
Make sure Python is installed.

Navigate to the backend directory:

cd backend
Create a virtual environment:

python -m venv venv
Activate it on Windows:

venv\Scripts\activate
Install the required packages:

pip install -r requirements.txt
Setting Up MySQL
Open MySQL or MySQL Workbench.

Run:

database/schema.sql
This will create the CivicReport database and required tables.

Make sure the credentials in:

backend/.env
match your MySQL configuration.

Running Flask
Navigate to:

backend/
Activate the virtual environment:

venv\Scripts\activate
Then run:

python app.py
The backend should start on:

http://127.0.0.1:5000
The health endpoint is:

http://127.0.0.1:5000/api/health
A successful response should look similar to:

{
    "status": "ok",
    "message": "CivicReport API is running"
}
Frontend API Configuration
The frontend contains a configuration value in:

frontend/www/js/app.js
For local development, it may point to:

const API_BASE_URL = "http://127.0.0.1:5000/api";
When the Flask API is deployed, change it to the production API address.

For example:

const API_BASE_URL = "https://your-civicreport-api.example.com/api";
Do not leave the mobile application pointing to localhost when building the Android APK.

Testing the Frontend
The frontend can be tested in a browser.

The easiest approach is to serve the frontend/www directory using a local development server.

For example, with Python:

cd frontend
python -m http.server 8080 --directory www
Then open:

http://127.0.0.1:8080
Make sure the Flask backend is also running.

Cordova Setup
CivicReport is designed to be packaged using Apache Cordova.

Install Cordova:

npm install -g cordova
Create a Cordova project:

cordova create CivicReport com.example.civicreport CivicReport
Enter the project:

cd CivicReport
Add Android:

cordova platform add android
Replace the generated Cordova www folder with the CivicReport frontend:

frontend/www
The final Cordova structure should look similar to:

CivicReport/
│
├── config.xml
│
├── www/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── images/
│
└── platforms/
Android Permissions
The application may require permissions for:

Internet access

Geolocation

Camera/photo access depending on how image selection is implemented

Cordova configuration should be updated appropriately before building the final APK.

During development, using HTTPS for the Flask API is recommended.

Building the Android APK
After configuring the Cordova project:

cordova build android
The generated Android application will normally be available somewhere under:

platforms/android/app/build/outputs/apk/
The exact output path can vary depending on the Cordova/Android Gradle version.

Development Architecture
During development:

Browser / Cordova
       │
       │ HTTP
       ▼
Flask API
       │
       ▼
MySQL
Socket.IO provides the real-time communication channel:

Flask
  │
  │ Socket.IO
  ▼
Connected Clients
Production Architecture
The intended production architecture is:

                 Android APK
                     │
                     ▼
              Cordova WebView
                     │
                     │ HTTPS
                     ▼
                Flask REST API
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
            MySQL       Socket.IO
                            │
                            ▼
                    Real-Time Updates
The Flask API can be deployed to a Python-compatible hosting provider.

The MySQL database can be hosted on a managed MySQL server.

Security Considerations
The assessment version implements basic security practices.

These include:

Password hashing

Parameterized SQL queries

Authentication

Protected endpoints

Input validation

Image validation

Safe uploaded filenames

Environment variables for secrets

For production deployment, additional security measures should be considered, including:

HTTPS

Strong authentication/session management

Rate limiting

CSRF protection where applicable

More advanced authorization

Secure HTTP headers

Production logging

Database backups

File storage security

Future Improvements
The project can later be extended with:

Push notifications

Google Maps/OpenStreetMap integration

Incident verification

Admin dashboard

Incident moderation

User reporting/reputation system

Incident status tracking

Image cloud storage

Email notifications

Analytics

Search

Advanced filtering

Offline reporting

WordPress API integration

The current architecture intentionally keeps the frontend separated from the backend so that the API layer can be changed later without completely rebuilding the mobile interface.

Assessment Objectives
CivicReport demonstrates the following skills:

HTML5
Semantic HTML

Forms

Navigation

Inputs

Buttons

Modals

Application structure

CSS3
Mobile-first design

Responsive layouts

Flexbox

CSS Grid

Form styling

Cards

Navigation

Animations

Responsive media queries

JavaScript
DOM manipulation

Event handling

Form validation

Fetch API

JSON

API integration

Geolocation

Image preview

Socket.IO

Authentication state

Dynamic UI rendering

Notifications

Local storage

Python Flask
REST API development

Routing

Authentication

Password hashing

MySQL integration

Image uploads

JSON responses

Error handling

Socket.IO

API integration

MySQL
Database creation

Tables

Primary keys

Foreign keys

Relationships

Indexes

CRUD operations

Cordova
Cross-platform mobile development

WebView-based mobile application

Android packaging

Device capabilities

Geolocation

API communication

Application Flow
                    ┌───────────────┐
                    │    Welcome    │
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
           Create Account             Login
                │                       │
                ▼                       ▼
             Register                Authenticate
                │                       │
                └───────────┬───────────┘
                            ▼
                         Dashboard
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
         Reports       Add Report      Notifications
                            │
                            ▼
                     Create Incident
                            │
                     ┌──────┴──────┐
                     ▼             ▼
                   Image        Location
                     │             │
                     └──────┬──────┘
                            ▼
                         Flask
                            │
                            ▼
                          MySQL
                            │
                            ▼
                        Socket.IO
                            │
                            ▼
                    Live User Updates
Author
BIGUDOM (Udom Blessing)

Citizen Incident Reporting Solution

Developed as a Mobile App Development / Cross Platform Mobile Development assessment project.

License
This project is intended for educational and assessment purposes.



