import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, JobPost, ApplyJobPost, Notice, Mailbox, ReplyMailbox, Company

student = Blueprint('student', __name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Decorator helper to check if logged in user is actually a student
def student_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        id_str = current_user.get_id()
        if not id_str or not id_str.startswith('student_'):
            flash('Access denied. Candidate login required.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    from ai_engine import AIEngine

    # Statistics
    applied_count = ApplyJobPost.query.filter_by(id_user=current_user.id_user).count()
    active_jobs = JobPost.query.count()
    
    # Fetch student-relevant notices (audience='all' or audience='students')
    notices = Notice.query.filter(
        (Notice.audience == 'all') | (Notice.audience == 'students')
    ).order_by(Notice.date.desc()).all()
    
    # Calculate profile completeness
    fields = [
        current_user.address, current_user.city, current_user.state, 
        current_user.contactno, current_user.qualification, current_user.stream,
        current_user.passingyear, current_user.skills, current_user.resume,
        current_user.hsc, current_user.ssc, current_user.ug
    ]
    filled_fields = sum(1 for f in fields if f)
    completeness = int((filled_fields / len(fields)) * 100)

    # Recent job applications
    applications = ApplyJobPost.query.filter_by(id_user=current_user.id_user).order_by(ApplyJobPost.id_apply.desc()).limit(5).all()

    # AI Sector Classifications
    ai_sector, ai_confidence, _ = AIEngine.classify_student(current_user)

    # AI Job Recommendations
    all_jobs = JobPost.query.all()
    job_recommendations = []
    
    # Exclude already applied jobs
    applied_job_ids = {app.id_jobpost for app in ApplyJobPost.query.filter_by(id_user=current_user.id_user).all()}
    
    for job in all_jobs:
        if job.id_jobpost in applied_job_ids:
            continue
        match_details = AIEngine.match_job_for_student(current_user, job)
        job_recommendations.append({
            'job': job,
            'score': match_details['score'],
            'matched_skills': match_details['matched_skills'],
            'missing_skills': match_details['missing_skills'],
            'message': match_details['message']
        })
    # Sort recommendations by matching score descending
    job_recommendations.sort(key=lambda x: x['score'], reverse=True)
    recommended_jobs = job_recommendations[:3]

    return render_template(
        'student/dashboard.html', 
        applied_count=applied_count, 
        active_jobs=active_jobs,
        notices=notices,
        completeness=completeness,
        applications=applications,
        ai_sector=ai_sector,
        ai_confidence=ai_confidence,
        recommended_jobs=recommended_jobs
    )

@student.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    if request.method == 'POST':
        # Update text details
        current_user.firstname = request.form.get('firstname')
        current_user.lastname = request.form.get('lastname')
        current_user.address = request.form.get('address')
        current_user.contactno = request.form.get('contactno')
        current_user.qualification = request.form.get('qualification')
        current_user.stream = request.form.get('stream')
        current_user.passingyear = request.form.get('passingyear')
        current_user.dob = request.form.get('dob')
        current_user.age = request.form.get('age')
        current_user.skills = request.form.get('skills')
        current_user.aboutme = request.form.get('aboutme')
        current_user.hsc = request.form.get('hsc')
        current_user.ssc = int(request.form.get('ssc') or 0)
        current_user.ug = int(request.form.get('ug') or 0)
        current_user.pg = int(request.form.get('pg') or 0)

        # Handle resume file upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                if allowed_file(file.filename, current_app.config['ALLOWED_RESUME_EXTENSIONS']):
                    # Secure file name: student_ID_resume.pdf
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"student_{current_user.id_user}_resume.{ext}"
                    filepath = os.path.join(current_app.config['RESUME_FOLDER'], filename)
                    file.save(filepath)
                    current_user.resume = filename
                else:
                    flash('Invalid file format. Please upload PDF, DOC, or DOCX.', 'danger')
                    return redirect(url_for('student.profile'))

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html')

@student.route('/apply/<int:job_id>')
@login_required
@student_required
def apply(job_id):
    # Verify user has uploaded a resume first
    if not current_user.resume:
        flash('Please upload your resume in the Profile section before applying to jobs.', 'warning')
        return redirect(url_for('student.profile'))

    # Check if job exists
    job = JobPost.query.get_or_404(job_id)
    
    # Check if already applied
    already_applied = ApplyJobPost.query.filter_by(
        id_jobpost=job_id, 
        id_user=current_user.id_user
    ).first()
    
    if already_applied:
        flash('You have already applied for this job!', 'info')
        return redirect(url_for('student.applied_jobs'))

    # Create job application
    new_app = ApplyJobPost(
        id_jobpost=job_id,
        id_company=job.id_company,
        id_user=current_user.id_user,
        status=2 # Applied/Pending
    )
    db.session.add(new_app)
    db.session.commit()
    
    flash(f'Successfully applied for {job.jobtitle}!', 'success')
    return redirect(url_for('student.applied_jobs'))

@student.route('/applied-jobs')
@login_required
@student_required
def applied_jobs():
    applications = ApplyJobPost.query.filter_by(id_user=current_user.id_user).order_by(ApplyJobPost.id_apply.desc()).all()
    return render_template('student/applied_jobs.html', applications=applications)

@student.route('/mailbox', methods=['GET', 'POST'])
@login_required
@student_required
def mailbox():
    # Load all recruiters for new message dropdown
    companies = Company.query.filter_by(active=1).all()
    
    if request.method == 'POST':
        # Send new message
        to_company_id = request.form.get('to_company')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if to_company_id == "admin":
            dest_id = 1 # Admin ID is 1
            dest_role = "admin"
        else:
            dest_id = int(to_company_id)
            dest_role = "company"
            
        new_mail = Mailbox(
            id_fromuser=current_user.id_user,
            fromuser=f"{current_user.firstname} {current_user.lastname} ({current_user.email})",
            id_touser=dest_id,
            touser=dest_role,
            subject=subject,
            message=message
        )
        db.session.add(new_mail)
        db.session.commit()
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('student.mailbox'))

    # Load messages
    # Inbox: messages addressed to student role and student ID
    inbox = Mailbox.query.filter_by(touser='student', id_touser=current_user.id_user).order_by(Mailbox.createdAt.desc()).all()
    # Outbox: messages sent by student ID and role
    outbox = Mailbox.query.filter_by(id_fromuser=current_user.id_user, fromuser=f"{current_user.firstname} {current_user.lastname} ({current_user.email})").order_by(Mailbox.createdAt.desc()).all()
    
    # Load selected thread
    thread_id = request.args.get('thread_id')
    active_mail = None
    if thread_id:
        active_mail = Mailbox.query.get(int(thread_id))
        # Safety check: student must be sender or recipient of this thread
        if active_mail:
            is_recipient = (active_mail.touser == 'student' and active_mail.id_touser == current_user.id_user)
            is_sender = (active_mail.id_fromuser == current_user.id_user and active_mail.fromuser == f"{current_user.firstname} {current_user.lastname} ({current_user.email})")
            if not (is_recipient or is_sender):
                active_mail = None
    
    return render_template('student/mailbox.html', companies=companies, inbox=inbox, outbox=outbox, active_mail=active_mail)

@student.route('/mailbox/reply/<int:mail_id>', methods=['POST'])
@login_required
@student_required
def reply_mailbox(mail_id):
    mail = Mailbox.query.get_or_404(mail_id)
    message = request.form.get('message')
    
    if message:
        reply = ReplyMailbox(
            id_mailbox=mail.id_mailbox,
            id_user=current_user.id_user,
            usertype="student",
            message=message
        )
        db.session.add(reply)
        db.session.commit()
        flash('Reply sent!', 'success')
        
    return redirect(url_for('student.mailbox'))
