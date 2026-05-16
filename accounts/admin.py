from django.contrib import admin
from .models import ResearcherProfile


@admin.register(ResearcherProfile)
class ResearcherProfileAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'research_area',
        'application_status',
        'is_adjunct_researcher',
    ]

    list_filter = [
        'application_status',
        'is_adjunct_researcher',
    ]