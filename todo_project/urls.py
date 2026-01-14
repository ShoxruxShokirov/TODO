"""
URL configuration for todo_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

# Configure admin site
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Todo App Administration')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Todo App Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Welcome to Todo App Administration')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

