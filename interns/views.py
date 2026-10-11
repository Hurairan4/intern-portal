from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .forms import RegisterForm, ProfileForm, ProjectForm
from .models import InternProfile, Review


def home(request):
    return redirect("profile" if request.user.is_authenticated else "login")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    profile, _ = InternProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    skill_list = [s.strip() for s in profile.skills.split(",") if s.strip()]
    return render(
        request,
        "interns/profile.html",
        {"form": form, "profile": profile, "skill_list": skill_list},
    )


@login_required
def project_list(request):
    profile, _ = InternProfile.objects.get_or_create(user=request.user)
    projects = profile.projects.select_related("review").order_by("-submitted_at")
    reviews = Review.objects.filter(project__intern=profile)
    avg = reviews.aggregate(avg=Avg("score"))["avg"]
    context = {
        "projects": projects,
        "total": projects.count(),
        "reviewed_count": reviews.count(),
        "avg_score": round(avg, 1) if avg else None,
    }
    return render(request, "interns/projects.html", context)


@login_required
def project_create(request):
    profile, _ = InternProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.intern = profile
            project.save()
            return redirect("project_list")
    else:
        form = ProjectForm()
    return render(request, "interns/project_form.html", {"form": form})
