from .auth import auth_bp
from .incidents import incidents_bp
from .categories import categories_bp
from .users import users_bp
from .reports import reports_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')