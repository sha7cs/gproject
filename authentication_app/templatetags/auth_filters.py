from django import template

register = template.Library()

@register.filter
def add_class(value, arg):
    """
    Adds the given class to the field.
    Usage: {{ form.field_name|add_class:"css_class" }}
    """
    return value.as_widget(attrs={'class': arg})
