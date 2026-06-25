from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import db, JobPost, Company, User, ApplyJobPost

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Gather statistics for the premium hero page dashboard
    stats = {
        'students': User.query.filter_by(active=1).count(),
        'companies': Company.query.filter_by(active=1).count(),
        'jobs': JobPost.query.count(),
        'placed': ApplyJobPost.query.filter_by(status=1).count()
    }
    
    # Fetch 3 most recent jobs to display on the landing page
    recent_jobs = JobPost.query.order_by(JobPost.createdat.desc()).limit(3).all()
    return render_template('main/index.html', stats=stats, recent_jobs=recent_jobs)

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # In a real app we might store this in a contact inquiries table or send an email.
        # For now, flashing success is clean and works.
        flash(f'Thank you, {name}! Your message has been received. We will get back to you shortly.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('main/contact.html')

@main.route('/faq')
def faq():
    return render_template('main/faq.html')

@main.route('/jobs')
def jobs():
    search = request.args.get('search', '')
    query = JobPost.query
    
    if search:
        query = query.filter(
            (JobPost.jobtitle.ilike(f'%{search}%')) | 
            (JobPost.description.ilike(f'%{search}%')) |
            (JobPost.qualification.ilike(f'%{search}%'))
        )
        
    jobs_list = query.order_by(JobPost.createdat.desc()).all()
    return render_template('main/jobs.html', jobs=jobs_list, search=search)

@main.route('/api/chat', methods=['POST'])
def api_chat():
    from flask import jsonify, session
    from ai_engine import AIEngine
    
    data = request.get_json() or {}
    message = data.get('message', '')
    role = session.get('role')
    
    response_text = AIEngine.chatbot_response(message, role)
    return jsonify({'response': response_text})

