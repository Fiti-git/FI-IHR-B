from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .models import JobPosting, JobApplication


class JobPostingModelTest(TestCase):
    """
    Test cases for JobPosting model
    """
    
    def setUp(self):
        """Set up test data"""
        self.job_data = {
            'job_provider_id': 1,
            'job_title': 'Software Engineer',
            'department': 'Engineering',
            'job_type': 'full-time',
            'work_location': 'New York, NY',
            'work_mode': 'hybrid',
            'role_overview': 'Develop and maintain software applications',
            'key_responsibilities': 'Code, test, debug applications',
            'required_qualifications': 'Bachelor\'s degree in Computer Science',
            'job_category': 'engineering',
            'hiring_manager': 'John Doe',
            'number_of_openings': 2
        }
    
    def test_job_posting_creation(self):
        """Test creating a job posting"""
        job = JobPosting.objects.create(**self.job_data)
        self.assertEqual(job.job_title, 'Software Engineer')
        self.assertEqual(job.department, 'Engineering')
        self.assertEqual(job.job_status, 'open')  # default status
        self.assertTrue(job.is_active)
    
    def test_job_posting_str_method(self):
        """Test string representation of job posting"""
        job = JobPosting.objects.create(**self.job_data)
        expected_str = f"{job.job_title} - {job.department}"
        self.assertEqual(str(job), expected_str)
    
    def test_salary_range_property(self):
        """Test salary range property"""
        job_data = self.job_data.copy()
        job_data.update({
            'salary_from': 80000,
            'salary_to': 120000,
            'currency': 'USD'
        })
        job = JobPosting.objects.create(**job_data)
        self.assertEqual(job.salary_range, 'USD 80,000 - 120,000')
    
    def test_is_active_property(self):
        """Test is_active property"""
        job = JobPosting.objects.create(**self.job_data)
        self.assertTrue(job.is_active)
        
        job.job_status = 'closed'
        job.save()
        self.assertFalse(job.is_active)
    
    def test_job_posting_ordering(self):
        """Test that job postings are ordered by date_posted descending"""
        job1 = JobPosting.objects.create(**self.job_data)
        
        job2_data = self.job_data.copy()
        job2_data['job_title'] = 'Senior Software Engineer'
        job2 = JobPosting.objects.create(**job2_data)
        
        jobs = JobPosting.objects.all()
        self.assertEqual(jobs.first(), job2)  # Most recent first


class JobApplicationModelTest(TestCase):
    """
    Test cases for JobApplication model
    """
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.freelancer = User.objects.create_user(
            username='freelancer1',
            email='freelancer@example.com',
            password='testpass123'
        )
        
        # Create test job posting
        self.job_data = {
            'job_provider_id': 1,
            'job_title': 'Python Developer',
            'department': 'Engineering',
            'job_type': 'full-time',
            'work_location': 'Remote',
            'work_mode': 'remote',
            'role_overview': 'Develop Python applications',
            'key_responsibilities': 'Code, test, deploy',
            'required_qualifications': 'Python experience',
            'job_category': 'engineering',
            'hiring_manager': 'Jane Smith',
            'number_of_openings': 1
        }
        self.job = JobPosting.objects.create(**self.job_data)
        
        # Test application data
        self.application_data = {
            'job': self.job,
            'freelancer': self.freelancer,
            'resume': 'https://example.com/resume.pdf',
            'cover_letter': 'I am interested in this position...',
            'expected_rate': 75.00
        }
    
    def test_job_application_creation(self):
        """Test creating a job application"""
        application = JobApplication.objects.create(**self.application_data)
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.freelancer, self.freelancer)
        self.assertEqual(application.status, 'pending')  # default status
        self.assertTrue(application.is_pending)
    
    def test_job_application_str_method(self):
        """Test string representation of job application"""
        application = JobApplication.objects.create(**self.application_data)
        expected_str = f"{self.freelancer.username} - {self.job.job_title}"
        self.assertEqual(str(application), expected_str)
    
    def test_application_status_properties(self):
        """Test status property methods"""
        application = JobApplication.objects.create(**self.application_data)
        
        # Test pending status
        self.assertTrue(application.is_pending)
        self.assertFalse(application.is_accepted)
        self.assertFalse(application.is_rejected)
        
        # Test accepted status
        application.status = 'accepted'
        application.save()
        self.assertFalse(application.is_pending)
        self.assertTrue(application.is_accepted)
        self.assertFalse(application.is_rejected)
        
        # Test rejected status
        application.status = 'rejected'
        application.save()
        self.assertFalse(application.is_pending)
        self.assertFalse(application.is_accepted)
        self.assertTrue(application.is_rejected)
    
    def test_unique_together_constraint(self):
        """Test that a freelancer can only apply once to the same job"""
        # Create first application
        JobApplication.objects.create(**self.application_data)
        
        # Try to create another application for the same job and freelancer
        with self.assertRaises(Exception):  # Should raise IntegrityError
            JobApplication.objects.create(**self.application_data)
    
    def test_application_ordering(self):
        """Test that applications are ordered by date_applied descending"""
        # Create second freelancer
        freelancer2 = User.objects.create_user(
            username='freelancer2',
            email='freelancer2@example.com',
            password='testpass123'
        )
        
        # Create applications
        app1 = JobApplication.objects.create(**self.application_data)
        
        app2_data = self.application_data.copy()
        app2_data['freelancer'] = freelancer2
        app2 = JobApplication.objects.create(**app2_data)
        
        applications = JobApplication.objects.all()
        self.assertEqual(applications.first(), app2)  # Most recent first
    
    def test_related_name_access(self):
        """Test accessing applications through job and freelancer relations"""
        application = JobApplication.objects.create(**self.application_data)
        
        # Test accessing applications through job
        job_applications = self.job.applications.all()
        self.assertIn(application, job_applications)
        
        # Test accessing applications through freelancer
        freelancer_applications = self.freelancer.job_applications.all()
        self.assertIn(application, freelancer_applications)