-- HSU Early Warning System - Complete Database Schema
-- =====================================================
-- Production-ready SQLite database schema
-- Author: Team Infinite - Group 6
-- Date: 2025

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- =====================================================
-- 1. USERS & AUTHENTICATION
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK(role IN ('student', 'advisor', 'admin')),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expiry TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- =====================================================
-- 2. STUDENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    banner_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    classification VARCHAR(50),
    enrollment_status VARCHAR(50) DEFAULT 'Active',
    first_generation_student BOOLEAN DEFAULT 0,
    international_student BOOLEAN DEFAULT 0,
    veteran_status BOOLEAN DEFAULT 0,
    disability_status BOOLEAN DEFAULT 0,
    primary_advisor_id INTEGER,
    expected_graduation_date DATE,
    declared_major VARCHAR(100),
    declared_minor VARCHAR(100),
    home_address TEXT,
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    photo_url VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (primary_advisor_id) REFERENCES advisors(advisor_id)
);

CREATE INDEX idx_students_banner_id ON students(banner_id);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_classification ON students(classification);
CREATE INDEX idx_students_advisor ON students(primary_advisor_id);

-- =====================================================
-- 3. ADVISORS
-- =====================================================

CREATE TABLE IF NOT EXISTS advisors (
    advisor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    department VARCHAR(100),
    office_location VARCHAR(200),
    office_hours TEXT,
    specialization TEXT,
    max_caseload INTEGER DEFAULT 50,
    is_active BOOLEAN DEFAULT 1,
    photo_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_advisors_email ON advisors(email);
CREATE INDEX idx_advisors_department ON advisors(department);

-- =====================================================
-- 4. DEPARTMENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_code VARCHAR(20) UNIQUE NOT NULL,
    department_name VARCHAR(200) NOT NULL,
    college VARCHAR(200),
    department_head VARCHAR(200),
    contact_email VARCHAR(255),
    phone_number VARCHAR(20),
    building VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_code ON departments(department_code);

-- =====================================================
-- 5. TERMS (Academic Terms)
-- =====================================================

CREATE TABLE IF NOT EXISTS terms (
    term_id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_code VARCHAR(20) UNIQUE NOT NULL,
    term_name VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    midterm_date DATE,
    is_current_term BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_terms_code ON terms(term_code);
CREATE INDEX idx_terms_current ON terms(is_current_term);

-- =====================================================
-- 6. COURSES
-- =====================================================

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    course_description TEXT,
    credit_hours INTEGER NOT NULL,
    level VARCHAR(50),
    department_id INTEGER,
    prerequisites TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE INDEX idx_courses_code ON courses(course_code);
CREATE INDEX idx_courses_department ON courses(department_id);

-- =====================================================
-- 7. FACULTY
-- =====================================================

CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    title VARCHAR(100),
    department_id INTEGER,
    office_location VARCHAR(200),
    office_hours TEXT,
    is_active BOOLEAN DEFAULT 1,
    photo_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE INDEX idx_faculty_email ON faculty(email);
CREATE INDEX idx_faculty_department ON faculty(department_id);

-- =====================================================
-- 8. ENROLLMENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    faculty_id INTEGER,
    enrollment_date DATE NOT NULL,
    withdrawal_date DATE,
    status VARCHAR(50) DEFAULT 'Active',
    grade VARCHAR(5),
    grade_points DECIMAL(3,2),
    is_completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (term_id) REFERENCES terms(term_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
    UNIQUE(student_id, course_id, term_id)
);

CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_enrollments_term ON enrollments(term_id);
CREATE INDEX idx_enrollments_status ON enrollments(status);

-- =====================================================
-- 9. GRADES (Assignment-level grades)
-- =====================================================

CREATE TABLE IF NOT EXISTS grades (
    grade_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    assignment_type VARCHAR(50),
    assignment_name VARCHAR(200),
    points_earned DECIMAL(6,2),
    points_possible DECIMAL(6,2),
    grade_percentage DECIMAL(5,2),
    submission_date TIMESTAMP,
    is_on_time BOOLEAN DEFAULT 1,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
);

CREATE INDEX idx_grades_enrollment ON grades(enrollment_id);
CREATE INDEX idx_grades_type ON grades(assignment_type);

-- =====================================================
-- 10. ATTENDANCE
-- =====================================================

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    class_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Present',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    UNIQUE(enrollment_id, class_date)
);

CREATE INDEX idx_attendance_enrollment ON attendance(enrollment_id);
CREATE INDEX idx_attendance_date ON attendance(class_date);
CREATE INDEX idx_attendance_status ON attendance(status);

-- =====================================================
-- 11. LMS LOGINS (Learning Management System Activity)
-- =====================================================

CREATE TABLE IF NOT EXISTS logins (
    login_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    enrollment_id INTEGER,
    login_timestamp TIMESTAMP NOT NULL,
    logout_timestamp TIMESTAMP,
    session_duration_minutes INTEGER,
    activity_type VARCHAR(100),
    ip_address VARCHAR(50),
    device_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
);

CREATE INDEX idx_logins_student ON logins(student_id);
CREATE INDEX idx_logins_timestamp ON logins(login_timestamp);

-- =====================================================
-- 12. PAYMENTS (Financial Transactions)
-- =====================================================

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    amount_owed DECIMAL(10,2) NOT NULL,
    amount_paid DECIMAL(10,2) DEFAULT 0,
    balance DECIMAL(10,2) NOT NULL,
    has_hold BOOLEAN DEFAULT 0,
    hold_reason TEXT,
    due_date DATE NOT NULL,
    payment_date DATE,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (term_id) REFERENCES terms(term_id)
);

