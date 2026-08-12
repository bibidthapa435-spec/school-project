from .models import SiteSettings


def site_settings(request):
    settings = SiteSettings.objects.first()
    if settings is None:
        settings = SiteSettings.objects.create()
    return {'site_settings': settings}
