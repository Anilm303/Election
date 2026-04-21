"""
Serializers for the voting application REST API
"""
from rest_framework import serializers
from .models import (
    Election, Candidate, Vote, CustomUser, VoterProfile,
    VoteLog, NotificationLog, OTPVerification
)


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'email_verified', 'two_fa_enabled', 'language']
        read_only_fields = ['id', 'email_verified']


class VoterProfileSerializer(serializers.ModelSerializer):
    """Serializer for VoterProfile model"""
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = VoterProfile
        fields = ['id', 'user', 'unique_voter_id', 'date_of_birth', 'gender',
                 'verification_status', 'verified_at', 'address', 'contact_number']
        read_only_fields = ['id', 'verification_status', 'verified_at']


class CandidateSerializer(serializers.ModelSerializer):
    """Serializer for Candidate model"""
    vote_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['id', 'election', 'name', 'email', 'phone', 'party', 
                 'symbol', 'biography', 'manifesto', 'photo', 'position',
                 'is_independent', 'vote_count']
    
    def get_vote_count(self, obj):
        return obj.votes.count()


class ElectionSerializer(serializers.ModelSerializer):
    """Serializer for Election model"""
    candidates = CandidateSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    
    class Meta:
        model = Election
        fields = ['id', 'title', 'description', 'start_time', 'end_time',
                 'is_active', 'allow_voting', 'publish_results',
                 'require_voter_verification', 'candidates', 'total_votes']
    
    def get_total_votes(self, obj):
        return obj.total_votes()


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Vote model"""
    election_title = serializers.CharField(source='election.title', read_only=True)
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    
    class Meta:
        model = Vote
        fields = ['id', 'election', 'election_title', 'candidate', 
                 'candidate_name', 'user', 'voted_at', 'ip_address']
        read_only_fields = ['id', 'user', 'voted_at', 'ip_address']


class VoteLogSerializer(serializers.ModelSerializer):
    """Serializer for VoteLog model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    election_title = serializers.CharField(source='election.title', read_only=True)
    
    class Meta:
        model = VoteLog
        fields = ['id', 'user', 'user_username', 'election', 'election_title',
                 'activity_type', 'description', 'ip_address', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for NotificationLog model"""
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = ['id', 'recipient', 'recipient_username', 'notification_type',
                 'subject', 'message', 'status', 'created_at', 'sent_at', 'read_at']
        read_only_fields = ['id', 'created_at', 'sent_at', 'read_at']


class OTPVerificationSerializer(serializers.ModelSerializer):
    """Serializer for OTPVerification model"""
    class Meta:
        model = OTPVerification
        fields = ['id', 'otp_type', 'is_verified', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at', 'expires_at', 'otp_code']
