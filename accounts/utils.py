# accounts/utils.py
from django.core.mail import send_mail
from django.conf import settings
from .models import ResearcherProfile, Notification


def get_or_create_profile(user):
    """
    Returns the ResearcherProfile linked to a user.
    Creates one with empty defaults if it doesn't exist yet
    (e.g. for superusers or accounts created outside signup_view).
    """
    profile, created = ResearcherProfile.objects.get_or_create(
        user=user,
        defaults={
            'research_area': '',
            'institution': '',
            'achievements': '',
            'proposals_applied': 0,
            'proposals_won': 0,
        }
    )
    return profile

#notification function to create a notification for the admin when a new adjunct application is submitted
def create_notification(user, message, link=''):
    """
    Creates an in-platform notification and sends an email alert.
    Used for review outcomes (approved / needs revision / flagged).
    """
    Notification.objects.create(user=user, message=message, link=link)

    if user.email:
        send_mail(
            subject='New notification - Adjunct Portal',
            message=f"{message}\n\nView here: {link}" if link else message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )