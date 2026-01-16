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
    try:
        return [tag.strip() for tag in str(value).split(',') if tag.strip()]
    except (AttributeError, TypeError):
        return []


@register.filter
def json_data(value):
    """
    Convert Python data structure to JSON string for use in JavaScript.
    
    Args:
        value: Python data structure (list, dict, etc.)
        
    Returns:
        str: JSON string (marked as safe for template)
    """
    if value is None:
        return mark_safe('[]')
    try:
        return mark_safe(json.dumps(value))
    except (TypeError, ValueError) as e:
        # Return empty array if serialization fails
        return mark_safe('[]')


@register.filter
def safe_getattr(obj, attr_name):
    """
    Safely get attribute from object, return empty string if doesn't exist.
    
    Args:
        obj: Object to get attribute from
        attr_name: Name of the attribute
        
    Returns:
        Attribute value or empty string
    """
    try:
        return getattr(obj, attr_name, '') or ''
    except (AttributeError, Exception):
        return ''

