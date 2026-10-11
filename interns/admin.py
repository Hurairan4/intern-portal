from django.contrib import admin
from .models import InternProfile, Project, Review


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "track", "created_at")
    list_filter = ("track",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "skills")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "intern", "status", "submitted_at")
    list_filter = ("status",)
    search_fields = ("title", "intern__user__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("project", "score", "reviewer", "created_at")

    def save_model(self, request, obj, form, change):
        if not obj.reviewer:
            obj.reviewer = request.user
        super().save_model(request, obj, form, change)
        obj.project.status = "reviewed"
        obj.project.save(update_fields=["status"])
