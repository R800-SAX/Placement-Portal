import os
import re
from datetime import datetime
from app import create_app
from models import db, Admin, User, Company, JobPost, Notice, Country, State, City, ApplyJobPost, Mailbox, ReplyMailbox

def parse_and_seed_locations(app):
    sql_file_path = os.path.join(app.root_path, 'old_php', 'database', 'db1.sql')
    if not os.path.exists(sql_file_path):
        print(f"db1.sql not found at {sql_file_path}, skipping geographic data seeding.")
        return
    
    print("Parsing geographic data from db1.sql... (This might take a minute)")
    
    try:
        # Read the SQL dump with encoding errors ignored to avoid binary glitches
        with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find INSERT statements for states and cities
        # SQLite uses raw SQL inserts easily via connection execute
        with app.app_context():
            # Check if countries already exist
            if Country.query.first():
                print("Countries table already populated, skipping locations seeding.")
                return

            print("Seeding Countries, States and Cities...")
            # Create a default country (India)
            default_country = Country(id=1, sortname="IN", name="India", phonecode=91)
            db.session.add(default_country)
            db.session.commit()

            # Find state inserts
            state_matches = re.findall(r"INSERT INTO `states` VALUES (.*?);", content)
            for match in state_matches:
                # Format: (1,'Andaman and Nicobar Islands',1),(2,'Andhra Pradesh',1)
                # Split values by closed parenthesis and open parenthesis
                tuples = re.findall(r"\((.*?)\)", match)
                for t in tuples:
                    parts = [p.strip().strip("'") for p in t.split(",")]
                    if len(parts) >= 2:
                        try:
                            state_id = int(parts[0])
                            state_name = parts[1]
                            country_id = int(parts[2]) if len(parts) > 2 else 1
                            state = State(id=state_id, name=state_name, country_id=country_id)
                            db.session.add(state)
                        except Exception:
                            pass
            db.session.commit()
            print("States seeded successfully.")

            # Find city inserts. Since there are around 48k cities in the SQL file,
            # inserting them individually can be slow in Python ORM, so we parse and run bulk insert.
            city_matches = re.findall(r"INSERT INTO `cities` VALUES (.*?);", content)
            cities_to_add = []
            
            for match in city_matches:
                tuples = re.findall(r"\((.*?)\)", match)
                for t in tuples:
                    # Some city names might contain commas, let's parse carefully
                    # Standard CSV split might fail for names like "Bombuflat, South Andaman"
                    # So we use a regex for sql strings
                    parts = re.findall(r"(\d+)|'([^']*)'", t)
                    parsed_parts = []
                    for digit, string in parts:
                        if digit:
                            parsed_parts.append(digit)
                        else:
                            parsed_parts.append(string)
                    
                    if len(parsed_parts) >= 3:
                        try:
                            city_id = int(parsed_parts[0])
                            city_name = parsed_parts[1]
                            state_id = int(parsed_parts[2])
                            cities_to_add.append(
                                City(id=city_id, name=city_name, state_id=state_id)
                            )
                        except Exception:
                            pass
            
            # Seed in chunks to avoid memory issues
            chunk_size = 5000
            for i in range(0, len(cities_to_add), chunk_size):
                chunk = cities_to_add[i:i+chunk_size]
                db.session.bulk_save_objects(chunk)
                db.session.commit()
            
            print(f"Seeded {len(cities_to_add)} cities successfully.")
            
    except Exception as e:
        print(f"Error seeding locations: {e}")

