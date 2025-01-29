from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator


class Project(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_projects'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_projects'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class Milestone(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payable_amount = models.DecimalField(
        default=0.00,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount to be paid for this milestone"
    )
    is_paid = models.BooleanField(default=False)
    
    @property
    def payment_status(self):
        latest_payment = self.payments.order_by('-uploaded_at').first()
        if not latest_payment:
            return 'No payment'
        return latest_payment.status
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    milestone = models.ForeignKey(
        Milestone, 
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_proof = models.ImageField(upload_to='payment_proofs/')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        'user.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='verified_payments'
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment for {self.milestone.title}"


class Task(models.Model):
    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('finalized', 'Finalized'),
        ('rejected', 'Rejected'),
    )
    
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE,
                                  related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='not_started')
    start_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def mark_as_started(self):
        if self.status == 'not_started':
            self.status = 'started'
            self.start_date = timezone.now()
            self.save()
    
    def mark_as_completed(self):
        if self.status == 'started':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            
    def approve_task(self):
        if self.status == 'completed':
            self.status = 'finalized'
            self.save()
            
    def reject_task(self):
        if self.status == 'completed':
            self.status = 'rejected'
            self.save()


class TaskNotification(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification for {self.task.title}"
    

class Document(models.Model):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='documents', null=True,
                                blank=True)
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,
                             related_name='documents', null=True, blank=True)
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='project_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title