from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class ResearcherProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    research_area = models.CharField(
        max_length=255
    )

    institution = models.CharField(
        max_length=255,
        blank=True
    )

    achievements = RichTextField(
        blank=True
    )

    proposals_applied = models.IntegerField(
        default=0
    )

    proposals_won = models.IntegerField(
        default=0
    )
    is_adjunct_researcher = models.BooleanField(
        default=False
    )

    application_submitted = models.BooleanField(
        default=False
    )

    application_status = models.CharField(
        max_length=50,
        default='Pending'
    )

    qualification = RichTextField(
        blank=True
    )

    experience = RichTextField(
        blank=True
    )

    brief_profile = RichTextField(
        blank=True
    )

    work_experience = RichTextField(
        blank=True
    )

    grants_fellowships = RichTextField(
        blank=True
    )

    publications = RichTextField(
        blank=True
    )

    cv = models.FileField(
        upload_to='cv/',
        blank=True,
        null=True
    )

    application_letter = models.FileField(
        upload_to='application_letters/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username

#Creating a separate model for publications to allow multiple publications per researcher
class Publication(models.Model):

    researcher = models.ForeignKey(
        ResearcherProfile,
        on_delete=models.CASCADE,
        related_name='publications_list'
    )

    title = models.CharField(
        max_length=500
    )

    journal = models.CharField(
        max_length=300
    )

    publication_year = models.IntegerField()

    category = models.CharField(
        max_length=200,
        blank=True
    )

    doi_link = models.URLField(
        blank=True
    )

    publication_pdf = models.FileField(
        upload_to='publications/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title