# networks/templatetags/dict_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get a value from a dictionary by key"""
    return dictionary.get(key)