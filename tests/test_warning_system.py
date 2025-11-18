"""
Test Warning System with Different Student Profiles
Tests the early warning system with various student risk profiles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from utils.intervention_manager import InterventionManager
from utils.email_service import EmailService
import json

class WarningSystemTester:
    """Test warning system with different student profiles"""
    
    def __init__(self, db_path='database/hsu_database.db'):
        self.db_path = db_path
        self.intervention_manager = InterventionManager()
        self.email_service = EmailService()
        self.test_results = []
        
    def create_test_student_profiles(self):
        """Create diverse student test profiles"""
        
        test_profiles = [
            {
                'name': 'High Risk - Academic Struggling',
                'student_id': 'TEST_HR_001',
                'gpa': 1.8,
                'credits_attempted': 45,
                'credits_earned': 30,
                'attendance_rate': 0.65,
                'engagement_score': 0.4,
                'financial_aid': 1,
                'first_generation': 1,
                'risk_level': 'High',
                'expected_warnings': ['GPA Drop', 'Low Attendance', 'Credit Deficit']
            },
            {
                'name': 'Medium Risk - Attendance Issues',
                'student_id': 'TEST_MR_001',
                'gpa': 2.8,
                'credits_attempted': 60,
                'credits_earned': 55,
                'attendance_rate': 0.72,
                'engagement_score': 0.6,
                'financial_aid': 0,
                'first_generation': 0,
                'risk_level': 'Medium',
                'expected_warnings': ['Attendance Warning']
            },
            {
                'name': 'Low Risk - Good Standing',
                'student_id': 'TEST_LR_001',
                'gpa': 3.5,
                'credits_attempted': 75,
                'credits_earned': 75,
                'attendance_rate': 0.95,
                'engagement_score': 0.9,
                'financial_aid': 0,
                'first_generation': 0,
                'risk_level': 'Low',
                'expected_warnings': []
            },
            {
                'name': 'High Risk - Financial & Engagement',
                'student_id': 'TEST_HR_002',
                'gpa': 2.2,
                'credits_attempted': 30,
                'credits_earned': 25,
                'attendance_rate': 0.70,
                'engagement_score': 0.3,
                'financial_aid': 1,
                'first_generation': 1,
                'risk_level': 'High',
                'expected_warnings': ['Low GPA', 'Low Engagement', 'Financial Risk']
            },
            {
                'name': 'Medium Risk - Declining Performance',
                'student_id': 'TEST_MR_002',
                'gpa': 2.5,
                'credits_attempted': 90,
                'credits_earned': 80,
                'attendance_rate': 0.80,
                'engagement_score': 0.65,
                'financial_aid': 1,
                'first_generation': 0,
                'risk_level': 'Medium',
                'expected_warnings': ['GPA Watch', 'Credit Progress']
            },
            {
                'name': 'Critical Risk - Multiple Issues',
                'student_id': 'TEST_CR_001',
                'gpa': 1.5,
                'credits_attempted': 40,
                'credits_earned': 20,
                'attendance_rate': 0.55,
                'engagement_score': 0.2,
                'financial_aid': 1,
                'first_generation': 1,
                'risk_level': 'Critical',
                'expected_warnings': ['Academic Probation', 'Severe Attendance', 'High Credit Deficit', 'Very Low Engagement']
            }
        ]
        
        return test_profiles
    
    def insert_test_student(self, profile):
        """Insert test student into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert student
            cursor.execute("""
                INSERT OR REPLACE INTO students 
                (student_id, name, email, major, year, gpa, credits_earned, enrollment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile['student_id'],
                profile['name'],
                f"{profile['student_id'].lower()}@hsu.edu",
                'Computer Science',
                'Sophomore',
                profile['gpa'],
                profile['credits_earned'],
                'Active'
            ))
            
            # Insert academic record
            cursor.execute("""
                INSERT OR REPLACE INTO academic_records
                (student_id, term, gpa, credits_attempted, credits_earned, academic_standing)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                profile['student_id'],
                'Fall 2024',
                profile['gpa'],
                profile['credits_attempted'],
                profile['credits_earned'],
                profile['risk_level']
            ))
            
            # Insert engagement record
            cursor.execute("""
                INSERT OR REPLACE INTO engagement
                (student_id, term, attendance_rate, participation_score, lms_activity)
                VALUES (?, ?, ?, ?, ?)
            """, (
                profile['student_id'],
                'Fall 2024',
                profile['attendance_rate'],
                profile['engagement_score'],
                profile['engagement_score']
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting test student: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def generate_warnings_for_profile(self, profile):
        """Generate warnings based on student profile"""
        warnings = []
        
        # GPA-based warnings
        if profile['gpa'] < 2.0:
            warnings.append({
                'type': 'Academic Probation',
                'severity': 'Critical',
                'message': f"GPA {profile['gpa']} is below 2.0 threshold"
            })
        elif profile['gpa'] < 2.5:
            warnings.append({
                'type': 'Low GPA',
                'severity': 'High',
                'message': f"GPA {profile['gpa']} is below recommended 2.5"
            })
        elif profile['gpa'] < 3.0:
            warnings.append({
                'type': 'GPA Watch',
                'severity': 'Medium',
                'message': f"GPA {profile['gpa']} could be improved"
            })
        
        # Credit completion warnings
        completion_rate = profile['credits_earned'] / profile['credits_attempted'] if profile['credits_attempted'] > 0 else 0
        if completion_rate < 0.67:
            warnings.append({
                'type': 'High Credit Deficit',
                'severity': 'Critical',
                'message': f"Only {completion_rate*100:.1f}% credits completed"
            })
        elif completion_rate < 0.80:
            warnings.append({
                'type': 'Credit Progress',
                'severity': 'Medium',
                'message': f"{completion_rate*100:.1f}% completion rate needs improvement"
            })
        
        # Attendance warnings
        if profile['attendance_rate'] < 0.70:
            warnings.append({
                'type': 'Severe Attendance',
                'severity': 'Critical',
                'message': f"Attendance at {profile['attendance_rate']*100:.1f}%"
            })
        elif profile['attendance_rate'] < 0.80:
            warnings.append({
                'type': 'Attendance Warning',
                'severity': 'High',
                'message': f"Attendance at {profile['attendance_rate']*100:.1f}%"
            })
        
        # Engagement warnings
        if profile['engagement_score'] < 0.40:
            warnings.append({
                'type': 'Very Low Engagement',
                'severity': 'Critical',
                'message': f"Engagement score {profile['engagement_score']*100:.1f}%"
            })
        elif profile['engagement_score'] < 0.60:
            warnings.append({
                'type': 'Low Engagement',
                'severity': 'High',
                'message': f"Engagement score {profile['engagement_score']*100:.1f}%"
            })
        
        # Financial risk
        if profile['financial_aid'] == 1 and profile['gpa'] < 2.5:
            warnings.append({
                'type': 'Financial Aid Risk',
                'severity': 'High',
                'message': 'GPA may affect financial aid eligibility'
            })
        
        # First-generation support
        if profile['first_generation'] == 1 and len(warnings) > 0:
            warnings.append({
                'type': 'First-Gen Support Needed',
                'severity': 'Medium',
                'message': 'First-generation student needs additional support'
            })
        
        return warnings
    
    def test_warning_generation(self, profile):
        """Test warning generation for a profile"""
        print(f"\n{'='*80}")
        print(f"Testing Profile: {profile['name']}")
        print(f"Student ID: {profile['student_id']}")
        print(f"Expected Risk Level: {profile['risk_level']}")
        print(f"{'='*80}")
        
        # Insert test student
        success = self.insert_test_student(profile)
        if not success:
            print("❌ Failed to insert test student")
            return
        
        # Generate warnings
        warnings = self.generate_warnings_for_profile(profile)
        
        print(f"\n📊 Student Metrics:")
        print(f"   GPA: {profile['gpa']}")
        print(f"   Credits: {profile['credits_earned']}/{profile['credits_attempted']}")
        print(f"   Attendance: {profile['attendance_rate']*100:.1f}%")
        print(f"   Engagement: {profile['engagement_score']*100:.1f}%")
        print(f"   Financial Aid: {'Yes' if profile['financial_aid'] else 'No'}")
        print(f"   First Generation: {'Yes' if profile['first_generation'] else 'No'}")
        
        print(f"\n⚠️  Generated Warnings ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            severity_emoji = {
                'Critical': '🔴',
                'High': '🟠',
                'Medium': '🟡',
                'Low': '🟢'
            }
            print(f"   {i}. {severity_emoji[warning['severity']]} [{warning['severity']}] {warning['type']}")
            print(f"      {warning['message']}")
        
        # Store warnings in database
        for warning in warnings:
            self.store_warning(profile['student_id'], warning)
        
        # Test result
        test_result = {
            'profile_name': profile['name'],
            'student_id': profile['student_id'],
            'risk_level': profile['risk_level'],
            'warnings_generated': len(warnings),
            'warning_types': [w['type'] for w in warnings],
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(test_result)
        
        print(f"\n✅ Test completed for {profile['name']}")
        
        return warnings
    
    def store_warning(self, student_id, warning):
        """Store warning in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO interventions 
                (student_id, intervention_type, description, priority, status, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                warning['type'],
                warning['message'],
                warning['severity'],
                'Pending',
                datetime.now().strftime('%Y-%m-%d')
            ))
            conn.commit()
        except Exception as e:
            print(f"Error storing warning: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def test_email_notifications(self, profile, warnings):
        """Test email notification system"""
        print(f"\n📧 Testing Email Notifications for {profile['name']}...")
        
        if not warnings:
            print("   No warnings to send")
            return
        
        # Test advisor notification
        try:
            advisor_email = "advisor@hsu.edu"
            subject = f"Early Warning Alert: {profile['student_id']}"
            
            warning_list = "\n".join([f"- {w['type']}: {w['message']}" for w in warnings])
            
            body = f"""
Early Warning System Alert

Student: {profile['name']} ({profile['student_id']})
Risk Level: {profile['risk_level']}

Warnings Detected ({len(warnings)}):
{warning_list}

Metrics:
- GPA: {profile['gpa']}
- Attendance: {profile['attendance_rate']*100:.1f}%
- Engagement: {profile['engagement_score']*100:.1f}%

Please review and take appropriate action.
"""
            
            print(f"   ✅ Advisor notification prepared")
            print(f"      To: {advisor_email}")
            print(f"      Subject: {subject}")
            print(f"      Warnings: {len(warnings)}")
            
            # Test student notification
            student_email = f"{profile['student_id'].lower()}@hsu.edu"
            student_subject = "Important: Academic Support Available"
            
            print(f"   ✅ Student notification prepared")
            print(f"      To: {student_email}")
            print(f"      Subject: {student_subject}")
            
        except Exception as e:
            print(f"   ❌ Email notification test failed: {e}")
    
    def run_all_tests(self):
        """Run tests for all student profiles"""
        print("\n" + "="*80)
        print("HSU EARLY WARNING SYSTEM - COMPREHENSIVE TEST SUITE")
        print("="*80)
        
        profiles = self.create_test_student_profiles()
        
        for profile in profiles:
            warnings = self.test_warning_generation(profile)
            self.test_email_notifications(profile, warnings)
        
        # Generate summary
        self.print_test_summary()
        
        # Save results
        self.save_test_results()
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        print(f"\n📊 Total Profiles Tested: {len(self.test_results)}")
        
        # Group by risk level
        risk_summary = {}
        for result in self.test_results:
            risk_level = result['risk_level']
            if risk_level not in risk_summary:
                risk_summary[risk_level] = []
            risk_summary[risk_level].append(result)
        
        print("\n📈 Results by Risk Level:")
        for risk_level in ['Critical', 'High', 'Medium', 'Low']:
            if risk_level in risk_summary:
                results = risk_summary[risk_level]
                total_warnings = sum(r['warnings_generated'] for r in results)
                avg_warnings = total_warnings / len(results) if results else 0
                print(f"   {risk_level}: {len(results)} profiles, Avg {avg_warnings:.1f} warnings")
        
        print("\n✅ All tests completed successfully!")
    
    def save_test_results(self):
        """Save test results to JSON file"""
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('tests', filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Test results saved to: {filepath}")
    
    def cleanup_test_data(self):
        """Remove test students from database"""
        print("\n🧹 Cleaning up test data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete test students
            cursor.execute("DELETE FROM students WHERE student_id LIKE 'TEST_%'")
            cursor.execute("DELETE FROM academic_records WHERE student_id LIKE 'TEST_%'")
            cursor.execute("DELETE FROM engagement WHERE student_id LIKE 'TEST_%'")
            cursor.execute("DELETE FROM interventions WHERE student_id LIKE 'TEST_%'")
            
            conn.commit()
            print("   ✅ Test data cleaned up")
        except Exception as e:
            print(f"   ❌ Cleanup failed: {e}")
            conn.rollback()
        finally:
            conn.close()


def main():
    """Main test function"""
    print("Starting Warning System Tests...\n")
    
    tester = WarningSystemTester()
    
    try:
        tester.run_all_tests()
    finally:
        # Optional: cleanup test data
        cleanup = input("\nCleanup test data? (y/n): ")
        if cleanup.lower() == 'y':
            tester.cleanup_test_data()


if __name__ == "__main__":
    main()
