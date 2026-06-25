import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Company, JobPost, ApplyJobPost, User, Mailbox, ReplyMailbox, Notice

company = Blueprint('company', __name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Decorator helper to check if logged in user is actually a company
def company_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        id_str = current_user.get_id()
        if not id_str or not id_str.startswith('company_'):
            flash('Access denied. Recruiter login required.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@company.route('/dashboard')
@login_required
@company_required
def dashboard():
    # Statistics
    posted_jobs_count = JobPost.query.filter_by(id_company=current_user.id_company).count()
    
    # Total candidates applied to jobs posted by this company
    applications_query = ApplyJobPost.query.filter_by(id_company=current_user.id_company)
    total_applicants = applications_query.count()
    pending_applicants = applications_query.filter_by(status=2).count()
    selected_candidates = applications_query.filter_by(status=1).count()

    # Recent applications
    recent_applications = applications_query.order_by(ApplyJobPost.id_apply.desc()).limit(5).all()

    # notices
    notices = Notice.query.filter(
        (Notice.audience == 'all') | (Notice.audience == 'companies')
    ).order_by(Notice.date.desc()).limit(3).all()

    return render_template(
        'company/dashboard.html',
        posted_jobs_count=posted_jobs_count,
        total_applicants=total_applicants,
        pending_applicants=pending_applicants,
        selected_candidates=selected_candidates,
        recent_applications=recent_applications,
        notices=notices
    )

@company.route('/profile', methods=['GET', 'POST'])
@login_required
@company_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.companyname = request.form.get('companyname')
        current_user.website = request.form.get('website')
        current_user.contactno = request.form.get('contactno')
        current_user.aboutme = request.form.get('aboutme')

        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                if allowed_file(file.filename, current_app.config['ALLOWED_LOGO_EXTENSIONS']):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"company_{current_user.id_company}_logo.{ext}"
                    filepath = os.path.join(current_app.config['LOGO_FOLDER'], filename)
                    file.save(filepath)
                    current_user.logo = filename
                else:
                    flash('Invalid image format. Allowed: PNG, JPG, JPEG, GIF.', 'danger')
                    return redirect(url_for('company.profile'))

        db.session.commit()
        flash('Company profile updated successfully!', 'success')
        return redirect(url_for('company.profile'))

    return render_template('company/profile.html')

@company.route('/jobs', methods=['GET'])
@login_required
@company_required
def manage_jobs():
    jobs = JobPost.query.filter_by(id_company=current_user.id_company).order_by(JobPost.createdat.desc()).all()
    return render_template('company/job_posts.html', jobs=jobs)

@company.route('/jobs/new', methods=['GET', 'POST'])
@login_required
@company_required
def create_job():
    if request.method == 'POST':
        jobtitle = request.form.get('jobtitle')
        description = request.form.get('description')
        minimumsalary = request.form.get('minimumsalary')
        maximumsalary = request.form.get('maximumsalary')
        experience = request.form.get('experience')
        qualification = request.form.get('qualification')

        new_job = JobPost(
            id_company=current_user.id_company,
            jobtitle=jobtitle,
            description=description,
            minimumsalary=minimumsalary,
            maximumsalary=maximumsalary,
            experience=experience,
            qualification=qualification
        )
        db.session.add(new_job)
        db.session.commit()

        flash('Job opening posted successfully!', 'success')
        return redirect(url_for('company.manage_jobs'))

    return render_template('company/job_create.html')

@company.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
@company_required
def edit_job(job_id):
    job = JobPost.query.filter_by(id_jobpost=job_id, id_company=current_user.id_company).first_or_404()
    
    if request.method == 'POST':
        job.jobtitle = request.form.get('jobtitle')
        job.description = request.form.get('description')
        job.minimumsalary = request.form.get('minimumsalary')
        job.maximumsalary = request.form.get('maximumsalary')
        job.experience = request.form.get('experience')
        job.qualification = request.form.get('qualification')

        db.session.commit()
        flash('Job posting updated successfully!', 'success')
        return redirect(url_for('company.manage_jobs'))

    return render_template('company/job_edit.html', job=job)

@company.route('/jobs/delete/<int:job_id>', methods=['POST'])
@login_required
@company_required
def delete_job(job_id):
    job = JobPost.query.filter_by(id_jobpost=job_id, id_company=current_user.id_company).first_or_404()
    db.session.delete(job)
    db.session.commit()
    flash('Job posting deleted successfully.', 'success')
    return redirect(url_for('company.manage_jobs'))

@company.route('/applicants')
@login_required
@company_required
def view_applicants():
    # View all applicants for jobs posted by this company
    applications = ApplyJobPost.query.filter_by(id_company=current_user.id_company).order_by(ApplyJobPost.id_apply.desc()).all()
    return render_template('company/applicants.html', applications=applications)

@company.route('/application/<int:app_id>/status/<int:status_code>', methods=['POST'])
@login_required
@company_required
def change_status(app_id, status_code):
    # status_code: 1 = Selected, 0 = Rejected, 3 = Under Review, 2 = Pending
    application = ApplyJobPost.query.filter_by(id_apply=app_id, id_company=current_user.id_company).first_or_404()
    application.status = status_code
    db.session.commit()
    
    status_label = {1: "Selected", 0: "Rejected", 3: "Under Review", 2: "Pending"}.get(status_code, "Updated")
    flash(f"Candidate application status updated to '{status_label}'", 'success')
    return redirect(url_for('company.view_applicants'))

@company.route('/mailbox', methods=['GET', 'POST'])
@login_required
@company_required
def mailbox():
    # Load list of candidates who have applied to their jobs to message them
    # Fetch student users who have application history with this company
    applied_users = db.session.query(User).join(ApplyJobPost).filter(ApplyJobPost.id_company == current_user.id_company).distinct().all()

    if request.method == 'POST':
        to_user_id = request.form.get('to_user')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if to_user_id == "admin":
            dest_id = 1
            dest_role = "admin"
        else:
            dest_id = int(to_user_id)
            dest_role = "student"

        new_mail = Mailbox(
            id_fromuser=current_user.id_company,
            fromuser=f"{current_user.companyname} HR Portal ({current_user.email})",
            id_touser=dest_id,
            touser=dest_role,
            subject=subject,
            message=message
        )
        db.session.add(new_mail)
        db.session.commit()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('company.mailbox'))

    # Load messages
    inbox = Mailbox.query.filter_by(touser='company', id_touser=current_user.id_company).order_by(Mailbox.createdAt.desc()).all()
    outbox = Mailbox.query.filter_by(id_fromuser=current_user.id_company, fromuser=f"{current_user.companyname} HR Portal ({current_user.email})").order_by(Mailbox.createdAt.desc()).all()

    # Load selected thread
    thread_id = request.args.get('thread_id')
    active_mail = None
    if thread_id:
        active_mail = Mailbox.query.get(int(thread_id))
        # Safety check: company must be sender or recipient
        if active_mail:
            is_recipient = (active_mail.touser == 'company' and active_mail.id_touser == current_user.id_company)
            is_sender = (active_mail.id_fromuser == current_user.id_company and active_mail.fromuser == f"{current_user.companyname} HR Portal ({current_user.email})")
            if not (is_recipient or is_sender):
                active_mail = None

    return render_template('company/mailbox.html', students=applied_users, inbox=inbox, outbox=outbox, active_mail=active_mail)

@company.route('/mailbox/reply/<int:mail_id>', methods=['POST'])
@login_required
@company_required
def reply_mailbox(mail_id):
    mail = Mailbox.query.get_or_404(mail_id)
    message = request.form.get('message')

    if message:
        reply = ReplyMailbox(
            id_mailbox=mail.id_mailbox,
            id_user=current_user.id_company,
            usertype="company",
            message=message
        )
        db.session.add(reply)
        db.session.commit()
        flash('Reply sent!', 'success')

    return redirect(url_for('company.mailbox'))
