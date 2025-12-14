from django import template

register = template.Library()

@register.filter
def average(value):
    """Calculate average of a list"""
    if value:
        return sum(value) / len(value)
    return 0

@register.filter
def sum(value):
    """Calculate sum of a list"""
    if value:
        return sum(value)
    return 0