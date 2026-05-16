from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('apply-adjunct/', views.apply_adjunct_view, name='apply_adjunct'),
    path('adjunct-researchers/', views.adjunct_researchers_view, name='adjunct_researchers'),
    
]