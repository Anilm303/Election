from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

from .models import (
    Candidate, CustomUser, Election, Vote, VoterProfile,
    VoteLog, OTPVerification, CaptchaLog, NotificationLog, AuditLog
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "email_verified", "two_fa_enabled", "is_staff", "is_active")
    list_filter = ("email_verified", "two_fa_enabled", "is_staff", "is_active", "created_at")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("created_at", "updated_at", "last_login")
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Security', {'fields': ('email_verified', 'phone_verified', 'two_fa_enabled', 'is_locked', 'failed_login_attempts')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Preferences', {'fields': ('language',)}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )


@admin.register(VoterProfile)
class VoterProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "unique_voter_id", "verification_status", "verified_by", "verified_at")
    list_filter = ("verification_status", "gender", "verified_at")
    search_fields = ("user__username", "unique_voter_id")
    readonly_fields = ("created_at", "updated_at", "verified_at")
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Verification', {'fields': ('unique_voter_id', 'verification_status', 'verified_by', 'verified_at', 'verification_notes')}),
        ('Personal Information', {'fields': ('date_of_birth', 'gender', 'address', 'contact_number')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1
    fields = ('name', 'party', 'symbol', 'position', 'is_independent')


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "start_time", "end_time", "is_active", "allow_voting", 
                   "publish_results", "vote_count")
    list_filter = ("is_active", "allow_voting", "publish_results", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at", "created_by", "vote_count")
    inlines = [CandidateInline]
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description', 'created_by')}),
        ('Timing', {'fields': ('start_time', 'end_time')}),
        ('Status', {'fields': ('is_active', 'allow_voting', 'publish_results')}),
        ('Settings', {'fields': ('require_voter_verification', 'max_attempts_allowed')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def vote_count(self, obj):
        count = obj.votes.count()
        return format_html(
            '<span style="background-color: #417690; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            count
        )
    vote_count.short_description = 'Total Votes'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "election", "party", "symbol", "vote_count", "position")
    list_filter = ("election", "is_independent", "party")
    search_fields = ("name", "party", "manifesto")
    readonly_fields = ("created_at", "updated_at", "vote_count")
    fieldsets = (
        ('Basic Info', {'fields': ('election', 'name', 'email', 'phone')}),
        ('Political Info', {'fields': ('party', 'symbol', 'is_independent')}),
        ('Biography', {'fields': ('biography', 'manifesto')}),
        ('Photo', {'fields': ('photo', 'photo_url')}),
        ('Display', {'fields': ('position',)}),
        ('Vote Count', {'fields': ('vote_count',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def vote_count(self, obj):
        return obj.votes.count()
    vote_count.short_description = 'Votes'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "election", "candidate", "user", "ip_address", "voted_at")
    list_filter = ("election", "candidate", "voted_at")
    search_fields = ("user__username", "candidate__name", "election__title", "ip_address")
    readonly_fields = ("id", "voted_at", "ip_address", "user_agent")
    date_hierarchy = "voted_at"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(VoteLog)
class VoteLogAdmin(admin.ModelAdmin):
    list_display = ("user", "election", "activity_type", "ip_address", "timestamp")
    list_filter = ("activity_type", "timestamp")
    search_fields = ("user__username", "description", "ip_address")
    readonly_fields = ("timestamp", "user_agent")
    date_hierarchy = "timestamp"
    
    def has_add_permission(self, request):
        return False


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "otp_type", "is_verified", "attempts", "created_at", "expires_at")
    list_filter = ("otp_type", "is_verified", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "verified_at", "otp_code")
    
    def has_add_permission(self, request):
        return False


@admin.register(CaptchaLog)
class CaptchaLogAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "is_passed", "timestamp")
    list_filter = ("is_passed", "timestamp")
    search_fields = ("ip_address",)
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"
    
    def has_add_permission(self, request):
        return False


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("subject", "recipient", "notification_type", "status", "created_at")
    list_filter = ("notification_type", "status", "created_at")
    search_fields = ("subject", "recipient__username", "message")
    readonly_fields = ("created_at", "sent_at", "read_at")
    date_hierarchy = "created_at"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("admin_user", "action_type", "model_name", "description", "timestamp")
    list_filter = ("action_type", "model_name", "timestamp")
    search_fields = ("admin_user__username", "description")
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"
    
    def has_add_permission(self, request):
        return False