def seed_mock_data(app):
    with app.app_context():
        # Check if users already exist
        if User.query.first():
            print("Mock data already populated, skipping.")
            return

        print("Seeding mock data...")

        # 1. Admin
        admin = Admin(username="admin")
        admin.set_password("123456")
        db.session.add(admin)

        # 2. Users (Students)
        student1 = User(
            firstname="Atinder",
            lastname="Kumar",
            email="student@example.com",
            address="123 Academic Lane",
            city="Noida",
            state="Uttar Pradesh",
            contactno="9876543210",
            qualification="B.Tech",
            stream="Computer Science",
            passingyear="2026",
            dob="2004-05-15",
            age="22",
            designation="Student",
            active=1, # Approved
            aboutme="Aspiring software engineer interested in full stack web development and system design.",
            skills="Python, Flask, JavaScript, SQLite, HTML5, CSS3",
            hsc="85%",
            ssc=80,
            ug=82,
            pg=0
        )
        student1.set_password("password123")
        db.session.add(student1)

        student2 = User(
            firstname="Jatin",
            lastname="Tagore",
            email="jatin@gmail.com",
            address="456 Campus Road",
            city="Noida",
            state="Uttar Pradesh",
            contactno="9876543211",
            qualification="B.Tech",
            stream="Information Technology",
            passingyear="2026",
            dob="2004-08-20",
            age="22",
            designation="Student",
            active=1, # Approved
            aboutme="Passionate coder with experience in building data-driven python apps.",
            skills="Python, SQL, Django, Pandas, Data Science",
            hsc="90%",
            ssc=88,
            ug=84,
            pg=0
        )
        student2.set_password("123456")
        db.session.add(student2)

        student_pending = User(
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            address="789 Lane Street",
            city="Delhi",
            state="Delhi",
            contactno="9876543212",
            qualification="MCA",
            stream="Computer Applications",
            passingyear="2027",
            dob="2003-01-01",
            age="23",
            designation="Student",
            active=2, # Pending approval
            aboutme="Enthusiastic developer looking for internship opportunities.",
            skills="Java, Spring, HTML, CSS",
            hsc="75%",
            ssc=72,
            ug=75,
            pg=78
        )
        student_pending.set_password("password123")
        db.session.add(student_pending)

        # 3. Companies
        company1 = Company(
            name="Sumit Sharma",
            companyname="Tech Solutions Inc.",
            state="Delhi",
            city="New Delhi",
            contactno="9999988888",
            website="https://techsolutions.example.com",
            email="recruiter@example.com",
            aboutme="A global technology consulting and software services company specializing in building scalable applications.",
            active=1, # Approved
            logo="default_logo.png"
        )
        company1.set_password("password123")
        db.session.add(company1)

        company2 = Company(
            name="Rajesh Patel",
            companyname="Innovative Web Corp",
            state="Maharashtra",
            city="Mumbai",
            contactno="9999988887",
            website="https://webcorp.example.com",
            email="abc@gmail.com",
            aboutme="A creative digital agency creating modern web applications and providing top-notch cloud solutions.",
            active=1, # Approved
            logo="default_logo.png"
        )
        company2.set_password("123456")
        db.session.add(company2)

        company_pending = Company(
            name="Sarah Jenkins",
            companyname="Future Systems",
            state="Karnataka",
            city="Bengaluru",
            contactno="9999988886",
            website="https://futuresys.example.com",
            email="futuresys@example.com",
            aboutme="Pioneering future tech in AI and Cloud infrastructure.",
            active=2, # Pending approval
            logo="default_logo.png"
        )
        company_pending.set_password("password123")
        db.session.add(company_pending)

        db.session.commit() # Save users & companies to reference foreign keys
        print("Users and Companies seeded.")

        # 4. Job Posts
        job1 = JobPost(
            id_company=company1.id_company,
            jobtitle="Software Engineer Intern (Python/Flask)",
            description="We are seeking a Software Engineer Intern with strong Python fundamentals. Experience in Flask web framework, SQLite/SQL, and basic HTML/CSS is highly desirable. You will work on optimizing backend services, debugging APIs, and improving developer workflows.",
            minimumsalary="30,000",
            maximumsalary="45,000",
            experience="Fresher (0-1 Years)",
            qualification="B.Tech CS/IT / MCA",
            createdat=datetime.utcnow()
        )
        db.session.add(job1)

        job2 = JobPost(
            id_company=company1.id_company,
            jobtitle="Data Engineer Associate",
            description="Tech Solutions is looking for a junior Data Engineer to help build our ETL pipelines. Knowledge of SQL, Python, pandas, and databases is required. Experience with cloud platforms (AWS/Azure) is a plus.",
            minimumsalary="50,000",
            maximumsalary="70,000",
            experience="0-2 Years",
            qualification="B.Tech CS/IT / BCA",
            createdat=datetime.utcnow()
        )
        db.session.add(job2)

        job3 = JobPost(
            id_company=company2.id_company,
            jobtitle="Full-Stack Web Developer",
            description="Innovative Web Corp is hiring a Junior Full-Stack Developer. Strong command of Vanilla Javascript, HTML5, CSS3 is required. Backend experience with Python or PHP is necessary. You will design, build, and support highly interactive user interfaces.",
            minimumsalary="40,000",
            maximumsalary="60,000",
            experience="1-2 Years",
            qualification="B.Tech CS/IT / BCA",
            createdat=datetime.utcnow()
        )
        db.session.add(job3)

        # 5. Notices
        n1 = Notice(
            subject="Welcome to the New PlaceTrack AI Portal",
            notice="We are excited to launch our rewritten, premium PlaceTrack AI Portal. Students can now manage their profiles, upload resumes, and track job drives with ease. Please complete your registration and profile setup.",
            audience="all",
            date=datetime.utcnow()
        )
        db.session.add(n1)

        n2 = Notice(
            subject="Resume Upload Guidelines",
            notice="All students are requested to only upload resumes in PDF format. Keep the file size under 5MB. Ensure your contact details and aggregate CGPA are accurate in the profile settings.",
            audience="students",
            date=datetime.utcnow()
        )
        db.session.add(n2)

        n3 = Notice(
            subject="Upcoming Recruiter Briefing",
            notice="A briefing session for all registered recruitment cell coordinators is scheduled on Friday at 3:00 PM to discuss the upcoming pre-placement drives and registration flows.",
            audience="companies",
            date=datetime.utcnow()
        )
        db.session.add(n3)

        # 6. Apply Job Post
        # Atinder Kumar (student1) applied to Software Engineer Intern (job1)
        apply1 = ApplyJobPost(
            id_jobpost=job1.id_jobpost,
            id_company=company1.id_company,
            id_user=student1.id_user,
            status=2 # Pending/Applied
        )
        db.session.add(apply1)

        # Jatin Tagore (student2) applied to Full-Stack Web Developer (job3)
        apply2 = ApplyJobPost(
            id_jobpost=job3.id_jobpost,
            id_company=company2.id_company,
            id_user=student2.id_user,
            status=1 # Selected
        )
        db.session.add(apply2)

        db.session.commit()
        print("Mock job posts, notices, and applications seeded successfully!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Created all database tables.")
        
    # Seed location data
    parse_and_seed_locations(app)
    
    # Seed mock data
    seed_mock_data(app)
    print("Database initialization complete!")
