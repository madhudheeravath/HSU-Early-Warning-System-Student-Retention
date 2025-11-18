"""
CSV to Database Migration Script
=================================
Migrates all CSV data to SQLite database with proper relationships

Author: Team Infinite - Group 6
Date: 2025
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import hashlib

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db, logger

# Data directory
DATA_DIR = Path(__file__).parent.parent / "Data_Web"


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def migrate_departments():
    """Migrate departments.csv"""
    logger.info("Migrating departments...")
    
    df = pd.read_csv(DATA_DIR / "departments.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO departments (
                    department_id, department_code, department_name, college,
                    department_head, contact_email
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                int(row['DepartmentID']),
                row['DepartmentCode'],
                row['DepartmentName'],
                row['College'],
                row['DepartmentHead'],
                row['ContactEmail']
            ))
    
    logger.info(f"✅ Migrated {len(df)} departments")


def migrate_terms():
    """Migrate terms.csv"""
    logger.info("Migrating terms...")
    
    df = pd.read_csv(DATA_DIR / "terms.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO terms (
                    term_id, term_code, term_name, year, start_date, end_date,
                    midterm_date, is_current_term
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['TermID']),
                row['TermCode'],
                row['TermName'],
                int(row['Year']),
                row['StartDate'],
                row['EndDate'],
                row['MidtermDate'],
                int(row['IsCurrentTerm'])
            ))
    
    logger.info(f"✅ Migrated {len(df)} terms")


def migrate_courses():
    """Migrate courses.csv"""
    logger.info("Migrating courses...")
    
    df = pd.read_csv(DATA_DIR / "courses.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO courses (
                    course_id, course_code, course_name, course_description,
                    credit_hours, level, department_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['CourseID']),
                row['CourseCode'],
                row['CourseName'],
                row.get('CourseDescription', ''),
                int(row['CreditHours']),
                row['Level'],
                int(row['DepartmentID'])
            ))
    
    logger.info(f"✅ Migrated {len(df)} courses")


def migrate_faculty():
    """Migrate faculty.csv"""
    logger.info("Migrating faculty...")
    
    df = pd.read_csv(DATA_DIR / "faculty.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            # Create user account for faculty
            email = row['Email']
            password_hash = hash_password('faculty123')  # Default password
            
            cursor.execute("""
                INSERT OR IGNORE INTO users (
                    email, password_hash, role, first_name, last_name, phone_number
                ) VALUES (?, ?, 'advisor', ?, ?, ?)
            """, (
                email,
                password_hash,
                row['FirstName'],
                row['LastName'],
                row.get('PhoneNumber', '')
            ))
            
            user_id = cursor.lastrowid
            
            # Create faculty record
            cursor.execute("""
                INSERT OR IGNORE INTO faculty (
                    faculty_id, user_id, first_name, last_name, email,
                    phone_number, title, department_id, office_location
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['FacultyID']),
                user_id if user_id > 0 else None,
                row['FirstName'],
                row['LastName'],
                email,
                row.get('PhoneNumber', ''),
                row['Title'],
                int(row['DepartmentID']),
                row.get('OfficeLocation', '')
            ))
    
    logger.info(f"✅ Migrated {len(df)} faculty members")


def migrate_students():
    """Migrate students.csv and create user accounts"""
    logger.info("Migrating students...")
    
    df = pd.read_csv(DATA_DIR / "students.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            # Create user account for student
            email = row['Email']
            password_hash = hash_password('student123')  # Default password
            
            cursor.execute("""
                INSERT OR IGNORE INTO users (
                    email, password_hash, role, first_name, last_name, phone_number
                ) VALUES (?, ?, 'student', ?, ?, ?)
            """, (
                email,
                password_hash,
                row['FirstName'],
                row['LastName'],
                row.get('PhoneNumber', '')
            ))
            
            user_id = cursor.lastrowid if cursor.lastrowid > 0 else None
            
            # Create student record
            cursor.execute("""
                INSERT OR IGNORE INTO students (
                    student_id, user_id, banner_id, first_name, last_name, email,
                    phone_number, date_of_birth, gender, classification,
                    first_generation_student, international_student
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['StudentID']),
                user_id,
                row['BannerID'],
                row['FirstName'],
                row['LastName'],
                email,
                row.get('PhoneNumber', ''),
                row['DateOfBirth'],
                row['Gender'],
                row['Classification'],
                int(row.get('FirstGenerationStudent', 0)),
                int(row.get('InternationalStudent', 0))
            ))
    
    logger.info(f"✅ Migrated {len(df)} students")


def migrate_enrollments():
    """Migrate enrollments.csv"""
    logger.info("Migrating enrollments...")
    
    df = pd.read_csv(DATA_DIR / "enrollments.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            withdrawal_date = row.get('WithdrawalDate')
            if pd.isna(withdrawal_date):
                withdrawal_date = None
            
            cursor.execute("""
                INSERT OR IGNORE INTO enrollments (
                    enrollment_id, student_id, course_id, term_id,
                    enrollment_date, withdrawal_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['EnrollmentID']),
                int(row['StudentID']),
                int(row['CourseID']),
                int(row['TermID']),
                row['EnrollmentDate'],
                withdrawal_date,
                row['Status']
            ))
    
    logger.info(f"✅ Migrated {len(df)} enrollments")


