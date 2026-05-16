from django.db import models
from django.contrib.auth.models import User


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

    achievements = models.TextField(
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

    qualification = models.TextField(
        blank=True
    )

    experience = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.user.username