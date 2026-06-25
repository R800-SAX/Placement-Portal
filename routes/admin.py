from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Company, JobPost, ApplyJobPost, Notice

admin = Blueprint('admin', __name__)

# Decorator helper to check if logged in user is admin
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        id_str = current_user.get_id()
        if not id_str or not id_str.startswith('admin_'):
            flash('Access denied. Administrator login required.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Statistics
    stats = {
        'total_students': User.query.count(),
        'total_companies': Company.query.count(),
        'total_jobs': JobPost.query.count(),
        'total_applications': ApplyJobPost.query.count(),
        'pending_students': User.query.filter_by(active=2).count(),
        'pending_companies': Company.query.filter_by(active=2).count()
    }

    # Pending User Approvals (limit to 5 in dashboard view)
    pending_students_list = User.query.filter_by(active=2).order_by(User.id_user.desc()).limit(5).all()
    pending_companies_list = Company.query.filter_by(active=2).order_by(Company.id_company.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        pending_students=pending_students_list,
        pending_companies=pending_companies_list
    )

@admin.route('/students')
@login_required
@admin_required
def manage_students():
    ai_category = request.args.get('ai_category', '')
    all_students = User.query.order_by(User.id_user.desc()).all()
    
    from ai_engine import AIEngine
    for s in all_students:
        sector, confidence, _ = AIEngine.classify_student(s)
        s.ai_sector = sector
        s.ai_confidence = confidence
        s.ai_verify = AIEngine.cross_verify_student(s)
        
    if ai_category:
        filtered_students = [s for s in all_students if s.ai_sector == ai_category]
    else:
        filtered_students = all_students
        
    return render_template('admin/students.html', students=filtered_students, selected_category=ai_category)

@admin.route('/students/<int:user_id>/status/<int:status_code>', methods=['POST'])
@login_required
@admin_required
def change_student_status(user_id, status_code):
    # status_code: 1 = Approve/Active, 0 = Reject, 2 = Pending
    student_user = User.query.get_or_404(user_id)
    student_user.active = status_code
    db.session.commit()

    status_label = {1: "Approved", 0: "Rejected", 2: "Pending"}.get(status_code, "Updated")
    flash(f"Student account '{student_user.firstname} {student_user.lastname}' is now {status_label}.", 'success')
    return redirect(request.referrer or url_for('admin.manage_students'))

@admin.route('/students/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(user_id):
    student_user = User.query.get_or_404(user_id)
    db.session.delete(student_user)
    db.session.commit()
    flash(f"Student account deleted successfully.", 'success')
    return redirect(request.referrer or url_for('admin.manage_students'))

@admin.route('/companies')
@login_required
@admin_required
def manage_companies():
    companies_list = Company.query.order_by(Company.id_company.desc()).all()
    return render_template('admin/companies.html', companies=companies_list)

@admin.route('/companies/<int:company_id>/status/<int:status_code>', methods=['POST'])
@login_required
@admin_required
def change_company_status(company_id, status_code):
    comp = Company.query.get_or_404(company_id)
    comp.active = status_code
    db.session.commit()

    status_label = {1: "Approved", 0: "Rejected", 2: "Pending"}.get(status_code, "Updated")
    flash(f"Recruiter account '{comp.companyname}' is now {status_label}.", 'success')
    return redirect(request.referrer or url_for('admin.manage_companies'))

@admin.route('/companies/<int:company_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_company(company_id):
    comp = Company.query.get_or_404(company_id)
    db.session.delete(comp)
    db.session.commit()
    flash(f"Recruiter account deleted successfully.", 'success')
    return redirect(request.referrer or url_for('admin.manage_companies'))

@admin.route('/notices', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_notices():
    if request.method == 'POST':
        subject = request.form.get('subject')
        notice_text = request.form.get('notice')
        audience = request.form.get('audience') # 'all', 'students', 'companies'

        new_notice = Notice(
            subject=subject,
            notice=notice_text,
            audience=audience,
            date=datetime.utcnow()
        )
        db.session.add(new_notice)
        db.session.commit()

        flash('Notice published successfully!', 'success')
        return redirect(url_for('admin.manage_notices'))

    notices_list = Notice.query.order_by(Notice.date.desc()).all()
    return render_template('admin/notices.html', notices=notices_list)

@admin.route('/notices/<int:notice_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_notice(notice_id):
    n = Notice.query.get_or_404(notice_id)
    db.session.delete(n)
    db.session.commit()
    flash('Notice deleted successfully.', 'success')
    return redirect(url_for('admin.manage_notices'))

@admin.route('/jobs')
@login_required
@admin_required
def manage_jobs():
    jobs_list = JobPost.query.order_by(JobPost.createdat.desc()).all()
    return render_template('admin/jobs.html', jobs=jobs_list)

@admin.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_job(job_id):
    job = JobPost.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job posting removed.', 'success')
    return redirect(url_for('admin.manage_jobs'))

@admin.route('/ai-insights')
@login_required
@admin_required
def ai_insights():
    from ai_engine import AIEngine
    
    students = User.query.filter_by(active=1).all()
    jobs = JobPost.query.all()
    
    ai_results = AIEngine.analyze_talent_gap(students, jobs)
    
    # Render view passing stats
    return render_template(
        'admin/ai_insights.html',
        insights=ai_results['insights'],
        suggestions=ai_results['suggestions'],
        student_counts=ai_results['student_counts'],
        job_counts=ai_results['job_counts'],
        total_students=len(students),
        total_jobs=len(jobs)
    )
