import os

from django.contrib import messages
from django.core.management import call_command
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import RegisterForm, VoteForm
from .models import Election, Vote


def _ensure_sqlite_schema_for_vercel_fallback(error: OperationalError) -> bool:
    message = str(error).lower()
    is_missing_table = "no such table" in message
    using_fallback = os.getenv("VERCEL") and not (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL_NON_POOLING")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRES_PRISMA_URL")
    )
    if is_missing_table and using_fallback:
        call_command("migrate", interactive=False, verbosity=0, run_syncdb=True)
        return True
    return False


def home(request):
    now = timezone.now()
    try:
        elections = Election.objects.filter(is_active=True, end_time__gte=now)
    except OperationalError as exc:
        if not _ensure_sqlite_schema_for_vercel_fallback(exc):
            raise
        elections = Election.objects.filter(is_active=True, end_time__gte=now)
    return render(request, "voting/home.html", {"elections": elections})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "voting/register.html", {"form": form})


@login_required
def dashboard(request):
    now = timezone.now()
    elections = Election.objects.filter(is_active=True, end_time__gte=now)
    voted_election_ids = set(
        Vote.objects.filter(user=request.user).values_list("election_id", flat=True)
    )
    return render(
        request,
        "voting/dashboard.html",
        {
            "elections": elections,
            "voted_election_ids": voted_election_ids,
        },
    )


@login_required
def vote_view(request, election_id):
    election = get_object_or_404(Election, id=election_id, is_active=True)
    now = timezone.now()

    if election.start_time > now or election.end_time < now:
        messages.error(request, "This election is not open for voting.")
        return redirect("dashboard")

    if Vote.objects.filter(election=election, user=request.user).exists():
        messages.warning(request, "You have already voted in this election.")
        return redirect("results", election_id=election.id)

    if request.method == "POST":
        form = VoteForm(request.POST, election=election)
        if form.is_valid():
            candidate = form.cleaned_data["candidate"]
            try:
                with transaction.atomic():
                    Vote.objects.create(
                        election=election,
                        candidate=candidate,
                        user=request.user,
                    )
            except IntegrityError:
                messages.error(request, "Duplicate vote blocked.")
                return redirect("results", election_id=election.id)

            messages.success(request, "Your vote has been submitted successfully.")
            return redirect("results", election_id=election.id)
    else:
        form = VoteForm(election=election)

    return render(request, "voting/vote.html", {"election": election, "form": form})


def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    total_votes = election.votes.count()
    candidates = election.candidates.annotate(vote_count=Count("votes")).order_by("-vote_count", "name")

    candidate_rows = []
    for candidate in candidates:
        percentage = 0
        if total_votes > 0:
            percentage = round((candidate.vote_count / total_votes) * 100, 2)
        candidate_rows.append(
            {
                "candidate": candidate,
                "votes": candidate.vote_count,
                "percentage": percentage,
            }
        )

    return render(
        request,
        "voting/results.html",
        {
            "election": election,
            "total_votes": total_votes,
            "candidate_rows": candidate_rows,
        },
    )