CREATE INDEX idx_payments_student ON payments(student_id);
CREATE INDEX idx_payments_term ON payments(term_id);
CREATE INDEX idx_payments_hold ON payments(has_hold);

-- =====================================================
-- 13. COUNSELING (Mental Health & Support Services)
-- =====================================================

CREATE TABLE IF NOT EXISTS counseling (
    counseling_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    visit_date DATE NOT NULL,
    counselor_name VARCHAR(200),
    concern_type VARCHAR(100),
    severity_level INTEGER CHECK(severity_level BETWEEN 1 AND 10),
    crisis_flag BOOLEAN DEFAULT 0,
    notes TEXT,
    follow_up_required BOOLEAN DEFAULT 0,
    follow_up_date DATE,
    status VARCHAR(50) DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE INDEX idx_counseling_student ON counseling(student_id);
CREATE INDEX idx_counseling_date ON counseling(visit_date);
CREATE INDEX idx_counseling_crisis ON counseling(crisis_flag);

-- =====================================================
-- 14. RISK SCORES (ML Predictions)
-- =====================================================

CREATE TABLE IF NOT EXISTS risk_scores (
    risk_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    score_calculation_date TIMESTAMP NOT NULL,
    overall_risk_score DECIMAL(5,4) NOT NULL,
    academic_risk_factor DECIMAL(5,4),
    engagement_risk_factor DECIMAL(5,4),
    financial_risk_factor DECIMAL(5,4),
    wellness_risk_factor DECIMAL(5,4),
    risk_category VARCHAR(50),
    risk_pathway VARCHAR(200),
    confidence_score DECIMAL(5,4),
    model_version VARCHAR(50),
    is_current BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (term_id) REFERENCES terms(term_id)
);

CREATE INDEX idx_risk_scores_student ON risk_scores(student_id);
CREATE INDEX idx_risk_scores_term ON risk_scores(term_id);
CREATE INDEX idx_risk_scores_category ON risk_scores(risk_category);
CREATE INDEX idx_risk_scores_current ON risk_scores(is_current);

-- =====================================================
-- 15. INTERVENTION TYPES (Templates)
-- =====================================================

CREATE TABLE IF NOT EXISTS intervention_types (
    intervention_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    default_priority VARCHAR(50),
    estimated_duration_minutes INTEGER,
    success_criteria TEXT,
    best_practices TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_intervention_types_category ON intervention_types(category);

-- =====================================================
-- 16. INTERVENTIONS (Student Support Actions)
-- =====================================================

CREATE TABLE IF NOT EXISTS interventions (
    intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    advisor_id INTEGER NOT NULL,
    intervention_type_id INTEGER,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(50) DEFAULT 'Medium',
    status VARCHAR(50) DEFAULT 'Scheduled',
    scheduled_date TIMESTAMP,
    completed_date TIMESTAMP,
    location VARCHAR(200),
    method VARCHAR(50) DEFAULT 'In-person',
    duration_minutes INTEGER,
    student_response TEXT,
    outcome_assessment TEXT,
    follow_up_required BOOLEAN DEFAULT 0,
    follow_up_date DATE,
    success_rating INTEGER CHECK(success_rating BETWEEN 1 AND 5),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id),
    FOREIGN KEY (intervention_type_id) REFERENCES intervention_types(intervention_type_id)
);

CREATE INDEX idx_interventions_student ON interventions(student_id);
CREATE INDEX idx_interventions_advisor ON interventions(advisor_id);
CREATE INDEX idx_interventions_status ON interventions(status);
CREATE INDEX idx_interventions_priority ON interventions(priority);
CREATE INDEX idx_interventions_scheduled ON interventions(scheduled_date);

-- =====================================================
-- 17. APPOINTMENTS (Scheduled Meetings)
-- =====================================================

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    advisor_id INTEGER NOT NULL,
    appointment_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    location VARCHAR(200),
    method VARCHAR(50) DEFAULT 'In-person',
    purpose TEXT,
    status VARCHAR(50) DEFAULT 'Scheduled',
    reminder_sent BOOLEAN DEFAULT 0,
    reminder_sent_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id)
);

