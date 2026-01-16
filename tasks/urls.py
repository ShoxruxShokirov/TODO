from django.urls import path
from .views import (
    TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView,
    toggle_task, register,
    # Lead Developer Level: Advanced features
    bulk_delete_tasks, bulk_update_tasks,
    export_tasks, import_tasks,
    api_task_list, api_task_detail,
)

urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('edit/<int:pk>/', TaskUpdateView.as_view(), name='task_edit'),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='task_delete'),
    path('toggle/<int:task_id>/', toggle_task, name='toggle_task'),
    path('register/', register, name='register'),
    
    # Lead Developer Level: Advanced features
    path('bulk-delete/', bulk_delete_tasks, name='bulk_delete_tasks'),
    path('bulk-update/', bulk_update_tasks, name='bulk_update_tasks'),
    path('export/<str:format>/', export_tasks, name='export_tasks'),
    path('import/', import_tasks, name='import_tasks'),
    
    # REST API endpoints
    path('api/tasks/', api_task_list, name='api_task_list'),
    path('api/tasks/<int:task_id>/', api_task_detail, name='api_task_detail'),
]

