"""
Custom template filters for tasks.
"""
import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def split_tags(value):
    """
    Split comma-separated tags into a list.
    
    Args:
        value: String with comma-separated tags
        
    Returns:
        list: List of tag strings
    """
    if not value:
        return []
    return [tag.strip() for tag in str(value).split(',') if tag.strip()]


@register.filter
def json_data(value):
    """
    Convert Python data structure to JSON string for use in JavaScript.
    
    Args:
        value: Python data structure (list, dict, etc.)
        
    Returns:
        str: JSON string (marked as safe for template)
    """
    return mark_safe(json.dumps(value))

