from django.db import models
from django.utils import timezone
from .models import SiteSettings, PopupNotice


def site_settings(request):
    settings = SiteSettings.objects.first()
    if settings is None:
        settings = SiteSettings.objects.create()
    return {'site_settings': settings}


def popup_notices(request):
    """
    Context processor to fetch currently active popup notices.
    Returns notices that are active, within their date range, and ordered by display order.
    """
    now = timezone.now()
    active_notices = PopupNotice.objects.filter(
        status=True,
        is_active=True
    ).filter(
        # Filter by start_date: show if no start_date set OR start_date has passed
        models.Q(start_date__isnull=True) | models.Q(start_date__lte=now)
    ).filter(
        # Filter by end_date: show if no end_date set OR end_date is in the future
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
    ).order_by('display_order', '-created_at')
    
    return {'popup_notices': active_notices}
