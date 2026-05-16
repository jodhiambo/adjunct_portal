from django import forms
from .models import ResearcherProfile


class ResearcherProfileForm(forms.ModelForm):

    class Meta:
        model = ResearcherProfile

        fields = [
            'profile_picture',
            'research_area',
            'institution',
            'achievements',
            'proposals_applied',
            'proposals_won',
        ]

class AdjunctApplicationForm(forms.ModelForm):

    class Meta:

        model = ResearcherProfile

        fields = [
            'qualification',
            'experience',
        ]