import random
import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from interns.models import InternProfile, Project, Review

TRACKS = ["web", "cloud", "data", "mobile"]
SKILLS = [
    "Python", "Django", "AWS", "Docker", "Git", "Linux", "SQL", "React",
    "JavaScript", "Terraform", "CI/CD", "Kubernetes", "PostgreSQL", "REST APIs",
    "Pandas", "Flutter", "Node.js", "Bash",
]


class Command(BaseCommand):
    help = "Create fake interns, projects and reviews for load testing"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=1000)
        parser.add_argument("--password", default="Intern@12345")

    def handle(self, *args, **options):
        fake = Faker()
        count = options["users"]
        password_hash = make_password(options["password"])

        last = User.objects.filter(username__regex=r"^intern[0-9]+$").order_by("-id").first()
        offset = int(re.sub(r"[^0-9]", "", last.username)) if last else 0
        last_user_id = User.objects.order_by("-id").values_list("id", flat=True).first() or 0
        last_project_id = Project.objects.order_by("-id").values_list("id", flat=True).first() or 0

        users = []
        for i in range(count):
            number = offset + i + 1
            users.append(
                User(
                    username="intern" + str(number),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email="intern" + str(number) + "@example.com",
                    password=password_hash,
                )
            )
        User.objects.bulk_create(users, batch_size=500)
        new_users = list(User.objects.filter(id__gt=last_user_id))
        self.stdout.write("Created " + str(len(new_users)) + " users")

        profiles = [
            InternProfile(
                user=u,
                track=random.choice(TRACKS),
                skills=", ".join(random.sample(SKILLS, 3)),
                bio=fake.sentence(nb_words=10),
            )
            for u in new_users
        ]
        InternProfile.objects.bulk_create(profiles, batch_size=500)
        new_profiles = list(InternProfile.objects.filter(user__id__gt=last_user_id))
        self.stdout.write("Created " + str(len(new_profiles)) + " profiles")

        projects = []
        for profile in new_profiles:
            for _ in range(random.randint(1, 3)):
                reviewed = random.random() < 0.7
                projects.append(
                    Project(
                        intern=profile,
                        title=fake.catch_phrase()[:200],
                        description=fake.paragraph(nb_sentences=3),
                        github_link="https://github.com/" + profile.user.username + "/" + fake.slug(),
                        status="reviewed" if reviewed else "submitted",
                    )
                )
        Project.objects.bulk_create(projects, batch_size=500)
        new_projects = list(Project.objects.filter(id__gt=last_project_id, status="reviewed"))
        self.stdout.write("Created " + str(len(projects)) + " projects")

        reviewer = User.objects.filter(is_superuser=True).first()
        reviews = [
            Review(
                project=p,
                reviewer=reviewer,
                score=random.choice([5, 6, 7, 7, 8, 8, 8, 9, 9, 10]),
                feedback=fake.sentence(nb_words=12),
            )
            for p in new_projects
        ]
        Review.objects.bulk_create(reviews, batch_size=500)
        self.stdout.write("Created " + str(len(reviews)) + " reviews")
        self.stdout.write(self.style.SUCCESS("Done. Login for seeded users: intern1, intern2, ... password: " + options["password"]))
