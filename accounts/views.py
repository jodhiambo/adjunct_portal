from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import ResearcherProfile
from .forms import (
    ResearcherProfileForm,
    AdjunctApplicationForm,
    PublicationForm
)

#import utils for profile
from .utils import get_or_create_profile

#protecting view
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Publication
from django.core.paginator import Paginator

#for password reset
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


def signup_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        # create empty research profile for new user after signup
        get_or_create_profile(user)

        messages.success(request, 'Account created successfully')

        return redirect('login')

    return render(request, 'signup.html')

# research profile view
@login_required
def profile_view(request):

    profile = get_or_create_profile(request.user)
    return render(
        request,
        'profile.html',
        {'profile': profile}
    )

def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('profile')

        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'login.html')

#Forgot password view
def forgot_password_view(request):

    if request.method == 'POST':
        email = request.POST['email']

        user = User.objects.filter(email=email).first()

        if user is not None:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )

            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

        # Show the same message whether or not the email exists
        messages.success(request, 'If that email exists, a reset link has been sent.')
        return redirect('login')

    return render(request, 'forgot_password.html')

#Reset password view
def reset_password_view(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'This password reset link is invalid or has expired.')
        return redirect('login')

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password', uidb64=uidb64, token=token)

        user.set_password(password)
        user.save()

        messages.success(request, 'Password reset successful. Please log in.')
        return redirect('login')

    return render(request, 'reset_password.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard_view(request):
    return render(request, 'dashboard.html')

#edit profile view
@login_required
def edit_profile_view(request):

    profile = get_or_create_profile(request.user)

    if request.method == 'POST':

        form = ResearcherProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()

            return redirect('profile')

    else:

        form = ResearcherProfileForm(
            instance=profile
        )

    return render(
        request,
        'edit_profile.html',
        {'form': form}
    )
#Adjuct application view
@login_required
def apply_adjunct_view(request):

    profile = get_or_create_profile(request.user)

    if request.method == 'POST':

        form = AdjunctApplicationForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            application = form.save(
                commit=False
            )

            application.application_submitted = True

            application.application_status = 'Pending'

            application.save()

            return redirect('profile')

    else:

        form = AdjunctApplicationForm(
            instance=profile
        )

    return render(
        request,
        'apply_adjunct.html',
        {'form': form}
    )

#adjunct researcher being viewed publicly
def adjunct_researchers_view(request):

    query = request.GET.get('q')

    researchers = ResearcherProfile.objects.filter(
        is_adjunct_researcher=True
    ) .order_by('-proposals_won')  # Sort by proposals won in descending order

    if query:

        researchers = researchers.filter(

            Q(user__username__icontains=query) |

            Q(research_area__icontains=query) |

            Q(institution__icontains=query) |

            Q(publications__icontains=query)

        )
    
    paginator = Paginator(researchers, 6)  # Show 6 researchers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'adjunct_researchers.html',
        {
            'query': query,
            'researchers': page_obj
        }
    )

def researcher_detail_view(request, id):

    researcher = get_object_or_404(
        ResearcherProfile,
        id=id,
        is_adjunct_researcher=True
    )

    return render(
        request,
        'researcher_details.html',
        {'researcher': researcher}
    )

#Research publication view
@login_required
def add_publication_view(request):

    profile = get_or_create_profile(request.user)

    if request.method == 'POST':

        form = PublicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            publication = form.save(
                commit=False
            )

            publication.researcher = profile

            publication.save()

            return redirect('profile')

    else:

        form = PublicationForm()

    return render(
        request,
        'add_publication.html',
        {'form': form}
    )

#notification  bell icon require login 
@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications.html', {'notifications': notifications})
