from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.post_job, name='post_job'),
    path('board/', views.job_list, name='job_list'),
    path('apply/<str:job_id>/', views.apply_job, name='apply_job'), 
    path('dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('my-applications/', views.seeker_dashboard, name='seeker_dashboard'),
    path('update-status/<str:app_id>/<str:new_status>/', views.update_status, name='update_status'),
]