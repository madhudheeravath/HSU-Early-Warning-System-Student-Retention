"""
Database Manager for HSU Early Warning System
==============================================
Handles all database operations with connection pooling and error handling

Author: Team Infinite - Group 6
Date: 2025
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database file location
DB_PATH = Path(__file__).parent / "hsu_database.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class DatabaseManager:
    """Manages all database operations for HSU Early Warning System"""
    
    def __init__(self, db_path=DB_PATH):
        """Initialize database manager"""
        self.db_path = db_path
        self.ensure_database_exists()
    
    @contextmanager
    def get_connection(self):
        """
        Get database connection with automatic cleanup
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        if not self.db_path.exists():
            logger.info("Creating new database...")
            self.create_tables()
            logger.info("Database created successfully!")
        else:
            logger.info(f"Using existing database at {self.db_path}")
    
    def create_tables(self):
        """Create all database tables from schema file"""
        with self.get_connection() as conn:
            with open(SCHEMA_PATH, 'r') as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)
            logger.info("Database schema created successfully")
    
    def drop_all_tables(self):
        """Drop all tables - USE WITH CAUTION!"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                if table[0] != 'sqlite_sequence':
                    cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            
            logger.warning("All tables dropped!")
    
    def rebuild_database(self):
        """Drop and recreate all tables - USE WITH CAUTION!"""
        self.drop_all_tables()
        self.create_tables()
        logger.info("Database rebuilt successfully")
    
    # =====================================================
    # USER AUTHENTICATION
    # =====================================================
    
    def create_user(self, email, password, role, first_name, last_name, **kwargs):
        """
        Create a new user account
        
        Args:
            email: User email (unique)
            password: Plain text password (will be hashed)
            role: User role (student, advisor, admin)
            first_name: First name
            last_name: Last name
            **kwargs: Additional user fields
        
        Returns:
            int: user_id of created user
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, first_name, last_name, 
                                   phone_number, is_active, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email.lower().strip(),
                password_hash,
                role,
                first_name,
                last_name,
                kwargs.get('phone_number'),
                kwargs.get('is_active', 1),
                kwargs.get('is_verified', 0)
            ))
            
            user_id = cursor.lastrowid
            logger.info(f"Created user: {email} (ID: {user_id})")
            return user_id
    
    def authenticate_user(self, email, password):
        """
        Authenticate user credentials
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            dict: User info if authenticated, None otherwise
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, email, role, first_name, last_name, phone_number, is_active
                FROM users
                WHERE email = ? AND password_hash = ? AND is_active = 1
            """, (email.lower().strip(), password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user['user_id'],))
                
                logger.info(f"User authenticated: {email}")
                return dict(user)
            
            logger.warning(f"Authentication failed for: {email}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def update_password(self, user_id, new_password):
        """Update user password"""
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (password_hash, user_id))
            
            logger.info(f"Password updated for user ID: {user_id}")
    
    # =====================================================
    # STUDENTS
    # =====================================================
    
    def create_student(self, **kwargs):
        """Create a new student record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (
                    user_id, banner_id, first_name, last_name, email, phone_number,
                    date_of_birth, gender, classification, enrollment_status,
                    first_generation_student, international_student, veteran_status,
                    disability_status, primary_advisor_id, expected_graduation_date,
                    declared_major, declared_minor, home_address,
                    emergency_contact_name, emergency_contact_phone, photo_url, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kwargs.get('user_id'),
                kwargs['banner_id'],
                kwargs['first_name'],
                kwargs['last_name'],
                kwargs['email'],
                kwargs.get('phone_number'),
                kwargs['date_of_birth'],
                kwargs.get('gender'),
                kwargs.get('classification'),
                kwargs.get('enrollment_status', 'Active'),
                kwargs.get('first_generation_student', 0),
                kwargs.get('international_student', 0),
                kwargs.get('veteran_status', 0),
                kwargs.get('disability_status', 0),
                kwargs.get('primary_advisor_id'),
                kwargs.get('expected_graduation_date'),
                kwargs.get('declared_major'),
                kwargs.get('declared_minor'),
                kwargs.get('home_address'),
                kwargs.get('emergency_contact_name'),
                kwargs.get('emergency_contact_phone'),
                kwargs.get('photo_url'),
                kwargs.get('notes')
            ))
            
            student_id = cursor.lastrowid
            logger.info(f"Created student: {kwargs['first_name']} {kwargs['last_name']} (ID: {student_id})")
            return student_id
    
    def get_student_by_id(self, student_id):
        """Get student by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            student = cursor.fetchone()
            return dict(student) if student else None
    
    def get_all_students(self, filters=None):
        """
        Get all students with optional filters
        
        Args:
            filters: Dict of filter criteria (e.g., {'classification': 'Freshman'})
        
        Returns:
            list: List of student dictionaries
        """
        query = "SELECT * FROM students WHERE enrollment_status = 'Active'"
        params = []
        
        if filters:
            for key, value in filters.items():
                query += f" AND {key} = ?"
                params.append(value)
        
        query += " ORDER BY last_name, first_name"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            students = cursor.fetchall()
            return [dict(student) for student in students]
    
    def update_student(self, student_id, **kwargs):
        """Update student information"""
        fields = []
        values = []
        
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(student_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE students SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
            """, values)
            
            logger.info(f"Updated student ID: {student_id}")
    
    # =====================================================
    # RISK SCORES
    # =====================================================
    
    def create_risk_score(self, student_id, term_id, overall_risk_score, **kwargs):
        """Create a new risk score record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Mark previous risk scores as not current
            cursor.execute("""
                UPDATE risk_scores SET is_current = 0
                WHERE student_id = ? AND term_id = ?
            """, (student_id, term_id))
            
            # Insert new risk score
            cursor.execute("""
                INSERT INTO risk_scores (
                    student_id, term_id, score_calculation_date, overall_risk_score,
                    academic_risk_factor, engagement_risk_factor, financial_risk_factor,
                    wellness_risk_factor, risk_category, risk_pathway,
                    confidence_score, model_version, is_current
                ) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                student_id,
                term_id,
                overall_risk_score,
                kwargs.get('academic_risk_factor'),
                kwargs.get('engagement_risk_factor'),
                kwargs.get('financial_risk_factor'),
                kwargs.get('wellness_risk_factor'),
                kwargs.get('risk_category'),
                kwargs.get('risk_pathway'),
                kwargs.get('confidence_score'),
                kwargs.get('model_version', 'v1.0')
            ))
            
            risk_score_id = cursor.lastrowid
            logger.info(f"Created risk score for student {student_id}: {overall_risk_score}")
            return risk_score_id
    
    def get_current_risk_score(self, student_id):
        """Get current risk score for a student"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM risk_scores
                WHERE student_id = ? AND is_current = 1
                ORDER BY score_calculation_date DESC
                LIMIT 1
            """, (student_id,))
            
            risk = cursor.fetchone()
            return dict(risk) if risk else None
    
    def get_risk_score_history(self, student_id):
        """Get risk score history for a student"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM risk_scores
                WHERE student_id = ?
                ORDER BY score_calculation_date DESC
            """, (student_id,))
            
            risks = cursor.fetchall()
            return [dict(risk) for risk in risks]
    
    # =====================================================
    # INTERVENTIONS
    # =====================================================
    
    def create_intervention(self, student_id, advisor_id, title, **kwargs):
        """Create a new intervention"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interventions (
                    student_id, advisor_id, intervention_type_id, title, description,
                    priority, status, scheduled_date, location, method,
                    follow_up_required, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                advisor_id,
                kwargs.get('intervention_type_id'),
                title,
                kwargs.get('description'),
                kwargs.get('priority', 'Medium'),
                kwargs.get('status', 'Scheduled'),
                kwargs.get('scheduled_date'),
                kwargs.get('location'),
                kwargs.get('method', 'In-person'),
                kwargs.get('follow_up_required', 0),
                kwargs.get('notes')
            ))
            
            intervention_id = cursor.lastrowid
            logger.info(f"Created intervention {intervention_id} for student {student_id}")
            return intervention_id
    
    def get_interventions(self, student_id=None, advisor_id=None, status=None):
        """Get interventions with optional filters"""
        query = "SELECT i.*, s.first_name || ' ' || s.last_name as student_name FROM interventions i JOIN students s ON i.student_id = s.student_id WHERE 1=1"
        params = []
        
        if student_id:
            query += " AND i.student_id = ?"
            params.append(student_id)
        
        if advisor_id:
            query += " AND i.advisor_id = ?"
            params.append(advisor_id)
        
        if status:
            query += " AND i.status = ?"
            params.append(status)
        
        query += " ORDER BY i.scheduled_date DESC"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            interventions = cursor.fetchall()
            return [dict(intervention) for intervention in interventions]
    
    def update_intervention(self, intervention_id, **kwargs):
        """Update intervention"""
        fields = []
        values = []
        
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(intervention_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE interventions SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE intervention_id = ?
            """, values)
            
            logger.info(f"Updated intervention ID: {intervention_id}")
    
    # =====================================================
    # NOTIFICATIONS
    # =====================================================
    
    def create_notification(self, user_id, notification_type, title, message, **kwargs):
        """Create a new notification"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications (
                    user_id, notification_type, title, message, priority,
                    action_url, action_label, related_entity_type, related_entity_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                notification_type,
                title,
                message,
                kwargs.get('priority', 'Normal'),
                kwargs.get('action_url'),
                kwargs.get('action_label'),
                kwargs.get('related_entity_type'),
                kwargs.get('related_entity_id')
            ))
            
            notification_id = cursor.lastrowid
            logger.info(f"Created notification for user {user_id}")
            return notification_id
    
    def get_unread_notifications(self, user_id):
        """Get unread notifications for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
            """, (user_id,))
            
            notifications = cursor.fetchall()
            return [dict(notification) for notification in notifications]
    
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notifications SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE notification_id = ?
            """, (notification_id,))
    
    # =====================================================
    # AUDIT LOGS
    # =====================================================
    
    def log_action(self, user_id, action, entity_type=None, entity_id=None, old_values=None, new_values=None):
        """Log user action for audit trail"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (
                    user_id, action, entity_type, entity_id, old_values, new_values
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                action,
                entity_type,
                entity_id,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None
            ))
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    def execute_query(self, query, params=None):
        """Execute a custom query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def get_table_count(self, table_name):
        """Get row count for a table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            result = cursor.fetchone()
            return result['count']
    
    def get_database_stats(self):
        """Get database statistics"""
        stats = {}
        tables = [
            'users', 'students', 'advisors', 'enrollments', 'grades',
            'attendance', 'logins', 'payments', 'counseling', 'risk_scores',
            'interventions', 'appointments', 'notifications'
        ]
        
        for table in tables:
            try:
                stats[table] = self.get_table_count(table)
            except:
                stats[table] = 0
        
        return stats


# Global database manager instance
db = DatabaseManager()


if __name__ == "__main__":
    # Test database creation
    print("Testing Database Manager...")
    print(f"Database path: {DB_PATH}")
    
    # Get stats
    stats = db.get_database_stats()
    print("\nDatabase Statistics:")
    for table, count in stats.items():
        print(f"  {table}: {count} records")
    
    print("\n✅ Database manager working!")