def migrate_grades():
    """Migrate grades.csv"""
    logger.info("Migrating grades...")
    
    df = pd.read_csv(DATA_DIR / "grades.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                cursor.execute("""
                    INSERT OR IGNORE INTO grades (
                        grade_event_id, enrollment_id, assignment_type, assignment_name,
                        points_earned, points_possible, grade_percentage,
                        submission_date, is_on_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row['GradeEventID']),
                    int(row['EnrollmentID']),
                    row.get('AssignmentType', ''),
                    row.get('AssignmentName', ''),
                    float(row.get('PointsEarned', 0)) if pd.notna(row.get('PointsEarned')) else None,
                    float(row.get('PointsPossible', 100)),
                    float(row.get('GradePercentage', 0)) if pd.notna(row.get('GradePercentage')) else None,
                    row.get('SubmissionDate'),
                    int(row.get('IsOnTime', 1))
                ))
            
            logger.info(f"  Migrated {min(i+batch_size, len(df))}/{len(df)} grades...")
    
    logger.info(f"✅ Migrated {len(df)} grades")


def migrate_attendance():
    """Migrate attendance.csv"""
    logger.info("Migrating attendance...")
    
    df = pd.read_csv(DATA_DIR / "attendance.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                cursor.execute("""
                    INSERT OR IGNORE INTO attendance (
                        attendance_id, enrollment_id, class_date, status, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    int(row['AttendanceID']),
                    int(row['EnrollmentID']),
                    row['ClassDate'],
                    row['Status'],
                    row.get('Notes', '')
                ))
            
            logger.info(f"  Migrated {min(i+batch_size, len(df))}/{len(df)} attendance records...")
    
    logger.info(f"✅ Migrated {len(df)} attendance records")


def migrate_logins():
    """Migrate logins.csv"""
    logger.info("Migrating logins...")
    
    df = pd.read_csv(DATA_DIR / "logins.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                cursor.execute("""
                    INSERT OR IGNORE INTO logins (
                        login_id, student_id, enrollment_id, login_timestamp,
                        logout_timestamp, session_duration_minutes, activity_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row['LoginID']),
                    int(row['StudentID']),
                    int(row['EnrollmentID']) if pd.notna(row.get('EnrollmentID')) else None,
                    row['LoginTimestamp'],
                    row.get('LogoutTimestamp'),
                    int(row.get('SessionDurationMinutes', 0)) if pd.notna(row.get('SessionDurationMinutes')) else None,
                    row.get('ActivityType', '')
                ))
            
            logger.info(f"  Migrated {min(i+batch_size, len(df))}/{len(df)} logins...")
    
    logger.info(f"✅ Migrated {len(df)} logins")


def migrate_payments():
    """Migrate payments.csv"""
    logger.info("Migrating payments...")
    
    df = pd.read_csv(DATA_DIR / "payments.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO payments (
                    payment_id, student_id, term_id, amount_owed, amount_paid,
                    balance, has_hold, hold_reason, due_date, payment_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['PaymentID']),
                int(row['StudentID']),
                int(row['TermID']),
                float(row['AmountOwed']),
                float(row['AmountPaid']),
                float(row['Balance']),
                int(row.get('HasHold', 0)),
                row.get('HoldReason', ''),
                row['DueDate'],
                row.get('PaymentDate')
            ))
    
    logger.info(f"✅ Migrated {len(df)} payments")


def migrate_counseling():
    """Migrate counseling.csv"""
    logger.info("Migrating counseling...")
    
    df = pd.read_csv(DATA_DIR / "counseling.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO counseling (
                    counseling_id, student_id, visit_date, counselor_name,
                    concern_type, severity_level, crisis_flag, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['CounselingID']),
                int(row['StudentID']),
                row['VisitDate'],
                row['CounselorName'],
                row['ConcernType'],
                int(row['SeverityLevel']),
                int(row.get('CrisisFlag', 0)),
                row.get('Notes', '')
            ))
    
    logger.info(f"✅ Migrated {len(df)} counseling records")


