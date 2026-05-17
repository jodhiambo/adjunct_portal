from django import forms
from .models import ResearcherProfile
from .models import Publication

try:
    from ckeditor.widgets import CKEditorWidget
except ImportError:
    CKEditorWidget = forms.Textarea


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
            'brief_profile',
            'work_experience',
            'grants_fellowships',
            'publications',
            'cv',
            'application_letter',
        ]

        widgets = {

            'achievements': CKEditorWidget(),

            'brief_profile': CKEditorWidget(),

            'work_experience': CKEditorWidget(),

            'grants_fellowships': CKEditorWidget(),

        }

class AdjunctApplicationForm(forms.ModelForm):

    class Meta:

        model = ResearcherProfile

        fields = [
            'qualification',
            'experience',
        ]

        widgets = {

            'qualification': CKEditorWidget(),

            'experience': CKEditorWidget(),

        }


# Form for adding publications
class PublicationForm(forms.ModelForm):

    class Meta:

        model = Publication

        fields = [
            'title',
            'journal',
            'publication_year',
            'category',
            'doi_link',
            'publication_pdf',
        ]