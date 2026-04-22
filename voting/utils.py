"""
Utility functions for the voting application
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string
from .models import OTPVerification, NotificationLog, VoteLog


def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(user, otp_code):
    """Send OTP via email"""
    import logging
    
    logger = logging.getLogger(__name__)
    
    subject = "Your E-Voting OTP Code"
    message = f"""
    Hello {user.first_name or user.username},
    
    Your OTP code is: {otp_code}
    
    This code will expire in 5 minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    E-Voting System Team
    """
    
    try:
        logger.info(f"Attempting to send OTP email to {user.email} from {settings.DEFAULT_FROM_EMAIL}")
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"OTP email sent successfully to {user.email}. Result: {result}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {str(e)}", exc_info=True)
        print(f"❌ Email Error: {str(e)}")
        return False


def create_otp_record(user, otp_type='email'):
    """Create an OTP record in database"""
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=5)
    
    otp_record = OTPVerification.objects.create(
        user=user,
        otp_type=otp_type,
        otp_code=otp_code,
        expires_at=expires_at
    )
    
    if otp_type == 'email':
        send_otp_email(user, otp_code)
    
    return otp_record


def verify_otp(user, otp_code, otp_type='email'):
    """Verify OTP code"""
    try:
        otp_record = OTPVerification.objects.get(
            user=user,
            otp_type=otp_type,
            is_verified=False
        )
        
        if otp_record.is_expired():
            return False, "OTP has expired"
        
        if otp_record.attempts >= settings.MAX_OTP_ATTEMPTS:
            return False, "Maximum attempts exceeded"
        
        if otp_record.otp_code != otp_code:
            otp_record.attempts += 1
            otp_record.save()
            return False, "Invalid OTP"
        
        otp_record.is_verified = True
        otp_record.verified_at = timezone.now()
        otp_record.save()
        
        return True, "OTP verified successfully"
    
    except OTPVerification.DoesNotExist:
        return False, "No valid OTP found"


def setup_totp(user):
    """Setup Time-based OTP for 2FA"""
    secret = pyotp.random_base32()
    user.otp_secret = secret
    user.save()
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp.provisioning_uri(name=user.email, issuer_name=settings.OTP_TOTP_ISSUER))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return secret, qr_code_base64


def verify_totp(user, token):
    """Verify TOTP token"""
    if not user.otp_secret:
        return False
    
    totp = pyotp.TOTP(user.otp_secret)
    return totp.verify(token)


def send_vote_confirmation_email(user, election, candidate):
    """Send vote confirmation email"""
    subject = f"Vote Confirmation - {election.title}"
    message = f"""
    Hello {user.first_name or user.username},
    
    Your vote has been successfully recorded for the {election.title} election.
    
    Candidate: {candidate.name}
    Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Your vote is secure and anonymous. Thank you for participating in the democratic process.
    
    Best regards,
    E-Voting System Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        # Log notification
        NotificationLog.objects.create(
            recipient=user,
            notification_type='email',
            subject=subject,
            message=message,
            status='sent',
            related_election=election
        )
        return True
    except Exception as e:
        print(f"Failed to send vote confirmation email: {str(e)}")
        NotificationLog.objects.create(
            recipient=user,
            notification_type='email',
            subject=subject,
            message=message,
            status='failed',
            related_election=election,
            error_message=str(e)
        )
        return False


def send_admin_notification(admin_user, subject, message, election=None):
    """Send notification to admin"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_user.email],
            fail_silently=False,
        )
        
        NotificationLog.objects.create(
            recipient=admin_user,
            notification_type='email',
            subject=subject,
            message=message,
            status='sent',
            related_election=election
        )
        return True
    except Exception as e:
        print(f"Failed to send admin notification: {str(e)}")
        return False


def create_vote_log(user, election, activity_type, description="", ip_address=None, user_agent=""):
    """Create a vote activity log"""
    VoteLog.objects.create(
        user=user,
        election=election,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    if not ip:
        return None

    ip = ip.strip()

    if ip.startswith('[') and ']:' in ip:
        ip = ip[1:ip.index(']')]
    elif ip.count(':') == 1:
        ip = ip.rsplit(':', 1)[0]

    return ip


def check_suspicious_activity(user, election, ip_address):
    """Check for suspicious voting activity"""
    from .models import Vote
    
    # Check if user has voted from different IPs in short time
    recent_votes = Vote.objects.filter(
        user=user,
        election=election,
        voted_at__gte=timezone.now() - timedelta(hours=1)
    ).values_list('ip_address', flat=True).distinct()
    
    if len(recent_votes) > 1 and ip_address not in recent_votes:
        return True
    
    return False


def is_bot_activity(ip_address, threshold=10):
    """Check if IP has suspicious bot-like activity"""
    from .models import CaptchaLog
    
    failed_attempts = CaptchaLog.objects.filter(
        ip_address=ip_address,
        is_passed=False,
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).count()
    
    return failed_attempts >= threshold


def get_election_stats(election):
    """Get statistics for an election"""
    from .models import Vote, VoteLog
    from django.db.models import Count
    
    total_votes = election.votes.count()
    total_voters = election.votes.values('user').distinct().count()
    
    candidates = election.candidates.annotate(
        vote_count=Count('votes')
    ).order_by('-vote_count')
    
    return {
        'total_votes': total_votes,
        'total_voters': total_voters,
        'candidates': candidates,
        'voter_turnout': f"{(total_voters / 100) * 100:.2f}%" if total_voters else "0%"
    }
