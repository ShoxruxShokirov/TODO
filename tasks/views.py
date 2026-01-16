"""
Task views with advanced features, error handling, and optimization.

Senior-level implementation with:
- Query optimization (select_related, prefetch_related)
- Comprehensive error handling
- Logging
- Permission checks
- Performance optimizations
"""

import logging
import json
import csv
from datetime import datetime, timedelta
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Case, When, IntegerField, Count
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.http import require_http_methods

from .models import Task
from .forms import TaskForm, RegisterForm

logger = logging.getLogger('tasks')


class TaskListView(LoginRequiredMixin, ListView):
    """
    List view for tasks with advanced filtering, sorting, and statistics.
    
    Features:
    - Advanced filtering (status, priority, date range)
    - Full-text search
    - Multiple sorting options
    - Task statistics
    - Pagination
    - Query optimization
    """
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        """
        Get optimized queryset with filtering, searching, and sorting.
        
        Returns:
            QuerySet: Optimized queryset of tasks
        """
        try:
            # Start with user's tasks using custom manager
            queryset = Task.objects.for_user(self.request.user)
            
            # Filter by status
            filter_type = self.request.GET.get('filter', 'all')
            if filter_type == 'completed':
                queryset = queryset.completed(user=self.request.user)
            elif filter_type == 'active':
                queryset = queryset.active(user=self.request.user)
            elif filter_type == 'overdue':
                queryset = queryset.overdue(user=self.request.user)
            
            # Filter by priority
            priority_filter = self.request.GET.get('priority', '')
            if priority_filter in ['low', 'medium', 'high']:
                queryset = queryset.by_priority(priority_filter, user=self.request.user)
            
            # Search
            search = self.request.GET.get('search', '').strip()
            if search:
                queryset = queryset.search(search, user=self.request.user)
            
            # Sort
            sort = self.request.GET.get('sort', 'created')
            if sort == 'priority':
                queryset = queryset.annotate(
                    priority_order=Case(
                        When(priority='high', then=0),
                        When(priority='medium', then=1),
                        When(priority='low', then=2),
                        default=3,
                        output_field=IntegerField(),
                    )
                ).order_by('priority_order', '-created_at')
            elif sort == 'due_date':
                queryset = queryset.order_by(
                    'due_date', '-created_at'
                ).exclude(due_date__isnull=True)
                # Add tasks without due dates at the end
                queryset = queryset.union(
                    Task.objects.for_user(self.request.user).filter(
                        due_date__isnull=True
                    ).order_by('-created_at')
                )
            elif sort == 'title':
                queryset = queryset.order_by('title', '-created_at')
            else:
                queryset = queryset.order_by('-created_at')
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error in TaskListView.get_queryset: {str(e)}", exc_info=True)
            return Task.objects.none()

    def get_context_data(self, **kwargs):
        """
        Add additional context data including statistics and form.
        
        Returns:
            dict: Context dictionary
        """
        context = super().get_context_data(**kwargs)
        context['form'] = TaskForm()
        context['filter_type'] = self.request.GET.get('filter', 'all')
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_type'] = self.request.GET.get('sort', 'created')
        context['priority_filter'] = self.request.GET.get('priority', '')
        
        try:
            # Optimized statistics using aggregation
            all_tasks = Task.objects.for_user(self.request.user)
            stats = all_tasks.aggregate(
                total=Count('id'),
                completed=Count('id', filter=Q(completed=True)),
                active=Count('id', filter=Q(completed=False)),
                overdue=Count('id', filter=Q(
                    completed=False,
                    due_date__lt=timezone.now()
                ))
            )
            
            context['total_tasks'] = stats['total'] or 0
            context['completed_tasks'] = stats['completed'] or 0
            context['active_tasks'] = stats['active'] or 0
            context['overdue_tasks'] = stats['overdue'] or 0
            
            # Calculate progress percentage
            if context['total_tasks'] > 0:
                context['progress_percentage'] = int(
                    (context['completed_tasks'] / context['total_tasks']) * 100
                )
            else:
                context['progress_percentage'] = 0
            
            # Lead Developer Level: Extended Analytics
            # Statistics by priority
            priority_stats = all_tasks.values('priority').annotate(count=Count('id'))
            context['priority_distribution'] = {
                'high': next((p['count'] for p in priority_stats if p['priority'] == 'high'), 0),
                'medium': next((p['count'] for p in priority_stats if p['priority'] == 'medium'), 0),
                'low': next((p['count'] for p in priority_stats if p['priority'] == 'low'), 0),
            }
            
            # Statistics by completion status
            context['completion_rate'] = (context['completed_tasks'] / context['total_tasks'] * 100) if context['total_tasks'] > 0 else 0
            
            # Tasks created in last 7 days
            week_ago = timezone.now() - timedelta(days=7)
            context['tasks_last_week'] = all_tasks.filter(created_at__gte=week_ago).count()
            
            # Tasks completed in last 7 days
            context['completed_last_week'] = all_tasks.filter(
                completed=True,
                updated_at__gte=week_ago
            ).count()
            
            # Monthly statistics (last 6 months)
            monthly_data = []
            for i in range(6):
                month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                monthly_tasks = all_tasks.filter(created_at__range=[month_start, month_end]).count()
                monthly_data.append({
                    'month': month_start.strftime('%b %Y'),
                    'count': monthly_tasks
                })
            context['monthly_statistics'] = list(reversed(monthly_data))
            
            # Daily completion trend (last 7 days)
            daily_completion = []
            for i in range(7):
                day = timezone.now().date() - timedelta(days=6-i)
                day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
                day_end = timezone.make_aware(datetime.combine(day, datetime.max.time()))
                day_completed = all_tasks.filter(
                    completed=True,
                    updated_at__range=[day_start, day_end]
                ).count()
                daily_completion.append({
                    'day': day.strftime('%d %b'),
                    'count': day_completed
                })
            context['daily_completion'] = daily_completion
                
        except Exception as e:
            logger.error(f"Error in TaskListView.get_context_data: {str(e)}", exc_info=True)
            context['total_tasks'] = 0
            context['completed_tasks'] = 0
            context['active_tasks'] = 0
            context['overdue_tasks'] = 0
            context['progress_percentage'] = 0
            context['priority_distribution'] = {'high': 0, 'medium': 0, 'low': 0}
            context['completion_rate'] = 0
            context['tasks_last_week'] = 0
            context['completed_last_week'] = 0
            context['monthly_statistics'] = []
            context['daily_completion'] = []
        
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create view for tasks with transaction support and error handling.
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    @transaction.atomic
    def form_valid(self, form):
        """Save task with user assignment."""
        try:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, 'Task created successfully!')
            logger.info(f"Task created: {form.instance.id} by user {self.request.user.username}")
            return response
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}", exc_info=True)
            messages.error(self.request, 'An error occurred while creating the task.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        logger.warning(f"Task creation form invalid for user {self.request.user.username}")
        return super().form_invalid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update view for tasks with permission checks and transaction support.
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        """Only allow users to edit their own tasks."""
        return Task.objects.for_user(self.request.user)

    @transaction.atomic
    def form_valid(self, form):
        """Save updated task."""
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Task updated successfully!')
            logger.info(f"Task updated: {self.object.id} by user {self.request.user.username}")
            return response
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}", exc_info=True)
            messages.error(self.request, 'An error occurred while updating the task.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete view for tasks with permission checks and transaction support.
    """
    model = Task
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        """Only allow users to delete their own tasks."""
        return Task.objects.for_user(self.request.user)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """Delete task with logging."""
        try:
            task_id = self.get_object().id
            task_title = self.get_object().title
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, 'Task deleted successfully!')
            logger.info(f"Task deleted: {task_id} ({task_title}) by user {request.user.username}")
            return response
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}", exc_info=True)
            messages.error(self.request, 'An error occurred while deleting the task.')
            return redirect('task_list')


@require_http_methods(["POST"])
def toggle_task(request, task_id):
    """
    Toggle task completion status with transaction support.
    
    Args:
        request: HTTP request object
        task_id: ID of the task to toggle
        
    Returns:
        JsonResponse or RedirectResponse
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        with transaction.atomic():
            completed = task.toggle_completion()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'completed': completed
            })
        
        messages.success(request, 'Task status updated!')
        logger.info(f"Task toggled: {task.id} by user {request.user.username}")
        
    except Exception as e:
        logger.error(f"Error toggling task: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'An error occurred'}, status=500)
        messages.error(request, 'An error occurred.')
    
    return redirect('task_list')


def register(request):
    """
    User registration view with transaction support and error handling.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Registration page or redirect
    """
    if request.user.is_authenticated:
        return redirect('task_list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                messages.success(request, f'Welcome, {user.username}! Your account has been created.')
                logger.info(f"New user registered: {user.username}")
                return redirect('task_list')
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}", exc_info=True)
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            logger.warning("Registration form invalid")
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})


