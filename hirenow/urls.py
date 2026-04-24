from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView # <-- Add this import
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jobs/', include('jobs.urls')),
    path('accounts/', include('accounts.urls')), 
    path('', RedirectView.as_view(url='jobs/board/')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)