from django.contrib import admin
from .models import ResearcherProfile
from .models import Publication


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

#Register Publication model in admin
admin.site.register(Publication)