from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views, api_views

# REST API Router
router = DefaultRouter()
router.register(r'elections', api_views.ElectionViewSet, basename='api-election')
router.register(r'candidates', api_views.CandidateViewSet, basename='api-candidate')
router.register(r'votes', api_views.VoteViewSet, basename='api-vote')
router.register(r'voter-profiles', api_views.VoterProfileViewSet, basename='api-voter-profile')
router.register(r'otp', api_views.OTPViewSet, basename='api-otp')
router.register(r'vote-logs', api_views.VoteLogViewSet, basename='api-vote-log')
router.register(r'notifications', api_views.NotificationViewSet, basename='api-notification')

urlpatterns = [
    # ============ Public Views ============
    path("", views.home, name="home"),
    
    # ============ Authentication Views ============
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("verify-email/<int:user_id>/", views.verify_email, name="verify_email"),
    path("complete-voter-profile/", views.complete_voter_profile, name="complete_voter_profile"),
    path("setup-2fa/", views.setup_2fa, name="setup_2fa"),
    path("confirm-2fa/", views.confirm_2fa, name="confirm_2fa"),
    path("verify-2fa/", views.verify_2fa, name="verify_2fa"),
    
    # ============ Voting Views ============
    path("dashboard/", views.dashboard, name="dashboard"),
    path("vote/<int:election_id>/", views.vote_view, name="vote"),
    path("results/<int:election_id>/", views.results, name="results"),
    path("vote-history/", views.view_vote_history, name="vote_history"),
    path("settings/", views.settings_view, name="settings"),
    
    # ============ Export Views ============
    path("export/results/<int:election_id>/pdf/", views.export_results_pdf, name="export_results_pdf"),
    path("export/results/<int:election_id>/excel/", views.export_results_excel, name="export_results_excel"),
    
    # ============ Admin Views ============
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("manage-elections/", views.manage_elections, name="manage_elections"),
    path("create-election/", views.create_election, name="create_election"),
    path("manage-candidates/<int:election_id>/", views.manage_candidates, name="manage_candidates"),
    path("add-candidate/<int:election_id>/", views.add_candidate, name="add_candidate"),
    path("verify-voters/", views.verify_voters, name="verify_voters"),
    
    # ============ API Views ============
    path("api/stats/<int:election_id>/", views.get_election_stats_json, name="election_stats_json"),
    path("api/token/", api_views.CustomTokenObtainPairView.as_view(), name="api_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("api/", include(router.urls)),
]
