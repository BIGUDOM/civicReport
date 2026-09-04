# CivicReport

### Report incidents. Keep your community informed.

CivicReport is a mobile-first citizen incident reporting application developed as a **Mobile App Development / Cross Platform Mobile Development assessment project**.

The application allows citizens to report community incidents such as accidents, fires, theft, fighting, rioting, and other incidents. Users can provide descriptions, locations, GPS coordinates, and images.

The project uses a **Vanilla JavaScript frontend**, a **Python Flask REST API**, **MySQL** for persistent storage, and **Socket.IO** for real-time incident updates.

The frontend is designed to be packaged as an Android application using **Apache Cordova**.

---

# Features

## Authentication

- User registration
- User login
- User logout
- Password hashing
- Protected API endpoints
- Authentication state
- User profile management

## Incident Reporting

Users can:

- Create incident reports
- Select incident categories
- Add incident descriptions
- Enter locations
- Capture latitude and longitude
- Use device/browser geolocation
- Upload incident images
- View incident details
- View report status

## Incident Categories

The application supports:

- Accident
- Fighting
- Rioting
- Fire
- Theft
- Other

Categories are stored in MySQL and retrieved through the Flask API.

## My Reports

Logged-in users can view incidents they personally submitted.

## Notifications

Users can receive notifications when new incidents are reported.

Notifications support:

- Read/unread state
- Notification badge
- Notification list
- Real-time updates

## Real-Time Updates

CivicReport uses **Flask-SocketIO** to notify connected users when a new incident is submitted.

For example:

```text
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
```

## Image Uploads

Users can attach images to incident reports.

The Flask backend:

- Accepts image uploads
- Validates uploaded files
- Generates safe filenames
- Stores images on the server
- Returns the image path to the frontend

## Geolocation

The application can obtain the user's current location using the browser/Cordova geolocation API.

The following information can be stored:

- Location
- Latitude
- Longitude

---

# Technology Stack

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript

No frontend framework is used.

The application does **not** use:

- React
- React Native
- Vue
- Angular
- Bootstrap
- Tailwind
- jQuery

## Backend

- Python
- Flask
- Flask-CORS
- Flask-SocketIO
- MySQL Connector/Python
- Werkzeug password hashing
- python-dotenv

## Mobile Packaging

- Apache Cordova
- Android platform

## Database

- MySQL

---

# Project Architecture

```text
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
```

---

# Project Structure

```text
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
```

---

# Frontend

The frontend is a single-page mobile-first application.

The main HTML structure is located in:

```text
frontend/www/index.html
```

CSS is located in:

```text
frontend/www/css/style.css
```

JavaScript is located in:

```text
frontend/www/js/app.js
```

The frontend communicates with Flask using the JavaScript `fetch()` API.

---

# Backend

The Flask backend provides the REST API consumed by the mobile application.

The main application entry point is:

```text
backend/app.py
```

The backend is responsible for:

- Authentication
- Users
- Incidents
- Categories
- Reports
- Notifications
- Image uploads
- Geolocation data
- Database operations
- Socket.IO events

---

# Database

CivicReport uses MySQL for persistent data storage.

The database schema is located at:

```text
database/schema.sql
```

The main tables are:

```text
users
categories
incidents
incident_images
notifications
```

Relationships:

```text
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
```

---

# API Endpoints

## Authentication

### Register

```http
POST /api/auth/register
```

Creates a new CivicReport account.

Example request:

```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "08000000000",
    "password": "Password123"
}
```

---

### Login

```http
POST /api/auth/login
```

Authenticates an existing user.

---

### Logout

```http
POST /api/auth/logout
```

Logs the current user out.

---

### Current User

```http
GET /api/auth/me
```

Returns information about the authenticated user.

---

# Categories

### Get Categories

```http
GET /api/categories
```

Returns available incident categories.

---

# Incidents

### Get Incidents

```http
GET /api/incidents
```

Returns available incident reports.

Category filtering can be performed using query parameters where supported.

Example:

```http
GET /api/incidents?category_id=1
```

---

### Get Incident

```http
GET /api/incidents/<id>
```

Returns information about a specific incident.

---

### Create Incident

```http
POST /api/incidents
```

Creates a new incident.

The request uses:

```text
multipart/form-data
```

Example fields:

```text
title
category_id
description
location
latitude
longitude
image
```

---

### Update Incident

```http
PUT /api/incidents/<id>
```

Updates an incident.

---

### Delete Incident

```http
DELETE /api/incidents/<id>
```

Deletes an incident where the authenticated user has permission to do so.

---

# User Reports

### Get My Reports

```http
GET /api/reports/my
```

Returns incidents submitted by the authenticated user.

---

# User Profile

### Get Profile

```http
GET /api/users/me
```

Returns the current user's profile.

### Update Profile

```http
PUT /api/users/me
```

Updates the current user's profile information.

---

# Notifications

### Get Notifications

```http
GET /api/notifications
```

Returns notifications for the authenticated user.

### Mark Notification as Read

```http
PATCH /api/notifications/<id>/read
```

Marks a notification as read.

### Mark All Notifications as Read

```http
PATCH /api/notifications/read-all
```

Marks all notifications as read.

---

# Socket.IO

CivicReport uses Socket.IO for real-time updates.

When an incident is successfully created, the Flask backend emits:

```text
new_incident
```

Connected clients can listen for this event.

Example frontend logic:

```javascript
socket.on("new_incident", function (incident) {
    console.log("New incident:", incident);

    // Update incident list
    // Update notification badge
    // Display notification
});
```

This allows users to see new incidents without manually refreshing the application.

---

# Authentication Flow

The authentication flow is:

```text
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
```

