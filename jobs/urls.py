from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.post_job, name='post_job'),
    path('board/', views.job_list, name='job_list'),
    path('apply/<str:job_id>/', views.apply_job, name='apply_job'),
    path('dashboard/', views.employer_dashboard, name='employer_dashboard'),
]