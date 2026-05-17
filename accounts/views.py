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
#protecting view
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Publication
from django.core.paginator import Paginator


def signup_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        # create empty research profile for new user after signup
        ResearcherProfile.objects.create(
            user=user,
            research_area='',
            institution='', 
            achievements='',
            proposals_applied=0,
            proposals_won=0,
        )

        messages.success(request, 'Account created successfully')

        return redirect('login')

    return render(request, 'signup.html')

# research profile view
@login_required
def profile_view(request):

    profile = ResearcherProfile.objects.get(
        user=request.user
    )

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


def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard_view(request):
    return render(request, 'dashboard.html')

#edit profile view
@login_required
def edit_profile_view(request):

    profile = ResearcherProfile.objects.get(
        user=request.user
    )

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

    profile = ResearcherProfile.objects.get(
        user=request.user
    )

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

    paginator = Paginator(researchers, 6)  # Show 6 researchers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if query:

        researchers = researchers.filter(

            Q(user__username__icontains=query) |

            Q(research_area__icontains=query) |

            Q(institution__icontains=query) |

            Q(publications__icontains=query)

        )

    return render(
        request,
        'adjunct_researchers.html',
        {
            'researchers': researchers,
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

    profile = ResearcherProfile.objects.get(
        user=request.user
    )

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
