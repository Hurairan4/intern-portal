from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class InternProfile(models.Model):
    TRACKS = [
        ("web", "Web Development"),
        ("cloud", "Cloud / DevOps"),
        ("data", "Data Science"),
        ("mobile", "Mobile Development"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    track = models.CharField(max_length=20, choices=TRACKS, default="web", db_index=True)
    skills = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Project(models.Model):
    STATUS = [("submitted", "Submitted"), ("reviewed", "Reviewed")]
    intern = models.ForeignKey(InternProfile, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    description = models.TextField()
    github_link = models.URLField(blank=True)
    file = models.FileField(upload_to="submissions/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default="submitted", db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="review")
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - {self.score}/10"