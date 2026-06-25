import re

class AIEngine:
    SECTORS = {
        'Software Engineering': [
            'python', 'java', 'c++', 'c#', 'c', 'backend', 'algorithms', 'data structures', 
            'dsa', 'system design', 'oop', 'threading', 'git', 'compiler', 'assembly', 'linux'
        ],
        'Web Development': [
            'html', 'css', 'javascript', 'js', 'react', 'angular', 'vue', 'nodejs', 'node', 
            'django', 'flask', 'php', 'bootstrap', 'tailwind', 'front-end', 'frontend', 
            'fullstack', 'full-stack', 'web development', 'jquery', 'bootstrap'
        ],
        'Data Science & ML': [
            'data science', 'machine learning', 'ml', 'ai', 'deep learning', 'nlp', 'pandas', 
            'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'sql', 'tableau', 'powerbi', 
            'analytics', 'statistics', 'matplotlib', 'r', 'data analyst'
        ],
        'Core Engineering': [
            'vlsi', 'embedded systems', 'circuits', 'iot', 'robotics', 'matlab', 'cad', 
            'hardware', 'signal processing', 'microcontroller', 'electrical', 'mechanical'
        ],
        'Management & Product': [
            'product management', 'business analyst', 'finance', 'consulting', 'marketing', 
            'project management', 'agile', 'scrum', 'sales', 'operations', 'deloitte'
        ]
    }
    
    SECTOR_MOCK_COMPANIES = {
        'Software Engineering': ['Google', 'Microsoft', 'Amazon', 'Adobe', 'Oracle'],
        'Web Development': ['Wipro', 'Cognizant', 'TCS', 'Infosys', 'Capgemini'],
        'Data Science & ML': ['NVIDIA', 'Meta', 'Tiger Analytics', 'Fractal Analytics', 'Mu Sigma'],
        'Core Engineering': ['Intel', 'Qualcomm', 'Texas Instruments', 'AMD', 'GE'],
        'Management & Product': ['Deloitte', 'McKinsey & Company', 'BCG', 'KPMG', 'EY']
    }

    @classmethod
    def classify_student(cls, student):
        """
        Analyzes a student's skills, stream, and bio to categorize them into one of the key sectors.
        Returns: (Primary Sector, Confidence Score %, Extracted Skills List)
        """
        # Combine student content for analysis
        search_text = " ".join([
            (student.skills or "").lower(),
            (student.stream or "").lower(),
            (student.aboutme or "").lower(),
            (student.qualification or "").lower()
        ])
        
        # Clean text
        search_text = re.sub(r'[^a-z0-9\s,&#+-]', '', search_text)
        
        # Calculate scores per sector
        scores = {sector: 0 for sector in cls.SECTORS}
        matched_words = {sector: [] for sector in cls.SECTORS}
        
        for sector, keywords in cls.SECTORS.items():
            for kw in keywords:
                # Count keyword matches, giving extra weight if it appears in skills
                weight = 3 if kw in (student.skills or "").lower() else 1
                matches = len(re.findall(r'\b' + re.escape(kw) + r'\b', search_text))
                if matches > 0:
                    scores[sector] += matches * weight
                    matched_words[sector].append(kw)
                    
        # Expose skills list
        skills_list = [s.strip() for s in (student.skills or "").split(",") if s.strip()]
        
        # Choose sector
        total_score = sum(scores.values())
        if total_score == 0:
            # Fallback on stream mapping
            stream = (student.stream or "").lower()
            if "information" in stream or "computer" in stream:
                return 'Software Engineering', 80, skills_list
            elif "electronics" in stream or "electrical" in stream or "mechanical" in stream:
                return 'Core Engineering', 80, skills_list
            else:
                return 'Software Engineering', 50, skills_list
                
        max_sector = max(scores, key=scores.get)
        confidence = int((scores[max_sector] / total_score) * 100)
        
        # Cap minimum confidence at 50%
        confidence = max(confidence, 50)
        
        return max_sector, confidence, skills_list

    @classmethod
    def classify_job(cls, job):
        """
        Analyzes a job post title and description to classify it into one of the key sectors.
        """
        search_text = " ".join([
            job.jobtitle.lower(),
            job.description.lower(),
            job.qualification.lower()
        ])
        
        scores = {sector: 0 for sector in cls.SECTORS}
        for sector, keywords in cls.SECTORS.items():
            for kw in keywords:
                matches = len(re.findall(r'\b' + re.escape(kw) + r'\b', search_text))
                if matches > 0:
                    scores[sector] += matches
                    
        total_score = sum(scores.values())
        if total_score == 0:
            # Fallback on title checks
            title = job.jobtitle.lower()
            if "web" in title or "frontend" in title or "full" in title:
                return 'Web Development'
            elif "data" in title or "analytics" in title or "ml" in title:
                return 'Data Science & ML'
            elif "hardware" in title or "embedded" in title:
                return 'Core Engineering'
            elif "manager" in title or "consultant" in title:
                return 'Management & Product'
            return 'Software Engineering'
            
        return max(scores, key=scores.get)

    @classmethod
    def match_job_for_student(cls, student, job):
        """
        Computes the matching coefficient (0-100%) between a student and a job opening.
        Returns a breakdown dict.
        """
        student_skills = [s.strip().lower() for s in (student.skills or "").split(",") if s.strip()]
        if not student_skills:
            return {'score': 0, 'matched_skills': [], 'missing_skills': [], 'message': 'No skills defined in profile.'}
            
        job_desc = job.description.lower() + " " + job.jobtitle.lower()
        
        matched_skills = []
        missing_skills = []
        
        for skill in student_skills:
            # Simple word boundary or literal match
            if skill in job_desc:
                matched_skills.append(skill.title())
            else:
                missing_skills.append(skill.title())
                
        # Calculate score base
        match_ratio = len(matched_skills) / len(student_skills)
        score = int(match_ratio * 100)
        
        # Add qualifications match bonus (up to 15%)
        qual_bonus = 0
        if student.qualification and job.qualification:
            if student.qualification.strip().lower() in job.qualification.strip().lower():
                qual_bonus = 15
        
        final_score = min(score + qual_bonus, 100)
        
        # Custom message
        if final_score >= 80:
            message = "Excellent Match! Your skills strongly align with this role's requirements."
        elif final_score >= 60:
            message = "Good Match. Consider highlighting matching skills in your application."
        else:
            message = "Potential Match. You may need to acquire additional skills outlined in this drive."
            
        return {
            'score': final_score,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'message': message
        }

    @classmethod
    def analyze_talent_gap(cls, students, jobs):
        """
        Compares candidate talent distribution against active job drives.
        Generates invitations suggestions.
        """
        student_counts = {sector: 0 for sector in cls.SECTORS}
        job_counts = {sector: 0 for sector in cls.SECTORS}
        
        # Classify students
        for s in students:
            sector, _, _ = cls.classify_student(s)
            student_counts[sector] += 1
            
        # Classify jobs
        for j in jobs:
            sector = cls.classify_job(j)
            job_counts[sector] += 1
            
        total_students = len(students)
        total_jobs = len(jobs)
        
        insights = []
        suggestions = []
        
        for sector in cls.SECTORS:
            s_count = student_counts[sector]
            j_count = job_counts[sector]
            
            s_pct = int((s_count / total_students * 100)) if total_students > 0 else 0
            j_pct = int((j_count / total_jobs * 100)) if total_jobs > 0 else 0
            
            # Gap detection
            gap = s_pct - j_pct
            
            status = "Balanced"
            if gap > 15: # High surplus of talent
                status = "Talent Surplus / Job Shortage"
                # Suggest companies to invite
                companies = cls.SECTOR_MOCK_COMPANIES[sector]
                suggestions.append({
                    'sector': sector,
                    'unaligned_candidates': s_count,
                    'surplus_percentage': gap,
                    'companies_to_invite': companies,
                    'action': f"Invite {sector} recruiters (e.g. {', '.join(companies[:3])}) to capture the surplus talent pool."
                })
            elif gap < -15:
                status = "Job Surplus / Talent Shortage"
                
            insights.append({
                'sector': sector,
                'student_count': s_count,
                'job_count': j_count,
                'student_percentage': s_pct,
                'job_percentage': j_pct,
                'gap': gap,
                'status': status
            })
            
        return {
            'insights': insights,
            'suggestions': suggestions,
            'student_counts': student_counts,
            'job_counts': job_counts
        }

    # Mock Official Registry Database (ERP/College Admin records)
    OFFICIAL_STUDENT_REGISTRY = {
        'student@example.com': {
            'ssc': 80,
            'hsc': '82%',
            'ug': 82
        },
        'jatin@gmail.com': {
            'ssc': 88,
            'hsc': '90%',
            'ug': 84
        },
        'john@example.com': {
            # Claims ssc=72, hsc=75, ug=75. Let's make registry show different values to flag mismatch!
            'ssc': 70,
            'hsc': '72%',
            'ug': 70
        }
    }

    @classmethod
    def cross_verify_student(cls, student):
        """
        Cross-checks student academic fields (SSC, HSC, UG) with college official records.
        """
        record = cls.OFFICIAL_STUDENT_REGISTRY.get(student.email)
        if not record:
            return {'status': 'No Record Found', 'matched': False}
            
        ssc_match = (student.ssc == record['ssc'])
        
        # Clean percentage signs for comparison
        hsc_profile = re.sub(r'[^0-9]', '', str(student.hsc or ''))
        hsc_record = re.sub(r'[^0-9]', '', str(record['hsc'] or ''))
        hsc_match = (hsc_profile == hsc_record)
        
        ug_match = (student.ug == record['ug'])
        
        all_matched = ssc_match and hsc_match and ug_match
        
        return {
            'status': 'Verified' if all_matched else 'Mismatch Found',
            'matched': all_matched,
            'ssc': {'profile': student.ssc, 'official': record['ssc'], 'match': ssc_match},
            'hsc': {'profile': student.hsc, 'official': record['hsc'], 'match': hsc_match},
            'ug': {'profile': student.ug, 'official': record['ug'], 'match': ug_match}
        }

    @classmethod
    def chatbot_response(cls, message, role=None):
        """
        Intelligent local NLP matcher to resolve questions about the PlaceTrack AI portal.
        """
        msg = (message or "").lower().strip()
        
        if "resume" in msg or "cv" in msg or "upload" in msg:
            return "To upload or update your resume, go to 'My Profile' in the sidebar menu and scroll to the bottom. We support PDF, DOC, and DOCX formats up to 16MB. Ensure that your CGPA and details match before uploading."
            
        if "apply" in msg or "job" in msg or "post" in msg or "drive" in msg:
            if role == "company":
                return "To create a job drive, go to 'Manage Jobs' in the sidebar and click 'Post Job Drive'. Fill in the salary, experience, qualification requirements, and description to publish it."
            return "To apply for an opening, navigate to the 'Job Board' page, search for drives, and click 'Apply Now'. Ensure you have uploaded your resume first in your profile settings."
            
        if "verify" in msg or "erp" in msg or "mismatch" in msg or "crosscheck" in msg or "marks" in msg:
            return "PlaceTrack AI includes an ERP Database Crosscheck. Administrators can expand a candidate's profile in the Candidates Directory to view a detailed verification report highlighting any mismatches between claimed and official registry marks (SSC, HSC, UG)."
            
        if "insights" in msg or "gap" in msg or "invite" in msg or "analytics" in msg or "surplus" in msg:
            return "The AI Insights Dashboard maps graduating student skill sectors against active recruiter job drives. If a talent surplus is detected, it suggests specific industry leaders to invite (e.g. NVIDIA for Data Science, Texas Instruments for Core VLSI) and lets you trigger invitations."
            
        if "active" in msg or "approve" in msg or "pending" in msg:
            return "New candidate and recruiter registrations require administrator approval before login. Once the admin changes the account status to Active in the Candidate or Recruiter logs, users can sign in using their registered email."
            
        if "placetrack" in msg or "what is" in msg or "portal" in msg:
            return "PlaceTrack AI is an intelligent placement cell coordinator platform that connects candidates with corporate recruiters and automates talent gap analysis, ERP registry verification, and role matching."
            
        if "message" in msg or "chat" in msg or "mailbox" in msg or "inbox" in msg:
            return "You can use the Message Center (Mailbox) in the sidebar menu to start text chats, request interview slots, or ask questions to recruiters, candidates, or administrators."
            
        return "I am the PlaceTrack AI Assistant. I can guide you on resume uploads, job postings, ERP validation reports, mailbox messages, or AI gap analytics. What would you like to know?"


