from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import InternProfile


class StyledMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = css


class LoginForm(StyledMixin, AuthenticationForm):
    pass


class RegisterForm(StyledMixin, UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    track = forms.ChoiceField(choices=InternProfile.TRACKS)
    skills = forms.CharField(
        max_length=255,
        required=False,
        help_text="Comma separated, e.g. Python, AWS, Git",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            InternProfile.objects.create(
                user=user,
                track=self.cleaned_data["track"],
                skills=self.cleaned_data["skills"],
            )
        return user


class ProfileForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = InternProfile
        fields = ("track", "skills", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}
