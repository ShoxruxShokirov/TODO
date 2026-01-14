from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import Task
from .forms import TaskForm, RegisterForm


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        
        # Filter by status
        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'completed':
            queryset = queryset.filter(completed=True)
        elif filter_type == 'active':
            queryset = queryset.filter(completed=False)
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # Sort
        sort = self.request.GET.get('sort', 'created')
        if sort == 'priority':
            from django.db.models import Case, When, IntegerField
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
            queryset = queryset.order_by('due_date', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TaskForm()
        context['filter_type'] = self.request.GET.get('filter', 'all')
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_type'] = self.request.GET.get('sort', 'created')
        
        # Statistics for progress bar
        all_tasks = Task.objects.filter(user=self.request.user)
        context['total_tasks'] = all_tasks.count()
        context['completed_tasks'] = all_tasks.filter(completed=True).count()
        context['active_tasks'] = all_tasks.filter(completed=False).count()
        context['overdue_tasks'] = all_tasks.filter(
            completed=False,
            due_date__lt=timezone.now()
        ).count()
        
        # Calculate progress percentage
        if context['total_tasks'] > 0:
            context['progress_percentage'] = int((context['completed_tasks'] / context['total_tasks']) * 100)
        else:
            context['progress_percentage'] = 0
        
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return redirect('task_list')


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)


def toggle_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.completed = not task.completed
        task.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'completed': task.completed
            })
        
        messages.success(request, 'Task updated!')
    return redirect('task_list')


def register(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('task_list')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

