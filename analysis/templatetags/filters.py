from django import template
import calendar

register = template.Library()

@register.filter
def format_sales(value):
    """Formats numbers with commas and adds 'K' or 'M' if applicable."""
    try:
        value = float(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:,.2f}"  # Adds commas
    except (ValueError, TypeError):
        return value  # Return unchanged if an error occurs

@register.filter
def month_name_filter(month_number):
    """Convert a month number (1-12) into its corresponding name (e.g., 3 → 'March')."""
    try:
        month_number = int(month_number)  # Ensure it's an integer
        return calendar.month_name[month_number]  # Returns 'March' for 3
    except (ValueError, IndexError):
        return ""  # Return empty string if conversion fails
    

@register.filter
def format_commas(value):
    """Formats numbers with commas and exactly 4 decimal places."""
    try:
        value = float(value)
        return f"{value:,.4f}"  # Formats with commas and 4 decimal places
    except (ValueError, TypeError):
        return value  # Return unchanged if an error occurs
