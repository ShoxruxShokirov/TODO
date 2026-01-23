"""
Forms for tasks and user registration with advanced validation.

Senior-level implementation with:
- Custom field validation
- Clean methods
- Helpful error messages
- Bootstrap styling
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from .models import Task


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks with advanced validation.
    
    Features:
    - Custom validation for due dates
    - Title sanitization
    - Priority selection
    - Bootstrap styling
    """
    
    title = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'What needs to be done?',
            'autofocus': True,
            'maxlength': 255,
        }),
        max_length=255,
        required=True,
        help_text="Enter a clear and descriptive task title (max 255 characters)"
    )
    
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add a description (optional)',
            'rows': 3,
            'maxlength': 2000,
        }),
        required=False,
        max_length=2000,
        help_text="Optional detailed description (max 2000 characters)"
    )
    
    priority = forms.ChoiceField(
        label="Priority",
        choices=Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='medium',
        required=True,
        help_text="Set the priority level for this task"
    )
    
    due_date = forms.DateTimeField(
        label="Due Date",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        required=False,
        help_text="Optional deadline for this task"
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only add tags if it exists in database (safe check)
        # Color field removed as requested
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                # Get table name
                table_name = Task._meta.db_table
                # Check if tags column exists (works for SQLite and PostgreSQL)
                if 'sqlite' in connection.vendor.lower():
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [row[1] for row in cursor.fetchall()]
                else:
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = %s AND column_name = 'tags'
                    """, [table_name])
                    columns = [row[0] for row in cursor.fetchall()]
                
                # Add tags field only if column exists
                if 'tags' in columns:
                    self.fields['tags'] = forms.CharField(
                        label="Tags",
                        widget=forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'work, personal, urgent (comma-separated)',
                        }),
                        required=False,
                        help_text="Add tags separated by commas"
                    )
        except Exception:
            # If check fails for any reason, don't add fields
            # This ensures the form works even if database check fails
            pass

    def clean_title(self):
        """Validate and sanitize title."""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError(_('Title cannot be empty.'))
        if len(title) < 3:
            raise ValidationError(_('Title must be at least 3 characters long.'))
        return title

    def clean_description(self):
        """Validate description."""
        description = self.cleaned_data.get('description', '').strip()
        if description and len(description) > 2000:
            raise ValidationError(_('Description cannot exceed 2000 characters.'))
        return description

    def clean_due_date(self):
        """Validate due date."""
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            # Allow past dates (tasks can be created after due date)
            # But warn if it's too far in the past (more than 1 year)
            if due_date < timezone.now() - timedelta(days=365):
                raise ValidationError(_('Due date cannot be more than 1 year in the past.'))
        return due_date

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        description = cleaned_data.get('description')
        
        # Ensure title and description are not the same
        if title and description and title.strip().lower() == description.strip().lower():
            raise ValidationError(_('Description should be different from the title.'))
        
        return cleaned_data


class RegisterForm(UserCreationForm):
    """
    User registration form with enhanced validation and styling.
    
    Features:
    - Username validation
    - Password strength requirements
    - Bootstrap styling
    - Helpful error messages
    """
    
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username...',
            'autofocus': True,
            'maxlength': 150,
        }),
        max_length=150,
        required=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password...'
        }),
        required=True,
        help_text="Password must be at least 8 characters and not too common."
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password...'
        }),
        required=True,
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def clean_username(self):
        """Validate username."""
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise ValidationError(_('Username cannot be empty.'))
        # Убираем все пробелы
        username = username.replace(' ', '')
        if not username:
            raise ValidationError(_('Username cannot be empty or contain only spaces.'))
        if len(username) < 3:
            raise ValidationError(_('Username must be at least 3 characters long.'))
        if not username.replace('_', '').replace('.', '').replace('-', '').isalnum():
            raise ValidationError(_('Username can only contain letters, numbers, and _/./- characters.'))
        return username

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Passwords do not match.'))
        
        return cleaned_data
