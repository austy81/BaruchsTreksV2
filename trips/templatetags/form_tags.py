from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_attrs')
def add_attrs(field, attrs):
    """Add attributes to a form field widget"""
    attrs_list = attrs.split(',')
    attrs_dict = {}
    
    for attr in attrs_list:
        if ':' in attr:
            key, value = attr.split(':', 1)
            attrs_dict[key.strip()] = value.strip()
        else:
            attrs_dict[attr.strip()] = True
    
    return field.as_widget(attrs=attrs_dict)