Passwords are hashed before being stored in the database.

Plaintext passwords should never be stored in MySQL or localStorage.

---

# Incident Reporting Flow

```text
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
```

---

# Environment Configuration

The backend uses environment variables.

Create:

```text
backend/.env
```

based on:

```text
backend/.env.example
```

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=civicreport
DB_USER=root
DB_PASSWORD=your_password

SECRET_KEY=your_secret_key

UPLOAD_FOLDER=uploads/incidents
```

Do not commit the real `.env` file to GitHub.

---

# Installing the Backend

Make sure Python is installed.

Navigate to the backend directory:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

---

# Setting Up MySQL

Open MySQL or MySQL Workbench.

Run:

```text
database/schema.sql
```

This will create the CivicReport database and required tables.

Make sure the credentials in:

```text
backend/.env
```

match your MySQL configuration.

---

# Running Flask

Navigate to:

```text
backend/
```

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

Then run:

```powershell
python app.py
```

The backend should start on:

```text
http://127.0.0.1:5000
```

The health endpoint is:

```text
http://127.0.0.1:5000/api/health
```

A successful response should look similar to:

```json
{
    "status": "ok",
    "message": "CivicReport API is running"
}
```

---

# Frontend API Configuration

The frontend contains a configuration value in:

```text
frontend/www/js/app.js
```

For local development, it may point to:

```javascript
const API_BASE_URL = "http://127.0.0.1:5000/api";
```

When the Flask API is deployed, change it to the production API address.

For example:

```javascript
const API_BASE_URL = "https://your-civicreport-api.example.com/api";
```

Do not leave the mobile application pointing to `localhost` when building the Android APK.

---

# Testing the Frontend

The frontend can be tested in a browser.

The easiest approach is to serve the `frontend/www` directory using a local development server.

For example, with Python:

```powershell
cd frontend
python -m http.server 8080 --directory www
```

Then open:

```text
http://127.0.0.1:8080
```

Make sure the Flask backend is also running.

---

# Cordova Setup

CivicReport is designed to be packaged using Apache Cordova.

Install Cordova:

```powershell
npm install -g cordova
```

Create a Cordova project:

```powershell
cordova create CivicReport com.example.civicreport CivicReport
```

Enter the project:

```powershell
cd CivicReport
```

Add Android:

```powershell
cordova platform add android
```

Replace the generated Cordova `www` folder with the CivicReport frontend:

```text
frontend/www
```

The final Cordova structure should look similar to:

```text
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
```

---

# Android Permissions

The application may require permissions for:

- Internet access
- Geolocation
- Camera/photo access depending on how image selection is implemented

Cordova configuration should be updated appropriately before building the final APK.

During development, using HTTPS for the Flask API is recommended.

---

# Building the Android APK

After configuring the Cordova project:

```powershell
cordova build android
```

The generated Android application will normally be available somewhere under:

```text
platforms/android/app/build/outputs/apk/
```

The exact output path can vary depending on the Cordova/Android Gradle version.

---

# Development Architecture

During development:

```text
Browser / Cordova
       │
       │ HTTP
       ▼
Flask API
       │
       ▼
MySQL
```

Socket.IO provides the real-time communication channel:

```text
Flask
  │
  │ Socket.IO
  ▼
Connected Clients
```

---

# Production Architecture

The intended production architecture is:

```text
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
```

The Flask API can be deployed to a Python-compatible hosting provider.

The MySQL database can be hosted on a managed MySQL server.

---

# Security Considerations

The assessment version implements basic security practices.

These include:

- Password hashing
- Parameterized SQL queries
- Authentication
- Protected endpoints
- Input validation
- Image validation
- Safe uploaded filenames
- Environment variables for secrets

For production deployment, additional security measures should be considered, including:

- HTTPS
- Strong authentication/session management
- Rate limiting
- CSRF protection where applicable
- More advanced authorization
- Secure HTTP headers
- Production logging
- Database backups
- File storage security

---

# Future Improvements

The project can later be extended with:

- Push notifications
- Google Maps/OpenStreetMap integration
- Incident verification
- Admin dashboard
- Incident moderation
- User reporting/reputation system
- Incident status tracking
- Image cloud storage
- Email notifications
- Analytics
- Search
- Advanced filtering
- Offline reporting
- WordPress API integration

The current architecture intentionally keeps the frontend separated from the backend so that the API layer can be changed later without completely rebuilding the mobile interface.

---

# Assessment Objectives

CivicReport demonstrates the following skills:

## HTML5

- Semantic HTML
- Forms
- Navigation
- Inputs
- Buttons
- Modals
- Application structure

## CSS3

- Mobile-first design
- Responsive layouts
- Flexbox
- CSS Grid
- Form styling
- Cards
- Navigation
- Animations
- Responsive media queries

## JavaScript

- DOM manipulation
- Event handling
- Form validation
- Fetch API
- JSON
- API integration
- Geolocation
- Image preview
- Socket.IO
- Authentication state
- Dynamic UI rendering
- Notifications
- Local storage

## Python Flask

- REST API development
- Routing
- Authentication
- Password hashing
- MySQL integration
- Image uploads
- JSON responses
- Error handling
- Socket.IO
- API integration

## MySQL

- Database creation
- Tables
- Primary keys
- Foreign keys
- Relationships
- Indexes
- CRUD operations

## Cordova

- Cross-platform mobile development
- WebView-based mobile application
- Android packaging
- Device capabilities
- Geolocation
- API communication

---

# Application Flow

```text
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
```

---

# Author

**CivicReport**

Citizen Incident Reporting Solution

Developed as a Mobile App Development / Cross Platform Mobile Development assessment project.

---

# License

This project is intended for educational and assessment purposes.