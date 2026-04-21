from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    """Enhanced user model with OTP and 2FA support"""
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    two_fa_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True)  # For TOTP
    otp_counter = models.IntegerField(default=0)  # For counter-based OTP
    failed_login_attempts = models.IntegerField(default=0)
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    language = models.CharField(
        max_length=10, 
        default='en',
        choices=[('en', 'English'), ('ne', 'Nepali')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'

    def __str__(self):
        return f"{self.username} ({self.email})"


class VoterProfile(models.Model):
    """Voter verification and profile information"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='voter_profile')
    unique_voter_id = models.CharField(max_length=50, unique=True)  # e.g., Citizenship number
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='pending'
    )
    verified_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_voters'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Voter Profile'
        verbose_name_plural = 'Voter Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.verification_status}"


class Election(models.Model):
    """Election model with enhanced features"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    allow_voting = models.BooleanField(default=True)  # Can disable voting while keeping results visible
    require_voter_verification = models.BooleanField(default=True)
    publish_results = models.BooleanField(default=False)  # Control when results are public
    max_attempts_allowed = models.IntegerField(default=3)
    created_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_elections'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = 'Election'
        verbose_name_plural = 'Elections'

    def __str__(self):
        return self.title

    def is_voting_open(self):
        """Check if voting is currently open"""
        now = timezone.now()
        return self.is_active and self.allow_voting and self.start_time <= now <= self.end_time

    def is_voting_closed(self):
        """Check if voting period has ended"""
        return timezone.now() > self.end_time

    def total_votes(self):
        """Get total votes cast"""
        return self.votes.count()


class Candidate(models.Model):
    """Enhanced candidate model with profile information"""
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    party = models.CharField(max_length=100, blank=True)
    symbol = models.CharField(max_length=50, blank=True)  # Party symbol
    manifesto = models.TextField(blank=True)
    biography = models.TextField(blank=True)
    photo = models.ImageField(upload_to='candidates/%Y/%m/%d/', null=True, blank=True)
    photo_url = models.URLField(blank=True)  # Fallback for external URLs
    position = models.IntegerField(default=0, help_text="Display order in voting form")
    is_independent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("election", "name")
        ordering = ["position", "name"]
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'

    def __str__(self):
        return f"{self.name} ({self.election.title})"

    def vote_count(self):
        """Get total votes for this candidate"""
        return self.votes.count()

    def vote_percentage(self, total_votes=None):
        """Calculate vote percentage"""
        if total_votes is None:
            total_votes = self.election.total_votes()
        if total_votes == 0:
            return 0
        return round((self.vote_count() / total_votes) * 100, 2)


class Vote(models.Model):
    """Vote model with enhanced tracking"""
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="votes")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="votes")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["election", "user"], name="unique_vote_per_user_per_election")
        ]
        ordering = ["-voted_at"]
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        indexes = [
            models.Index(fields=['election', 'user']),
            models.Index(fields=['voted_at']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.candidate.name}"


class VoteLog(models.Model):
    """Detailed log of voting activity for transparency and auditing"""
    ACTIVITY_TYPES = [
        ('login', 'User Login'),
        ('vote_attempted', 'Vote Attempt'),
        ('vote_submitted', 'Vote Submitted'),
        ('vote_verified', 'Vote Verified'),
        ('failed_verification', 'Failed Verification'),
        ('logout', 'User Logout'),
        ('profile_updated', 'Profile Updated'),
        ('email_verified', 'Email Verified'),
        ('2fa_enabled', '2FA Enabled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vote_logs')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='vote_logs', null=True, blank=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Vote Log'
        verbose_name_plural = 'Vote Logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['election', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"


class OTPVerification(models.Model):
    """OTP verification records"""
    OTP_TYPE_CHOICES = [
        ('email', 'Email OTP'),
        ('sms', 'SMS OTP'),
        ('totp', 'Time-based OTP'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otp_verifications')
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    otp_code = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'

    def __str__(self):
        return f"{self.user.username} - {self.otp_type}"

    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if OTP is still valid (not expired and not yet verified)"""
        return not self.is_expired() and not self.is_verified


class CaptchaLog(models.Model):
    """Log CAPTCHA attempts to detect bot activity"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='captcha_logs', null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    is_passed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'CAPTCHA Log'
        verbose_name_plural = 'CAPTCHA Logs'
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.ip_address} - {'Passed' if self.is_passed else 'Failed'} - {self.timestamp}"


class NotificationLog(models.Model):
    """Track sent notifications"""
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    related_election = models.ForeignKey(
        Election, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.subject} -> {self.recipient.username}"


class AuditLog(models.Model):
    """General audit logging for admin actions"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('publish', 'Publish'),
        ('verify', 'Verify'),
    ]
    
    admin_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['admin_user', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.admin_user} - {self.action_type} - {self.model_name}"
