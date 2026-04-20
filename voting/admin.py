from django.contrib import admin

from .models import Candidate, CustomUser, Election, Vote


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "start_time", "end_time", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)
    inlines = [CandidateInline]


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "election")
    list_filter = ("election",)
    search_fields = ("name",)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "election", "candidate", "user", "voted_at")
    list_filter = ("election", "candidate")
    search_fields = ("user__username", "candidate__name", "election__title")
