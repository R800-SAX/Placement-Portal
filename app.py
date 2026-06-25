import os
from flask import Flask, session
from flask_login import LoginManager
from models import db, User, Company, Admin
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize db
    db.init_app(app)

    # Create upload directories
    os.makedirs(app.config['RESUME_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOGO_FOLDER'], exist_ok=True)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id_str):
        if not id_str:
            return None
        try:
            # Format: role_id (e.g. "student_1")
            role, user_id = id_str.split('_', 1)
            user_id = int(user_id)
            if role == 'student':
                return User.query.get(user_id)
            elif role == 'company':
                return Company.query.get(user_id)
            elif role == 'admin':
                return Admin.query.get(user_id)
        except Exception:
            return None
        return None

    # Context processor to make active user's role available in all templates
    @app.context_processor
    def inject_user_role():
        from flask_login import current_user
        role = None
        if current_user.is_authenticated:
            id_str = current_user.get_id()
            if id_str.startswith('student_'):
                role = 'student'
            elif id_str.startswith('company_'):
                role = 'company'
            elif id_str.startswith('admin_'):
                role = 'admin'
        return dict(current_user_role=role, current_year=2026)

    # Register blueprints
    from routes.main import main as main_blueprint
    from routes.auth import auth as auth_blueprint
    from routes.student import student as student_blueprint
    from routes.company import company as company_blueprint
    from routes.admin import admin as admin_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(student_blueprint, url_prefix='/student')
    app.register_blueprint(company_blueprint, url_prefix='/company')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    # Bind to all interfaces for local network and hostable access
    app.run(host='0.0.0.0', port=5000, debug=True)
