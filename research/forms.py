from django import forms
from django.forms import inlineformset_factory
from .models import Research, ProposalDocument, Comment, Funding


class ResearchForm(forms.ModelForm):
    class Meta:
        model = Research
        fields = ['title', 'description', 'status', 'researchers', 'external_collaborators']
        widgets = {
            'researchers': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'external_collaborators': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


# Lets one Research entry have multiple donors, each with their own amount range
FundingFormSet = inlineformset_factory(
    Research,
    Funding,
    fields=['donor', 'amount_min', 'amount_max'],
    extra=1,
    can_delete=True
)


class ProposalDocumentForm(forms.ModelForm):
    class Meta:
        model = ProposalDocument
        fields = ['topic', 'description', 'document']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'})
        }


class ReviewForm(forms.Form):
    ACTION_CHOICES = [
        ('approved', 'Approve'),
        ('needs_revision', 'Return for Revision'),
        ('flagged', 'Flag as Inappropriate'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)