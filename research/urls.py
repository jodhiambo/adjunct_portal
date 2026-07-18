from django.urls import path
from . import views

urlpatterns = [
    path('', views.research_list_view, name='research_list'),
    path('create/', views.research_create_view, name='research_create'),
    path('<int:pk>/', views.research_detail_view, name='research_detail'),
    path('<int:pk>/edit/', views.research_edit_view, name='research_edit'),
    path('<int:pk>/upload-proposal/', views.proposal_upload_view, name='proposal_upload'),

    path('review/', views.review_queue_view, name='review_queue'),
    path('review/research/<int:pk>/', views.review_research_action_view, name='review_research_action'),
    path('review/proposal/<int:pk>/', views.review_proposal_action_view, name='review_proposal_action'),

    path('dashboard/', views.analytics_dashboard_view, name='analytics_dashboard'),
    path('teams/', views.team_finder_view, name='team_finder'),
]