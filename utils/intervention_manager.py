"""
Intervention Management System
==============================
Complete workflow for creating, tracking, and managing student interventions

Author: Team Infinite - Group 6
Date: 2025
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import db

class InterventionManager:
    """Manages all intervention operations"""
    
    def __init__(self):
        self.db = db
    
    # =====================================================
    # CREATE INTERVENTIONS
    # =====================================================
    
    def create_intervention(self, student_id, advisor_id, title, description, 
                          intervention_type_id=None, priority='Medium', 
                          scheduled_date=None, location=None, method='In-person',
                          follow_up_required=False, notes=None):
        """
        Create a new intervention
        
        Args:
            student_id: ID of student receiving intervention
            advisor_id: ID of advisor conducting intervention
            title: Intervention title
            description: Detailed description
            intervention_type_id: Type of intervention (optional)
            priority: Priority level (Critical, High, Medium, Low)
            scheduled_date: When intervention is scheduled
            location: Location of intervention
            method: Method (In-person, Virtual, Phone, Email)
            follow_up_required: Whether follow-up is needed
            notes: Additional notes
        
        Returns:
            int: intervention_id
        """
        intervention_id = self.db.create_intervention(
            student_id=student_id,
            advisor_id=advisor_id,
            title=title,
            description=description,
            intervention_type_id=intervention_type_id,
            priority=priority,
            status='Scheduled',
            scheduled_date=scheduled_date,
            location=location,
            method=method,
            follow_up_required=1 if follow_up_required else 0,
            notes=notes
        )
        
        # Create notification for student
        student = self.db.get_student_by_id(student_id)
        if student and student.get('user_id'):
            self.db.create_notification(
                user_id=student['user_id'],
                notification_type='intervention_scheduled',
                title=f'New Intervention Scheduled: {title}',
                message=f'An intervention has been scheduled with your advisor. Date: {scheduled_date or "TBD"}',
                priority=priority,
                related_entity_type='interventions',
                related_entity_id=intervention_id
            )
        
        # Log action
        self.db.log_action(advisor_id, 'INTERVENTION_CREATED', 'interventions', intervention_id)
        
        return intervention_id
    
    def create_from_template(self, student_id, advisor_id, template_id, scheduled_date=None):
        """
        Create intervention from template
        
        Args:
            student_id: Student ID
            advisor_id: Advisor ID
            template_id: Intervention type ID to use as template
            scheduled_date: When to schedule
        
        Returns:
            int: intervention_id
        """
        # Get template
        template = self.db.execute_query(
            "SELECT * FROM intervention_types WHERE intervention_type_id = ?",
            [template_id]
        )
        
        if not template:
            raise ValueError("Template not found")
        
        template = template[0]
        
        return self.create_intervention(
            student_id=student_id,
            advisor_id=advisor_id,
            title=template['type_name'],
            description=template['description'],
            intervention_type_id=template_id,
            priority=template['default_priority'],
            scheduled_date=scheduled_date,
            method='In-person'
        )
    
    # =====================================================
    # UPDATE INTERVENTIONS
    # =====================================================
    
    def update_status(self, intervention_id, new_status, notes=None):
        """
        Update intervention status
        
        Args:
            intervention_id: Intervention ID
            new_status: New status (Scheduled, In Progress, Completed, Cancelled, No-Show)
            notes: Additional notes
        
        Returns:
            bool: Success
        """
        update_data = {'status': new_status}
        
        if notes:
            # Append to existing notes
            intervention = self.db.execute_query(
                "SELECT notes FROM interventions WHERE intervention_id = ?",
                [intervention_id]
            )
            if intervention:
                existing_notes = intervention[0].get('notes', '')
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_data['notes'] = f"{existing_notes}\n\n[{timestamp}] Status changed to {new_status}\n{notes}"
        
        if new_status == 'Completed':
            update_data['completed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.db.update_intervention(intervention_id, **update_data)
        
        # Log action
        self.db.log_action(None, 'INTERVENTION_STATUS_UPDATED', 'interventions', intervention_id,
                          new_values={'status': new_status})
        
        return True
    
    def complete_intervention(self, intervention_id, outcome_assessment, 
                            success_rating, student_response=None, 
                            duration_minutes=None):
        """
        Mark intervention as completed with assessment
        
        Args:
            intervention_id: Intervention ID
            outcome_assessment: Assessment of outcome
            success_rating: Rating 1-5
            student_response: How student responded
            duration_minutes: Actual duration
        
        Returns:
            bool: Success
        """
        self.db.update_intervention(
            intervention_id,
            status='Completed',
            completed_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            outcome_assessment=outcome_assessment,
            success_rating=success_rating,
            student_response=student_response,
            duration_minutes=duration_minutes
        )
        
        # Get intervention details
        intervention = self.get_intervention_by_id(intervention_id)
        
        # Create notification for student
        if intervention:
            student = self.db.get_student_by_id(intervention['student_id'])
            if student and student.get('user_id'):
                self.db.create_notification(
                    user_id=student['user_id'],
                    notification_type='intervention_completed',
                    title='Intervention Completed',
                    message=f'Your intervention "{intervention["title"]}" has been completed. Please check the outcome notes.',
                    related_entity_type='interventions',
                    related_entity_id=intervention_id
                )
        
        return True
    
    def schedule_follow_up(self, intervention_id, follow_up_date, notes=None):
        """
        Schedule follow-up for intervention
        
        Args:
            intervention_id: Intervention ID
            follow_up_date: Date for follow-up
            notes: Follow-up notes
        """
        self.db.update_intervention(
            intervention_id,
            follow_up_required=1,
            follow_up_date=follow_up_date,
            notes=notes
        )
        
        return True
    
    # =====================================================
    # RETRIEVE INTERVENTIONS
    # =====================================================
    
    def get_intervention_by_id(self, intervention_id):
        """Get intervention by ID"""
        query = """
            SELECT 
                i.*,
                s.first_name || ' ' || s.last_name as student_name,
                s.email as student_email,
                s.classification as student_classification,
                a.first_name || ' ' || a.last_name as advisor_name,
                a.email as advisor_email,
                it.type_name as intervention_type_name,
                it.category as intervention_category
            FROM interventions i
            JOIN students s ON i.student_id = s.student_id
            JOIN advisors a ON i.advisor_id = a.advisor_id
            LEFT JOIN intervention_types it ON i.intervention_type_id = it.intervention_type_id
            WHERE i.intervention_id = ?
        """
        
        result = self.db.execute_query(query, [intervention_id])
        return result[0] if result else None
    
    def get_interventions_for_student(self, student_id, status=None):
        """Get all interventions for a student"""
        interventions = self.db.get_interventions(student_id=student_id, status=status)
        return interventions
    
    def get_interventions_for_advisor(self, advisor_id, status=None):
        """Get all interventions for an advisor"""
        interventions = self.db.get_interventions(advisor_id=advisor_id, status=status)
        return interventions
    
    def get_pending_interventions(self, advisor_id=None):
        """Get all pending interventions"""
        query = """
            SELECT 
                i.*,
                s.first_name || ' ' || s.last_name as student_name,
                s.classification as student_classification,
                rs.overall_risk_score,
                rs.risk_category
            FROM interventions i
            JOIN students s ON i.student_id = s.student_id
            LEFT JOIN risk_scores rs ON s.student_id = rs.student_id AND rs.is_current = 1
            WHERE i.status IN ('Scheduled', 'In Progress')
        """
        
        params = []
        if advisor_id:
            query += " AND i.advisor_id = ?"
            params.append(advisor_id)
        
        query += " ORDER BY i.priority DESC, i.scheduled_date ASC"
        
        return self.db.execute_query(query, params if params else None)
    
    def get_overdue_interventions(self, advisor_id=None):
        """Get interventions that are overdue"""
        query = """
            SELECT 
                i.*,
                s.first_name || ' ' || s.last_name as student_name
            FROM interventions i
            JOIN students s ON i.student_id = s.student_id
            WHERE i.status = 'Scheduled'
            AND i.scheduled_date < date('now')
        """
        
        params = []
        if advisor_id:
            query += " AND i.advisor_id = ?"
            params.append(advisor_id)
        
        return self.db.execute_query(query, params if params else None)
    
    def get_follow_ups_due(self, advisor_id=None):
        """Get interventions with follow-ups due"""
        query = """
            SELECT 
                i.*,
                s.first_name || ' ' || s.last_name as student_name
            FROM interventions i
            JOIN students s ON i.student_id = s.student_id
            WHERE i.follow_up_required = 1
            AND i.follow_up_date <= date('now', '+7 days')
            AND i.status = 'Completed'
        """
        
        params = []
        if advisor_id:
            query += " AND i.advisor_id = ?"
            params.append(advisor_id)
        
        return self.db.execute_query(query, params if params else None)
    
    # =====================================================
    # ANALYTICS
    # =====================================================
    
    def get_intervention_statistics(self, advisor_id=None, start_date=None, end_date=None):
        """
        Get intervention statistics
        
        Args:
            advisor_id: Filter by advisor
            start_date: Start date for filter
            end_date: End date for filter
        
        Returns:
            dict: Statistics
        """
        query = """
            SELECT 
                COUNT(*) as total_interventions,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'Scheduled' THEN 1 ELSE 0 END) as scheduled,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled,
                AVG(CASE WHEN success_rating IS NOT NULL THEN success_rating END) as avg_success_rating,
                AVG(CASE WHEN duration_minutes IS NOT NULL THEN duration_minutes END) as avg_duration,
                COUNT(DISTINCT student_id) as unique_students
            FROM interventions
            WHERE 1=1
        """
        
        params = []
        
        if advisor_id:
            query += " AND advisor_id = ?"
            params.append(advisor_id)
        
        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)
        
        result = self.db.execute_query(query, params if params else None)
        
        if result:
            stats = dict(result[0])
            
            # Calculate success rate
            if stats['completed'] > 0:
                stats['success_rate'] = (stats['avg_success_rating'] / 5 * 100) if stats['avg_success_rating'] else 0
            else:
                stats['success_rate'] = 0
            
            # Calculate completion rate
            if stats['total_interventions'] > 0:
                stats['completion_rate'] = (stats['completed'] / stats['total_interventions'] * 100)
            else:
                stats['completion_rate'] = 0
            
            return stats
        
        return {}
    
    def get_interventions_by_type(self, advisor_id=None):
        """Get intervention counts by type"""
        query = """
            SELECT 
                it.type_name,
                it.category,
                COUNT(*) as count,
                AVG(CASE WHEN i.success_rating IS NOT NULL THEN i.success_rating END) as avg_rating
            FROM interventions i
            LEFT JOIN intervention_types it ON i.intervention_type_id = it.intervention_type_id
            WHERE 1=1
        """
        
        params = []
        if advisor_id:
            query += " AND i.advisor_id = ?"
            params.append(advisor_id)
        
        query += " GROUP BY it.type_name, it.category ORDER BY count DESC"
        
        return self.db.execute_query(query, params if params else None)
    
    def get_interventions_by_priority(self, advisor_id=None):
        """Get intervention counts by priority"""
        query = """
            SELECT 
                priority,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM interventions
            WHERE 1=1
        """
        
        params = []
        if advisor_id:
            query += " AND advisor_id = ?"
            params.append(advisor_id)
        
        query += " GROUP BY priority ORDER BY count DESC"
        
        return self.db.execute_query(query, params if params else None)
    
    def get_monthly_intervention_trends(self, advisor_id=None, months=6):
        """Get intervention trends over time"""
        query = """
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM interventions
            WHERE created_at >= date('now', '-' || ? || ' months')
        """
        
        params = [months]
        
        if advisor_id:
            query += " AND advisor_id = ?"
            params.append(advisor_id)
        
        query += " GROUP BY month ORDER BY month"
        
        return self.db.execute_query(query, params)
    
    # =====================================================
    # TEMPLATES
    # =====================================================
    
    def get_intervention_types(self):
        """Get all intervention type templates"""
        return self.db.execute_query("""
            SELECT * FROM intervention_types WHERE is_active = 1 ORDER BY category, type_name
        """)
    
    def get_intervention_types_by_category(self):
        """Get intervention types grouped by category"""
        types = self.get_intervention_types()
        
        grouped = {}
        for itype in types:
            category = itype['category']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(itype)
        
        return grouped
    
    # =====================================================
    # BULK OPERATIONS
    # =====================================================
    
    def create_bulk_interventions(self, student_ids, advisor_id, intervention_type_id, 
                                 priority='Medium', scheduled_date=None):
        """
        Create interventions for multiple students
        
        Args:
            student_ids: List of student IDs
            advisor_id: Advisor ID
            intervention_type_id: Type of intervention
            priority: Priority level
            scheduled_date: When to schedule
        
        Returns:
            list: Created intervention IDs
        """
        # Get template
        template = self.db.execute_query(
            "SELECT * FROM intervention_types WHERE intervention_type_id = ?",
            [intervention_type_id]
        )
        
        if not template:
            raise ValueError("Template not found")
        
        template = template[0]
        
        intervention_ids = []
        
        for student_id in student_ids:
            intervention_id = self.create_intervention(
                student_id=student_id,
                advisor_id=advisor_id,
                title=template['type_name'],
                description=template['description'],
                intervention_type_id=intervention_type_id,
                priority=priority,
                scheduled_date=scheduled_date
            )
            intervention_ids.append(intervention_id)
        
        return intervention_ids


# Global intervention manager instance
intervention_manager = InterventionManager()
