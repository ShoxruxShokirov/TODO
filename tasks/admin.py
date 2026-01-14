"""
Admin configuration for Task model.

Senior-level admin interface with advanced features:
- Custom list display
- Filtering and searching
- Bulk actions
- Read-only fields
- Custom actions
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Advanced admin interface for Task model.
    """
    list_display = [
        'id',
        'title_preview',
        'user_link',
        'priority_badge',
        'completed_status',
        'due_date_display',
        'created_at',
        'actions_column'
    ]
    list_filter = [
        'completed',
        'priority',
        'created_at',
        'due_date',
    ]
    search_fields = [
        'title',
        'description',
        'user__username',
        'user__email',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'user',
    ]
    list_per_page = 50
    list_select_related = ['user']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Status & Priority', {
            'fields': ('completed', 'priority')
        }),
        ('Timing', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
    )
    
    def title_preview(self, obj):
        """Display title with truncation."""
        if len(obj.title) > 50:
            return f"{obj.title[:50]}..."
        return obj.title
    title_preview.short_description = 'Title'
    title_preview.admin_order_field = 'title'
    
    def user_link(self, obj):
        """Display user as a link to user admin."""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def priority_badge(self, obj):
        """Display priority with color coding."""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def completed_status(self, obj):
        """Display completion status with icon."""
        if obj.completed:
            return format_html('<span style="color: green;">✓ Completed</span>')
        return format_html('<span style="color: orange;">○ Active</span>')
    completed_status.short_description = 'Status'
    completed_status.admin_order_field = 'completed'
    completed_status.boolean = True
    
    def due_date_display(self, obj):
        """Display due date with overdue indicator."""
        if obj.due_date:
            if obj.is_overdue():
                return format_html(
                    '<span style="color: red; font-weight: bold;">{} (Overdue)</span>',
                    obj.due_date.strftime('%Y-%m-%d %H:%M')
                )
            return obj.due_date.strftime('%Y-%m-%d %H:%M')
        return format_html('<span style="color: gray;">No due date</span>')
    due_date_display.short_description = 'Due Date'
    due_date_display.admin_order_field = 'due_date'
    
    def actions_column(self, obj):
        """Display action links."""
        return format_html(
            '<a href="/admin/tasks/task/{}/change/">Edit</a> | '
            '<a href="/admin/tasks/task/{}/delete/">Delete</a>',
            obj.pk, obj.pk
        )
    actions_column.short_description = 'Actions'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    actions = ['mark_completed', 'mark_active', 'set_high_priority']
    
    def mark_completed(self, request, queryset):
        """Bulk action to mark tasks as completed."""
        updated = queryset.update(completed=True)
        self.message_user(request, f'{updated} task(s) marked as completed.')
    mark_completed.short_description = 'Mark selected tasks as completed'
    
    def mark_active(self, request, queryset):
        """Bulk action to mark tasks as active."""
        updated = queryset.update(completed=False)
        self.message_user(request, f'{updated} task(s) marked as active.')
    mark_active.short_description = 'Mark selected tasks as active'
    
    def set_high_priority(self, request, queryset):
        """Bulk action to set high priority."""
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated} task(s) set to high priority.')
    set_high_priority.short_description = 'Set selected tasks to high priority'
