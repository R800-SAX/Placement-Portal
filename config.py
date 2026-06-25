import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-placement-portal-1298471204'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'placement_portal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configurations
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, 'logos')
    
    # 16 Megabytes max upload size
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Allowed file extensions
    ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}
    ALLOWED_LOGO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
