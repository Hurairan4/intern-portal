from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileForm
from .models import InternProfile


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
