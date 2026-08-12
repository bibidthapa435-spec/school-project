from django import template
from django.apps import apps
from django.urls import NoReverseMatch, reverse

register = template.Library()


def safe_reverse(name, fallback='#'):
    try:
        return reverse(name)
    except NoReverseMatch:
        return fallback


def get_model_count(app_label, model_name):
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return 0
    return model.objects.count()


@register.filter
def startswith(text, prefix):
    if not text or not prefix:
        return False
    return str(text).startswith(str(prefix))


@register.simple_tag
def admin_dashboard_metric_cards():
    return [
        {
            'label': 'Total Students',
            'count': get_model_count('school_app', 'Student'),
            'url': safe_reverse('admin:school_app_admissionapplication_changelist'),
            'icon': 'fa-solid fa-user-graduate',
        },
        {
            'label': 'Total Teachers',
            'count': get_model_count('school_app', 'Teacher'),
            'url': safe_reverse('admin:school_app_teacher_changelist'),
            'icon': 'fa-solid fa-chalkboard-user',
        },
        {
            'label': 'Total Notices',
            'count': get_model_count('school_app', 'Notice'),
            'url': safe_reverse('admin:school_app_notice_changelist'),
            'icon': 'fa-solid fa-bullhorn',
        },
        {
            'label': 'Total Gallery Photos',
            'count': get_model_count('school_app', 'GalleryPhoto'),
            'url': safe_reverse('admin:school_app_galleryphoto_changelist'),
            'icon': 'fa-solid fa-images',
        },
        {
            'label': 'Total Programs',
            'count': get_model_count('school_app', 'Program'),
            'url': safe_reverse('admin:school_app_program_changelist'),
            'icon': 'fa-solid fa-graduation-cap',
        },
        {
            'label': 'Total Admission Applications',
            'count': get_model_count('school_app', 'AdmissionApplication'),
            'url': safe_reverse('admin:school_app_admissionapplication_changelist'),
            'icon': 'fa-solid fa-file-signature',
        },
        {
            'label': 'Total Contact Messages',
            'count': get_model_count('school_app', 'ContactMessage'),
            'url': safe_reverse('admin:school_app_contactmessage_changelist'),
            'icon': 'fa-solid fa-envelope',
        },
        {
            'label': 'Total Sliders',
            'count': get_model_count('school_app', 'Slider'),
            'url': safe_reverse('admin:school_app_slider_changelist'),
            'icon': 'fa-solid fa-images',
        },
    ]


@register.inclusion_tag('admin/dashboard_recent_activity.html')
def admin_dashboard_recent_activity():
    return {
        'notices': get_model_count('school_app', 'Notice') and apps.get_model('school_app', 'Notice').objects.order_by('-created_at')[:5] or [],
        'applications': get_model_count('school_app', 'AdmissionApplication') and apps.get_model('school_app', 'AdmissionApplication').objects.order_by('-created_at')[:5] or [],
        'messages': get_model_count('school_app', 'ContactMessage') and apps.get_model('school_app', 'ContactMessage').objects.order_by('-created_at')[:5] or [],
    }