CREATE INDEX idx_appointments_student ON appointments(student_id);
CREATE INDEX idx_appointments_advisor ON appointments(advisor_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

-- =====================================================
-- 18. NOTIFICATIONS (System Notifications)
-- =====================================================

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    notification_type VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(50) DEFAULT 'Normal',
    is_read BOOLEAN DEFAULT 0,
    read_at TIMESTAMP,
    action_url VARCHAR(500),
    action_label VARCHAR(100),
    related_entity_type VARCHAR(50),
    related_entity_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

-- =====================================================
-- 19. EMAIL QUEUE (Outbound Emails)
-- =====================================================

CREATE TABLE IF NOT EXISTS email_queue (
    email_id INTEGER PRIMARY KEY AUTOINCREMENT,
    to_email VARCHAR(255) NOT NULL,
    cc_email VARCHAR(255),
    subject VARCHAR(500) NOT NULL,
    body_text TEXT NOT NULL,
    body_html TEXT,
    email_type VARCHAR(100),
    priority INTEGER DEFAULT 3,
    status VARCHAR(50) DEFAULT 'Pending',
    scheduled_send_time TIMESTAMP,
    sent_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_email_queue_scheduled ON email_queue(scheduled_send_time);

-- =====================================================
-- 20. AUDIT LOGS (System Activity Tracking)
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(200) NOT NULL,
    entity_type VARCHAR(100),
    entity_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- =====================================================
-- 21. REPORTS (Saved Reports)
-- =====================================================

CREATE TABLE IF NOT EXISTS reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_name VARCHAR(200) NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL,
    parameters TEXT,
    schedule VARCHAR(100),
    next_run_time TIMESTAMP,
    last_run_time TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE INDEX idx_reports_created_by ON reports(created_by);
CREATE INDEX idx_reports_type ON reports(report_type);

-- =====================================================
-- 22. SYSTEM SETTINGS (Configuration)
-- =====================================================

CREATE TABLE IF NOT EXISTS system_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key VARCHAR(200) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50),
    description TEXT,
    is_public BOOLEAN DEFAULT 0,
    updated_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

CREATE INDEX idx_system_settings_key ON system_settings(setting_key);

-- =====================================================
-- 23. STUDENT NOTES (Advisor Notes)
-- =====================================================

CREATE TABLE IF NOT EXISTS student_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    advisor_id INTEGER NOT NULL,
    note_type VARCHAR(100),
    subject VARCHAR(200),
    content TEXT NOT NULL,
    is_private BOOLEAN DEFAULT 0,
    is_flagged BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id)
);

CREATE INDEX idx_student_notes_student ON student_notes(student_id);
CREATE INDEX idx_student_notes_advisor ON student_notes(advisor_id);

-- =====================================================
-- END OF SCHEMA
-- =====================================================
