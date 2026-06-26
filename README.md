# PlaceTrack AI - Intelligent Placement Coordinator & Analytics Portal

PlaceTrack AI is a premium, university-grade placement automation and talent matching platform. It connects graduating student cohorts with corporate recruiters, automates drive scheduling, and uses local AI analytics to bridge talent-recruitment gaps.

---

## Key Features

### 1. Minimalist Flat User Interface
- Designed using custom CSS variables, CSS Grid, and Flexbox for maximum performance and layout cleanliness.
- Powered by the highly legible **Inter** font family stack.
- Zero clutter: no glowing glassmorphism, heavy gradients, or unnecessary animations, ensuring an enterprise-grade dark layout.

### 2. Floating AI Support Chatbot
- A floating support widget accessible from all dashboard views.
- Powered by a local NLP rules-matcher in `ai_engine.py` to handle session-specific inquiries for Candidates, Recruiters, and Admins.
- Answers questions about resume uploads, job approvals, recruiter requirements, and mailbox messaging.

### 3. Talent Sector Classification & Job Matching
- Automatically analyzes student skills, stream, and bio to map them into key industry sectors (e.g., Software Engineering, Web Development, Core Engineering, Data Science & ML).
- Computes job-student compatibility percentages (0-100%) and provides a detailed breakdown of matched vs. missing skills.

### 4. Admin AI Insights Dashboard
- Maps graduating student sector talent counts against active recruiter job drives.
- Analyzes matching ratios and automatically highlights talent surpluses or shortages.
- Suggests targeted recruiting partners to invite (e.g., Wipro for Web Dev, AMD for Core VLSI) and allows administrators to trigger invitations.

### 5. ERP Registry Mismatch Verification
- Compares candidate-reported qualifications (SSC, HSC, UG scores) with official college ERP database records.
- Automatically flags profile discrepancies in red for administrators to prevent academic score inflation.

### 6. Interactive Message Center
- An internal mailbox allowing live conversation threads between students, recruiters, and the college placement administration.

---

## Technology Stack

- **Backend Framework**: Python (Flask)
- **Authentication & Sessions**: Flask-Login
- **Database & ORM**: SQLite with Flask-SQLAlchemy ORM (supports zero-config run and easy MySQL/PostgreSQL migration)
- **Frontend Layer**: HTML5, Vanilla JavaScript (ES6+), Custom CSS (Variables, Flexbox, Grid)
- **AI Matching Engine**: Local regex NLP heuristics (`ai_engine.py`)

---

## Getting Started & Local Run

### Prerequisites
- Python 3.8 or higher installed on your machine.

### Installation Steps

1. **Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize and Seed Database**:
   This runs the seeder script `init_db.py` to compile the schema, parse 48,000+ states and cities from the legacy dataset, and populate sample notices, student records, and company drives:
   ```bash
   python init_db.py
   ```

4. **Start Web Server**:
   Launch the Flask development server:
   ```bash
   python app.py
   ```

5. **Access the Portal**:
   Open your browser and navigate to `http://localhost:5000`.

---

## Mock Accounts for Verification

Test the role-based views and the chatbot using these pre-seeded accounts:
- **Admin Panel**: Username: `admin` | Password: `123456`
- **Candidate (Approved)**: Email: `jatin@gmail.com` | Password: `123456`
- **Candidate (Discrepancy Mismatch)**: Email: `student@example.com` | Password: `password123`
- **Corporate Recruiter**: Email: `recruiter@example.com` | Password: `password123`
