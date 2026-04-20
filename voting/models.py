from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Keep the model simple while allowing future extension.
    pass


class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=120)
    manifesto = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)

    class Meta:
        unique_together = ("election", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.election.title})"


class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="votes")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="votes")
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["election", "user"], name="unique_vote_per_user_per_election")
        ]
        ordering = ["-voted_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.candidate.name}"
