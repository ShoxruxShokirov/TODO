from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task


class TaskForm(forms.ModelForm):
    title = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'What needs to be done?',
            'autofocus': True
        }),
        max_length=255,
        required=True
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add a description (optional)',
            'rows': 3
        }),
        required=False
    )
    priority = forms.ChoiceField(
        label="Priority",
        choices=Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='medium',
        required=True
    )
    due_date = forms.DateTimeField(
        label="Due Date",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        required=False
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date']


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username...'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password...'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password...'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

