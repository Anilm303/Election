"""
REST API views for the voting application
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count
import json

from .models import (
    Election, Candidate, Vote, CustomUser, VoterProfile,
    VoteLog, NotificationLog, AuditLog
)
from .utils import (
    create_otp_record, verify_otp, send_vote_confirmation_email,
    get_client_ip, create_vote_log, get_election_stats
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with email/username support"""
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Try authentication with username or email
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Try with email
            try:
                user_obj = CustomUser.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
        })


class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for elections"""
    queryset = Election.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Get only active elections
        return Election.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get election results"""
        election = self.get_object()
        
        # Check if results should be published
        if not election.publish_results and not request.user.is_staff:
            return Response(
                {'detail': 'Results not yet published'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        candidates = election.candidates.annotate(
            vote_count=Count('votes')
        ).order_by('-vote_count')
        
        total_votes = election.total_votes()
        
        data = {
            'election_id': election.id,
            'election_title': election.title,
            'total_votes': total_votes,
            'candidates': [
                {
                    'id': c.id,
                    'name': c.name,
                    'party': c.party,
                    'votes': c.vote_count,
                    'percentage': c.vote_percentage(total_votes),
                }
                for c in candidates
            ]
        }
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get election status"""
        election = self.get_object()
        
        now = timezone.now()
        if now < election.start_time:
            status_text = 'Upcoming'
        elif now > election.end_time:
            status_text = 'Closed'
        else:
            status_text = 'Active'
        
        return Response({
            'election_id': election.id,
            'title': election.title,
            'status': status_text,
            'start_time': election.start_time,
            'end_time': election.end_time,
            'allow_voting': election.allow_voting,
            'total_votes': election.total_votes(),
        })


class CandidateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for candidates"""
    queryset = Candidate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        election_id = self.request.query_params.get('election_id')
        if election_id:
            return Candidate.objects.filter(election_id=election_id)
        return Candidate.objects.all()
    
    @action(detail=True, methods=['get'])
    def vote_count(self, request, pk=None):
        """Get vote count for a candidate"""
        candidate = self.get_object()
        election = candidate.election
        
        if not election.publish_results and not request.user.is_staff:
            return Response(
                {'detail': 'Results not yet published'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({
            'candidate_id': candidate.id,
            'name': candidate.name,
            'votes': candidate.vote_count(),
            'percentage': candidate.vote_percentage(),
        })


class VoteViewSet(viewsets.ModelViewSet):
    """ViewSet for voting"""
    queryset = Vote.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Vote.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Submit a vote"""
        user = request.user
        election_id = request.data.get('election_id')
        candidate_id = request.data.get('candidate_id')
        
        # Validate election
        election = get_object_or_404(Election, id=election_id, is_active=True)
        
        # Check if voting is open
        if not election.is_voting_open():
            return Response(
                {'detail': 'Voting is not currently open for this election'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check voter verification if required
        if election.require_voter_verification:
            try:
                voter_profile = user.voter_profile
                if voter_profile.verification_status != 'verified':
                    return Response(
                        {'detail': 'Your voter profile is not verified'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except VoterProfile.DoesNotExist:
                return Response(
                    {'detail': 'Please complete your voter profile first'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if user already voted
        if Vote.objects.filter(election=election, user=user).exists():
            return Response(
                {'detail': 'You have already voted in this election'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get candidate
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)
        
        # Get client IP and user agent
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create vote
        vote = Vote.objects.create(
            election=election,
            candidate=candidate,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Log voting activity
        create_vote_log(
            user, election, 'vote_submitted',
            f'Voted for {candidate.name}',
            ip_address, user_agent
        )
        
        # Send confirmation email
        send_vote_confirmation_email(user, election, candidate)
        
        return Response({
            'vote_id': vote.id,
            'message': 'Vote submitted successfully',
            'timestamp': vote.voted_at
        }, status=status.HTTP_201_CREATED)


class VoterProfileViewSet(viewsets.ViewSet):
    """ViewSet for voter profile"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get current user's voter profile"""
        try:
            profile = request.user.voter_profile
            return Response({
                'user_id': profile.user.id,
                'unique_voter_id': profile.unique_voter_id,
                'verification_status': profile.verification_status,
                'date_of_birth': profile.date_of_birth,
                'gender': profile.gender,
            })
        except VoterProfile.DoesNotExist:
            return Response(
                {'detail': 'Voter profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request):
        """Create or update voter profile"""
        user = request.user
        
        data = request.data
        
        voter_profile, created = VoterProfile.objects.get_or_create(
            user=user,
            defaults={
                'unique_voter_id': data.get('unique_voter_id'),
                'date_of_birth': data.get('date_of_birth'),
                'gender': data.get('gender'),
                'address': data.get('address', ''),
                'contact_number': data.get('contact_number', ''),
            }
        )
        
        if not created:
            # Update existing profile
            voter_profile.unique_voter_id = data.get('unique_voter_id', voter_profile.unique_voter_id)
            voter_profile.date_of_birth = data.get('date_of_birth', voter_profile.date_of_birth)
            voter_profile.gender = data.get('gender', voter_profile.gender)
            voter_profile.address = data.get('address', voter_profile.address)
            voter_profile.contact_number = data.get('contact_number', voter_profile.contact_number)
            voter_profile.save()
        
        return Response({
            'message': 'Voter profile created/updated successfully',
            'verification_status': voter_profile.verification_status
        })


class OTPViewSet(viewsets.ViewSet):
    """ViewSet for OTP operations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request):
        """Request OTP"""
        user = request.user
        otp_type = request.data.get('otp_type', 'email')
        
        if otp_type not in ['email', 'sms']:
            return Response(
                {'detail': 'Invalid OTP type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create OTP record
        otp_record = create_otp_record(user, otp_type)
        
        return Response({
            'message': f'OTP sent via {otp_type}',
            'otp_id': otp_record.id,
        })
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify OTP"""
        user = request.user
        otp_code = request.data.get('otp_code')
        otp_type = request.data.get('otp_type', 'email')
        
        success, message = verify_otp(user, otp_code, otp_type)
        
        if success:
            user.email_verified = True
            user.save()
            
            return Response({
                'message': message,
                'verified': True
            })
        
        return Response(
            {'message': message, 'verified': False},
            status=status.HTTP_400_BAD_REQUEST
        )


class VoteLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for vote logs (audit trail)"""
    queryset = VoteLog.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        election_id = self.request.query_params.get('election_id')
        
        queryset = VoteLog.objects.filter(user=user)
        
        if election_id:
            queryset = queryset.filter(election_id=election_id)
        
        return queryset.order_by('-timestamp')


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notifications"""
    queryset = NotificationLog.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NotificationLog.objects.filter(recipient=self.request.user)
