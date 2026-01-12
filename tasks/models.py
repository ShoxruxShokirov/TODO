from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name="Title"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    completed = models.BooleanField(
        default=False,
        verbose_name="Completed"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Priority"
    )
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Due Date"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created at"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated at"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="User"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('task_list')

    def is_overdue(self):
        if self.due_date and not self.completed:
            return timezone.now() > self.due_date
        return False

    def get_priority_color(self):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
        }
        return colors.get(self.priority, 'secondary')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['user', 'priority']),
        ]