# ============================================================================
# LEAD DEVELOPER LEVEL: Advanced Features
# ============================================================================

@require_http_methods(["POST"])
def bulk_delete_tasks(request):
    """
    Lead Developer Level: Bulk delete multiple tasks.
    
    Args:
        request: HTTP request object with task_ids in POST data
        
    Returns:
        JsonResponse: Success status
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    try:
        task_ids = request.POST.getlist('task_ids[]') or json.loads(request.body).get('task_ids', [])
        
        if not task_ids:
            return JsonResponse({'success': False, 'error': 'No tasks selected'}, status=400)
        
        with transaction.atomic():
            tasks = Task.objects.filter(id__in=task_ids, user=request.user)
            deleted_count = tasks.count()
            tasks.delete()
        
        messages.success(request, f'{deleted_count} task(s) deleted successfully.')
        logger.info(f"Bulk deleted {deleted_count} tasks by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error in bulk_delete_tasks: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'An error occurred'}, status=500)


@require_http_methods(["POST"])
def bulk_update_tasks(request):
    """
    Lead Developer Level: Bulk update multiple tasks (status, priority).
    
    Args:
        request: HTTP request object with task_ids and update data
        
    Returns:
        JsonResponse: Success status
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body) if request.body else request.POST
        task_ids = data.get('task_ids', [])
        action = data.get('action', '')
        
        if not task_ids:
            return JsonResponse({'success': False, 'error': 'No tasks selected'}, status=400)
        
        with transaction.atomic():
            tasks = Task.objects.filter(id__in=task_ids, user=request.user)
            updated_count = 0
            
            if action == 'complete':
                updated_count = tasks.update(completed=True)
            elif action == 'activate':
                updated_count = tasks.update(completed=False)
            elif action == 'high_priority':
                updated_count = tasks.update(priority='high')
            elif action == 'medium_priority':
                updated_count = tasks.update(priority='medium')
            elif action == 'low_priority':
                updated_count = tasks.update(priority='low')
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)
        
        messages.success(request, f'{updated_count} task(s) updated successfully.')
        logger.info(f"Bulk updated {updated_count} tasks by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error in bulk_update_tasks: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'An error occurred'}, status=500)


@require_http_methods(["GET"])
def export_tasks(request, format='json'):
    """
    Lead Developer Level: Export tasks to JSON or CSV.
    
    Args:
        request: HTTP request object
        format: Export format ('json' or 'csv')
        
    Returns:
        HttpResponse: File download response
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        tasks = Task.objects.for_user(request.user).order_by('-created_at')
        
        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Title', 'Description', 'Priority', 'Completed', 'Due Date', 'Tags', 'Created At', 'Updated At'])
            
            for task in tasks:
                writer.writerow([
                    task.title,
                    task.description or '',
                    task.get_priority_display(),
                    'Yes' if task.completed else 'No',
                    task.due_date.strftime('%Y-%m-%d %H:%M:%S') if task.due_date else '',
                    task.tags or '',
                    task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                ])
            
            logger.info(f"Tasks exported to CSV by user {request.user.username}")
            return response
            
        else:  # JSON
            tasks_data = []
            for task in tasks:
                tasks_data.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'completed': task.completed,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'tags': task.tags,
                    'color': task.color,
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat(),
                })
            
            response = HttpResponse(
                json.dumps(tasks_data, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            logger.info(f"Tasks exported to JSON by user {request.user.username}")
            return response
            
    except Exception as e:
        logger.error(f"Error exporting tasks: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while exporting tasks.')
        return redirect('task_list')


@require_http_methods(["GET", "POST"])
def import_tasks(request):
    """
    Lead Developer Level: Import tasks from JSON file.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Success/error response
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                messages.error(request, 'No file uploaded.')
                return redirect('task_list')
            
            file = request.FILES['file']
            
            if file.name.endswith('.json'):
                data = json.loads(file.read().decode('utf-8'))
                imported_count = 0
                
                with transaction.atomic():
                    for task_data in data:
                        # Skip if task with same title already exists
                        if Task.objects.filter(user=request.user, title=task_data.get('title', '')).exists():
                            continue
                        
                        Task.objects.create(
                            user=request.user,
                            title=task_data.get('title', 'Untitled'),
                            description=task_data.get('description', ''),
                            priority=task_data.get('priority', 'medium'),
                            completed=task_data.get('completed', False),
                            due_date=datetime.fromisoformat(task_data['due_date']) if task_data.get('due_date') else None,
                            tags=task_data.get('tags', ''),
                            color=task_data.get('color', ''),
                        )
                        imported_count += 1
                
                messages.success(request, f'{imported_count} task(s) imported successfully.')
                logger.info(f"{imported_count} tasks imported by user {request.user.username}")
                
            else:
                messages.error(request, 'Only JSON files are supported for import.')
                
        except Exception as e:
            logger.error(f"Error importing tasks: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred while importing tasks. Please check the file format.')
    
    return redirect('task_list')


# Lead Developer Level: REST API endpoints
def api_task_list(request):
    """
    Lead Developer Level: REST API endpoint to get all tasks.
    
    Returns:
        JsonResponse: List of tasks
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        tasks = Task.objects.for_user(request.user).order_by('-created_at')
        tasks_data = []
        
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'completed': task.completed,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'tags': task.tags,
                'color': task.color,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat(),
                'is_overdue': task.is_overdue(),
            })
        
        return JsonResponse({'tasks': tasks_data}, safe=False)
        
    except Exception as e:
        logger.error(f"Error in api_task_list: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred'}, status=500)


def api_task_detail(request, task_id):
    """
    Lead Developer Level: REST API endpoint to get task details.
    
    Args:
        request: HTTP request object
        task_id: ID of the task
        
    Returns:
        JsonResponse: Task data
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'completed': task.completed,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'tags': task.tags,
            'color': task.color,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'is_overdue': task.is_overdue(),
            'days_until_due': task.days_until_due(),
        }
        
        return JsonResponse(task_data)
        
    except Exception as e:
        logger.error(f"Error in api_task_detail: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred'}, status=500)
