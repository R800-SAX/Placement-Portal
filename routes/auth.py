from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Company, Admin, State, City

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect authenticated user to their respective dashboard
        role = current_user.get_id().split('_')[0]
        return redirect(url_for(f'{role}.dashboard'))

    if request.method == 'POST':
        email_or_username = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') # 'student', 'company', or 'admin'

        if role == 'student':
            user = User.query.filter_by(email=email_or_username).first()
            if user and user.check_password(password):
                if user.active == 2:
                    flash('Your student account is pending approval by the Admin.', 'warning')
                elif user.active == 0:
                    flash('Your registration was rejected. Contact administrator.', 'danger')
                elif user.active == 1:
                    login_user(user)
                    session['role'] = 'student'
                    flash(f'Welcome back, {user.firstname}!', 'success')
                    return redirect(url_for('student.dashboard'))
            else:
                flash('Invalid student email or password.', 'danger')

        elif role == 'company':
            company = Company.query.filter_by(email=email_or_username).first()
            if company and company.check_password(password):
                if company.active == 2:
                    flash('Your Recruiter account is pending approval by the Admin.', 'warning')
                elif company.active == 0:
                    flash('Your registration was rejected by the placement cell.', 'danger')
                elif company.active == 1:
                    login_user(company)
                    session['role'] = 'company'
                    flash(f'Welcome back, {company.companyname} recruitment portal!', 'success')
                    return redirect(url_for('company.dashboard'))
            else:
                flash('Invalid recruiter email or password.', 'danger')

        elif role == 'admin':
            admin = Admin.query.filter_by(username=email_or_username).first()
            if admin and admin.check_password(password):
                login_user(admin)
                session['role'] = 'admin'
                flash('Logged in successfully as Administrator.', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid administrator credentials.', 'danger')

    return render_template('auth/login.html')

@auth.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Load states to populate the dropdown
    states = State.query.all()

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        contactno = request.form.get('contactno')
        address = request.form.get('address')
        state_id = request.form.get('state')
        city_id = request.form.get('city')
        qualification = request.form.get('qualification')
        stream = request.form.get('stream')
        passingyear = request.form.get('passingyear')
        dob = request.form.get('dob')
        age = request.form.get('age')
        skills = request.form.get('skills')
        hsc = request.form.get('hsc')
        ssc = request.form.get('ssc')
        ug = request.form.get('ug')
        pg = request.form.get('pg') or 0

        # Validations
        if password != cpassword:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register_student'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.register_student'))

        # Resolve state and city names
        state_obj = State.query.get(state_id) if state_id else None
        city_obj = City.query.get(city_id) if city_id else None
        state_name = state_obj.name if state_obj else ""
        city_name = city_obj.name if city_obj else ""

        # Create new student user
        new_student = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            address=address,
            city=city_name,
            state=state_name,
            contactno=contactno,
            qualification=qualification,
            stream=stream,
            passingyear=passingyear,
            dob=dob,
            age=age,
            skills=skills,
            hsc=hsc,
            ssc=int(ssc) if ssc else 0,
            ug=int(ug) if ug else 0,
            pg=int(pg) if pg else 0,
            active=2 # Pending admin approval
        )
        new_student.set_password(password)

        db.session.add(new_student)
        db.session.commit()

        flash('Student registration successful! Your account is pending Admin approval.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_student.html', states=states)

@auth.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    states = State.query.all()

    if request.method == 'POST':
        name = request.form.get('name') # HR contact name
        companyname = request.form.get('companyname')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        contactno = request.form.get('contactno')
        website = request.form.get('website')
        aboutme = request.form.get('aboutme')
        state_id = request.form.get('state')
        city_id = request.form.get('city')

        # Validations
        if password != cpassword:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register_company'))

        existing_comp = Company.query.filter_by(email=email).first()
        if existing_comp:
            flash('Email already registered by another company!', 'danger')
            return redirect(url_for('auth.register_company'))

        # Resolve state and city names
        state_obj = State.query.get(state_id) if state_id else None
        city_obj = City.query.get(city_id) if city_id else None
        state_name = state_obj.name if state_obj else ""
        city_name = city_obj.name if city_obj else ""

        # Create new company user
        new_company = Company(
            name=name,
            companyname=companyname,
            email=email,
            contactno=contactno,
            website=website,
            aboutme=aboutme,
            state=state_name,
            city=city_name,
            logo="default_logo.png",
            active=2 # Pending admin approval
        )
        new_company.set_password(password)

        db.session.add(new_company)
        db.session.commit()

        flash('Recruiter registration successful! Your account is pending Admin approval.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_company.html', states=states)

@auth.route('/api/cities/<int:state_id>')
def get_cities(state_id):
    cities = City.query.filter_by(state_id=state_id).order_by(City.name).all()
    return jsonify([{'id': c.id, 'name': c.name} for c in cities])

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    if 'role' in session:
        session.pop('role')
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.index'))
