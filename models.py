from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(255), nullable=True)
    contactno = db.Column(db.String(255), nullable=True)
    qualification = db.Column(db.String(255), nullable=True)
    stream = db.Column(db.String(255), nullable=True)
    passingyear = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.String(255), nullable=True)
    age = db.Column(db.String(255), nullable=True)
    designation = db.Column(db.String(255), nullable=True)
    resume = db.Column(db.String(255), nullable=True)
    hash = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Integer, nullable=False, default=2) # 2 = Pending, 1 = Active, 0 = Rejected
    aboutme = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    hsc = db.Column(db.String(200), nullable=True)
    ssc = db.Column(db.Integer, nullable=True)
    ug = db.Column(db.Integer, nullable=True)
    pg = db.Column(db.Integer, nullable=True)

    # Relationships
    applications = db.relationship('ApplyJobPost', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password_str):
        self.password = generate_password_hash(password_str)
        
    def check_password(self, password_str):
        if self.password.startswith('pbkdf2:') or self.password.startswith('scrypt:'):
            return check_password_hash(self.password, password_str)
        # Fallback for plain text password comparison if matching seed data (e.g. '123456')
        return self.password == password_str

    def get_id(self):
        return f"student_{self.id_user}"

    @property
    def is_active(self):
        # Allow logins only for approved users (active = 1)
        return self.active == 1


class Company(db.Model, UserMixin):
    __tablename__ = 'company'
    
    id_company = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False) # Contact Person Name
    companyname = db.Column(db.String(255), nullable=False) # Company Name
    country = db.Column(db.String(255), nullable=False, default="India")
    state = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    contactno = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    aboutme = db.Column(db.String(255), nullable=True)
    logo = db.Column(db.String(255), nullable=True)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Integer, nullable=False, default=2) # 2 = Pending, 1 = Active, 0 = Rejected

    # Relationships
    job_posts = db.relationship('JobPost', backref='company', lazy=True, cascade="all, delete-orphan")
    applications = db.relationship('ApplyJobPost', backref='company', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password_str):
        self.password = generate_password_hash(password_str)
        
    def check_password(self, password_str):
        if self.password.startswith('pbkdf2:') or self.password.startswith('scrypt:'):
            return check_password_hash(self.password, password_str)
        return self.password == password_str

    def get_id(self):
        return f"company_{self.id_company}"

    @property
    def is_active(self):
        return self.active == 1


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    
    id_admin = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password_str):
        self.password = generate_password_hash(password_str)
        
    def check_password(self, password_str):
        if self.password.startswith('pbkdf2:') or self.password.startswith('scrypt:'):
            return check_password_hash(self.password, password_str)
        return self.password == password_str

    def get_id(self):
        return f"admin_{self.id_admin}"


class JobPost(db.Model):
    __tablename__ = 'job_post'
    
    id_jobpost = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_company = db.Column(db.Integer, db.ForeignKey('company.id_company'), nullable=False)
    jobtitle = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    minimumsalary = db.Column(db.String(255), nullable=False)
    maximumsalary = db.Column(db.String(255), nullable=False)
    experience = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(255), nullable=False)
    createdat = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('ApplyJobPost', backref='job_post', lazy=True, cascade="all, delete-orphan")


class ApplyJobPost(db.Model):
    __tablename__ = 'apply_job_post'
    
    id_apply = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_jobpost = db.Column(db.Integer, db.ForeignKey('job_post.id_jobpost'), nullable=False)
    id_company = db.Column(db.Integer, db.ForeignKey('company.id_company'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=2) # 2 = Applied/Pending, 1 = Selected, 0 = Rejected, 3 = Under Review


class Notice(db.Model):
    __tablename__ = 'notice'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(250), nullable=False)
    notice = db.Column(db.Text, nullable=True)
    audience = db.Column(db.String(255), nullable=True) # "all", "students", "companies"
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Mailbox(db.Model):
    __tablename__ = 'mailbox'
    
    id_mailbox = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_fromuser = db.Column(db.Integer, nullable=False) # User ID who sent
    fromuser = db.Column(db.String(255), nullable=False) # Sender's role/name/email description
    id_touser = db.Column(db.Integer, nullable=False) # Recipient ID
    touser = db.Column(db.String(255), nullable=False, default="company") # "student", "company", "admin"
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    replies = db.relationship('ReplyMailbox', backref='mailbox', lazy=True, cascade="all, delete-orphan")


class ReplyMailbox(db.Model):
    __tablename__ = 'reply_mailbox'
    
    id_reply = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_mailbox = db.Column(db.Integer, db.ForeignKey('mailbox.id_mailbox'), nullable=False)
    id_user = db.Column(db.Integer, nullable=False) # User ID who replies
    usertype = db.Column(db.String(255), nullable=False) # Sender role: "student", "company", "admin"
    message = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Country(db.Model):
    __tablename__ = 'countries'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sortname = db.Column(db.String(3), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phonecode = db.Column(db.Integer, nullable=False)


class State(db.Model):
    __tablename__ = 'states'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    country_id = db.Column(db.Integer, nullable=False, default=1)


class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    state_id = db.Column(db.Integer, nullable=False)
