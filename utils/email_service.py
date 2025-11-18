"""
Email Notification Service
===========================
Handles all email notifications for the HSU Early Warning System

Author: Team Infinite - Group 6
Date: 2025
"""

import sys
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import db

logger = logging.getLogger(__name__)

# Email configuration
# In production, these should be environment variables
EMAIL_CONFIG = {
    'enabled': False,  # Set to True when email is configured
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'noreply@hsu.edu',
    'sender_name': 'HSU Early Warning System',
    'password': ''  # Use environment variable in production
}


class EmailService:
    """Manages email notifications"""
    
    def __init__(self, config=EMAIL_CONFIG):
        self.config = config
        self.enabled = config['enabled']
    
    def send_email(self, to_email, subject, body_html, body_text=None, cc_email=None, priority=3):
        """
        Send email
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text fallback
            cc_email: CC email address
            priority: Priority level (1-5, 5 is highest)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.enabled:
            # Queue email for later sending
            self._queue_email(to_email, subject, body_html, body_text, cc_email, priority)
            logger.info(f"Email queued (service disabled): {subject} to {to_email}")
            return True, "Email queued"
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc_email:
                msg['Cc'] = cc_email
            
            # Add body
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], self.config['password'])
                server.send_message(msg)
            
            logger.info(f"Email sent: {subject} to {to_email}")
            return True, "Email sent successfully"
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            # Queue for retry
            self._queue_email(to_email, subject, body_html, body_text, cc_email, priority)
            return False, f"Email failed: {str(e)}"
    
    def _queue_email(self, to_email, subject, body_html, body_text, cc_email, priority):
        """Queue email for later sending"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO email_queue (
                    to_email, cc_email, subject, body_html, body_text, priority, status
                ) VALUES (?, ?, ?, ?, ?, ?, 'Pending')
            """, (to_email, cc_email, subject, body_html, body_text, priority))
    
    # =====================================================
    # NOTIFICATION TEMPLATES
    # =====================================================
    
    def send_welcome_email(self, user_email, user_name, role):
        """Send welcome email to new user"""
        subject = "Welcome to HSU Early Warning System"
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #003366;">Welcome to HSU Early Warning System!</h2>
                    
                    <p>Hi {user_name},</p>
                    
                    <p>Your account has been successfully created with the role of <strong>{role.title()}</strong>.</p>
                    
                    <p>You can now log in to access the system:</p>
                    <ul>
                        <li>Email: {user_email}</li>
                        <li>Portal: <a href="http://localhost:8501">HSU Early Warning System</a></li>
                    </ul>
                    
                    <p>If you have any questions, please contact your advisor or system administrator.</p>
                    
                    <p>Best regards,<br>
                    HSU Early Warning System Team</p>
                    
                    <hr style="border: 1px solid #ddd; margin-top: 30px;">
                    <p style="font-size: 12px; color: #888;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        body_text = f"""
        Welcome to HSU Early Warning System!
        
        Hi {user_name},
        
        Your account has been successfully created with the role of {role.title()}.
        
        Email: {user_email}
        
        You can now log in to access the system at: http://localhost:8501
        
        Best regards,
        HSU Early Warning System Team
        """
        
        return self.send_email(user_email, subject, body_html, body_text)
    
    def send_intervention_scheduled_email(self, student_email, student_name, advisor_name, 
                                        intervention_title, scheduled_date, location, method):
        """Send email when intervention is scheduled"""
        subject = f"Intervention Scheduled: {intervention_title}"
        
        date_str = scheduled_date.strftime('%B %d, %Y at %I:%M %p') if scheduled_date else 'TBD'
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #003366;">Intervention Scheduled</h2>
                    
                    <p>Hi {student_name},</p>
                    
                    <p>An intervention has been scheduled to help support your academic success:</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Intervention:</strong> {intervention_title}</p>
                        <p><strong>Advisor:</strong> {advisor_name}</p>
                        <p><strong>Date/Time:</strong> {date_str}</p>
                        <p><strong>Location:</strong> {location or 'TBD'}</p>
                        <p><strong>Method:</strong> {method}</p>
                    </div>
                    
                    <p>Please make sure to attend this session. If you need to reschedule, contact your advisor as soon as possible.</p>
                    
                    <p>Best regards,<br>
                    HSU Academic Advising</p>
                </div>
            </body>
        </html>
        """
        
        body_text = f"""
        Intervention Scheduled
        
        Hi {student_name},
        
        An intervention has been scheduled:
        
        Intervention: {intervention_title}
        Advisor: {advisor_name}
        Date/Time: {date_str}
        Location: {location or 'TBD'}
        Method: {method}
        
        Please attend this session. Contact your advisor if you need to reschedule.
        
        Best regards,
        HSU Academic Advising
        """
        
        return self.send_email(student_email, subject, body_html, body_text, priority=4)
    
    def send_high_risk_alert(self, advisor_email, advisor_name, student_name, student_id, 
                           risk_score, risk_factors):
        """Send alert when student becomes high risk"""
        subject = f"HIGH RISK ALERT: {student_name} (ID: {student_id})"
        
        factors_html = "<ul>"
        for factor, value in risk_factors.items():
            factors_html += f"<li><strong>{factor}:</strong> {value:.2%}</li>"
        factors_html += "</ul>"
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #DC2626;">🚨 HIGH RISK ALERT</h2>
                    
                    <p>Hi {advisor_name},</p>
                    
                    <p>A student in your caseload has been flagged as <strong style="color: #DC2626;">HIGH RISK</strong>:</p>
                    
                    <div style="background: #FEE2E2; padding: 15px; border-left: 4px solid #DC2626; margin: 20px 0;">
                        <p><strong>Student:</strong> {student_name}</p>
                        <p><strong>Student ID:</strong> {student_id}</p>
                        <p><strong>Overall Risk Score:</strong> {risk_score:.1%}</p>
                    </div>
                    
                    <h3>Risk Factors:</h3>
                    {factors_html}
                    
                    <p><strong>Recommended Actions:</strong></p>
                    <ul>
                        <li>Schedule an immediate intervention meeting</li>
                        <li>Review recent academic performance</li>
                        <li>Check engagement metrics (LMS activity, attendance)</li>
                        <li>Assess financial and wellness concerns</li>
                    </ul>
                    
                    <p><a href="http://localhost:8501" style="background: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Student Profile</a></p>
                    
                    <p>Please take action within 48 hours.</p>
                    
                    <p>Best regards,<br>
                    HSU Early Warning System</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(advisor_email, subject, body_html, priority=5)
    
    def send_intervention_reminder(self, advisor_email, advisor_name, student_name, 
                                  intervention_title, scheduled_date, location):
        """Send reminder before intervention"""
        subject = f"Reminder: Intervention Tomorrow - {student_name}"
        
        date_str = scheduled_date.strftime('%B %d, %Y at %I:%M %p')
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #003366;">📅 Intervention Reminder</h2>
                    
                    <p>Hi {advisor_name},</p>
                    
                    <p>This is a reminder about your intervention scheduled for tomorrow:</p>
                    
                    <div style="background: #DBEAFE; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Student:</strong> {student_name}</p>
                        <p><strong>Intervention:</strong> {intervention_title}</p>
                        <p><strong>Date/Time:</strong> {date_str}</p>
                        <p><strong>Location:</strong> {location}</p>
                    </div>
                    
                    <p>Please review the student's profile before the meeting.</p>
                    
                    <p><a href="http://localhost:8501" style="background: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Student Profile</a></p>
                    
                    <p>Best regards,<br>
                    HSU Early Warning System</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(advisor_email, subject, body_html, priority=4)
    
    def send_password_reset_email(self, user_email, user_name, reset_token):
        """Send password reset email"""
        subject = "Password Reset Request - HSU Early Warning System"
        
        reset_link = f"http://localhost:8501/reset_password?token={reset_token}"
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #003366;">Password Reset Request</h2>
                    
                    <p>Hi {user_name},</p>
                    
                    <p>We received a request to reset your password for the HSU Early Warning System.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <p><a href="{reset_link}" style="background: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">Reset Password</a></p>
                    
                    <p>This link will expire in 24 hours.</p>
                    
                    <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
                    
                    <p>Best regards,<br>
                    HSU Early Warning System Team</p>
                    
                    <hr style="border: 1px solid #ddd; margin-top: 30px;">
                    <p style="font-size: 12px; color: #888;">
                        For security reasons, this link will expire in 24 hours.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body_html, priority=5)
    
    def send_weekly_summary(self, advisor_email, advisor_name, stats):
        """Send weekly summary to advisor"""
        subject = f"Weekly Summary - {datetime.now().strftime('%B %d, %Y')}"
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #003366;">📊 Weekly Activity Summary</h2>
                    
                    <p>Hi {advisor_name},</p>
                    
                    <p>Here's your weekly summary for the week ending {datetime.now().strftime('%B %d, %Y')}:</p>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3>Interventions</h3>
                        <ul>
                            <li>Completed: {stats.get('interventions_completed', 0)}</li>
                            <li>Scheduled: {stats.get('interventions_scheduled', 0)}</li>
                            <li>Overdue: {stats.get('interventions_overdue', 0)}</li>
                        </ul>
                        
                        <h3>At-Risk Students</h3>
                        <ul>
                            <li>High Risk: {stats.get('high_risk_students', 0)}</li>
                            <li>Medium Risk: {stats.get('medium_risk_students', 0)}</li>
                            <li>New Alerts: {stats.get('new_alerts', 0)}</li>
                        </ul>
                    </div>
                    
                    <p><a href="http://localhost:8501" style="background: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Dashboard</a></p>
                    
                    <p>Best regards,<br>
                    HSU Early Warning System</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(advisor_email, subject, body_html, priority=3)
    
    # =====================================================
    # BATCH OPERATIONS
    # =====================================================
    
    def process_email_queue(self, limit=10):
        """Process pending emails from queue"""
        if not self.enabled:
            logger.info("Email service disabled, skipping queue processing")
            return 0
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get pending emails
            cursor.execute("""
                SELECT * FROM email_queue
                WHERE status = 'Pending' AND retry_count < 3
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            """, (limit,))
            
            emails = cursor.fetchall()
            
            sent_count = 0
            
            for email in emails:
                success, message = self.send_email(
                    email['to_email'],
                    email['subject'],
                    email['body_html'],
                    email['body_text'],
                    email['cc_email']
                )
                
                if success:
                    # Mark as sent
                    cursor.execute("""
                        UPDATE email_queue
                        SET status = 'Sent', sent_at = CURRENT_TIMESTAMP
                        WHERE email_id = ?
                    """, (email['email_id'],))
                    sent_count += 1
                else:
                    # Increment retry count
                    cursor.execute("""
                        UPDATE email_queue
                        SET retry_count = retry_count + 1, error_message = ?
                        WHERE email_id = ?
                    """, (message, email['email_id']))
            
            return sent_count


# Global email service instance
email_service = EmailService()
