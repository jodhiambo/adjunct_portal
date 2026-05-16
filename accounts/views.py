from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import ResearcherProfile
from .forms import ResearcherProfileForm
from .forms import AdjunctApplicationForm
#protecting view
from django.contrib.auth.decorators import login_required


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

    researchers = ResearcherProfile.objects.filter(
        is_adjunct_researcher=True
    )

    return render(request, 'adjunct_researchers.html',
        {'researchers': researchers}
    )