def migrate_risk_scores():
    """Migrate risk_scores.csv"""
    logger.info("Migrating risk scores...")
    
    df = pd.read_csv(DATA_DIR / "risk_scores.csv")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO risk_scores (
                    risk_score_id, student_id, term_id, score_calculation_date,
                    overall_risk_score, academic_risk_factor, engagement_risk_factor,
                    financial_risk_factor, wellness_risk_factor, risk_category, is_current
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                int(row['RiskScoreID']),
                int(row['StudentID']),
                int(row['TermID']),
                row['ScoreCalculationDate'],
                float(row['OverallRiskScore']),
                float(row['AcademicRiskFactor']),
                float(row['EngagementRiskFactor']),
                float(row['FinancialRiskFactor']),
                float(row['WellnessRiskFactor']),
                row['RiskCategory']
            ))
    
    logger.info(f"✅ Migrated {len(df)} risk scores")


def create_advisors():
    """Create advisor accounts"""
    logger.info("Creating advisor accounts...")
    
    advisors = [
        {
            'email': 'advisor@hsu.edu',
            'password': 'advisor123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'department': 'Academic Advising',
            'office_location': 'Building A, Room 101'
        },
        {
            'email': 'advisor2@hsu.edu',
            'password': 'advisor123',
            'first_name': 'Michael',
            'last_name': 'Chen',
            'department': 'STEM Advising',
            'office_location': 'Building B, Room 205'
        }
    ]
    
    for advisor in advisors:
        # Create user (this manages its own transaction)
        user_id = db.create_user(
            email=advisor['email'],
            password=advisor['password'],
            role='advisor',
            first_name=advisor['first_name'],
            last_name=advisor['last_name']
        )
        
        # Create advisor record (separate transaction)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO advisors (
                    user_id, first_name, last_name, email, department, office_location
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                advisor['first_name'],
                advisor['last_name'],
                advisor['email'],
                advisor['department'],
                advisor['office_location']
            ))
    
    logger.info(f"✅ Created {len(advisors)} advisors")


def create_admin():
    """Create admin account"""
    logger.info("Creating admin account...")
    
    db.create_user(
        email='admin@hsu.edu',
        password='admin123',
        role='admin',
        first_name='Patricia',
        last_name='Martinez',
        phone_number='555-0100'
    )
    
    logger.info("✅ Created admin account")


def create_intervention_types():
    """Create default intervention types"""
    logger.info("Creating intervention types...")
    
    intervention_types = [
        {
            'type_name': 'Academic Check-In',
            'category': 'Academic',
            'description': 'Regular meeting to discuss academic progress and challenges',
            'default_priority': 'Medium',
            'estimated_duration_minutes': 30
        },
        {
            'type_name': 'Tutoring Referral',
            'category': 'Academic',
            'description': 'Connect student with tutoring services',
            'default_priority': 'High',
            'estimated_duration_minutes': 15
        },
        {
            'type_name': 'Financial Aid Consultation',
            'category': 'Financial',
            'description': 'Discuss financial aid options and payment plans',
            'default_priority': 'High',
            'estimated_duration_minutes': 45
        },
        {
            'type_name': 'Counseling Referral',
            'category': 'Wellness',
            'description': 'Connect student with mental health services',
            'default_priority': 'Critical',
            'estimated_duration_minutes': 15
        },
        {
            'type_name': 'Career Counseling',
            'category': 'Engagement',
            'description': 'Discuss career goals and major selection',
            'default_priority': 'Medium',
            'estimated_duration_minutes': 60
        },
        {
            'type_name': 'Study Skills Workshop',
            'category': 'Academic',
            'description': 'Workshop on time management and study strategies',
            'default_priority': 'Low',
            'estimated_duration_minutes': 90
        }
    ]
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for itype in intervention_types:
            cursor.execute("""
                INSERT OR IGNORE INTO intervention_types (
                    type_name, category, description, default_priority, estimated_duration_minutes
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                itype['type_name'],
                itype['category'],
                itype['description'],
                itype['default_priority'],
                itype['estimated_duration_minutes']
            ))
    
    logger.info(f"✅ Created {len(intervention_types)} intervention types")


def run_full_migration():
    """Run complete migration from CSV to database"""
    logger.info("="*60)
    logger.info("Starting full CSV to Database migration...")
    logger.info("="*60)
    
    try:
        # Reference data first (no dependencies)
        migrate_departments()
        migrate_terms()
        migrate_courses()
        
        # Users and people
        migrate_faculty()
        migrate_students()
        create_advisors()
        create_admin()
        
        # Student data (depends on students, courses, terms)
        migrate_enrollments()
        migrate_grades()
        migrate_attendance()
        migrate_logins()
        migrate_payments()
        migrate_counseling()
        migrate_risk_scores()
        
        # System data
        create_intervention_types()
        
        # Show statistics
        logger.info("="*60)
        logger.info("Migration completed successfully!")
        logger.info("="*60)
        
        stats = db.get_database_stats()
        logger.info("\nDatabase Statistics:")
        for table, count in stats.items():
            logger.info(f"  {table}: {count} records")
        
        logger.info("\n✅ All CSV data migrated to database!")
        logger.info(f"📊 Database location: {db.db_path}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    # Run migration
    run_full_migration()
