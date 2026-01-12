from django.urls import path
from .views import (
    TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView,
    toggle_task, register
)

urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('edit/<int:pk>/', TaskUpdateView.as_view(), name='task_edit'),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='task_delete'),
    path('toggle/<int:task_id>/', toggle_task, name='toggle_task'),
    path('register/', register, name='register'),
]

