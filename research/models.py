from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from accounts.models import ResearcherProfile


REVIEW_STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('approved', 'Approved'),
    ('needs_revision', 'Needs Revision'),
    ('flagged', 'Flagged as Inappropriate'),
]


class ExternalCollaborator(models.Model):

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    institution = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Donor(models.Model):

    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Research(models.Model):

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('won', 'Won'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=500)
    description = RichTextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )

    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default='pending'
    )

    review_comment = models.TextField(blank=True)

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_research'
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)

    researchers = models.ManyToManyField(
        ResearcherProfile,
        related_name='research_works',
        blank=True
    )

    external_collaborators = models.ManyToManyField(
        ExternalCollaborator,
        related_name='research_works',
        blank=True
    )

    donors = models.ManyToManyField(
        Donor,
        through='Funding',
        related_name='research_works',
        blank=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_research'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Funding(models.Model):

    research = models.ForeignKey(Research, on_delete=models.CASCADE)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)

    amount_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.donor.name} → {self.research.title}"


class ProposalDocument(models.Model):

    research = models.ForeignKey(
        Research,
        on_delete=models.CASCADE,
        related_name='proposal_documents'
    )

    topic = models.CharField(max_length=500)
    description = RichTextField(blank=True)
    document = models.FileField(upload_to='proposal_documents/')

    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default='pending'
    )

    review_comment = models.TextField(blank=True)

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_proposals'
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_proposals'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic


class Comment(models.Model):

    research = models.ForeignKey(
        Research,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.research.title}"