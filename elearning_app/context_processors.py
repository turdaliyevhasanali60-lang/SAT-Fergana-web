# media/context_processors.py
from .models import SiteSetting, Category


def site_settings(request):
    """Add site settings to all templates"""
    try:
        settings = SiteSetting.objects.first()
    except SiteSetting.DoesNotExist:
        settings = None

    return {'site_settings': settings}


def navigation_categories(request):
    """Add categories to navigation"""
    categories = Category.objects.filter(is_active=True)[:8]
    return {'navigation_categories': categories}