from datetime import timedelta

from django import template
from django.apps import apps
from django.contrib.auth.models import User
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

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


def get_model_queryset(app_label, model_name):
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return None
    return model.objects.all()


@register.filter
def startswith(text, prefix):
    if not text or not prefix:
        return False
    return str(text).startswith(str(prefix))


@register.simple_tag
def admin_dashboard_metric_cards():
    notice_qs = get_model_queryset('school_app', 'Notice')
    active_notices = notice_qs.filter(status=True).count() if notice_qs is not None else 0

    student_count = get_model_count('school_app', 'AdmissionApplication')

    return [
        {
            'label': 'Total Notices',
            'count': get_model_count('school_app', 'Notice'),
            'description': 'Active notices',
            'url': safe_reverse('admin:school_app_notice_changelist'),
            'icon': 'fa-solid fa-file-lines',
            'icon_bg': 'stat-icon--blue',
        },
        {
            'label': 'Total Teachers',
            'count': get_model_count('school_app', 'Teacher'),
            'description': 'Registered teachers',
            'url': safe_reverse('admin:school_app_teacher_changelist'),
            'icon': 'fa-solid fa-chalkboard-user',
            'icon_bg': 'stat-icon--navy',
        },
        {
            'label': 'Total Students',
            'count': student_count,
            'description': 'Registered students',
            'url': safe_reverse('admin:school_app_admissionapplication_changelist'),
            'icon': 'fa-solid fa-user-graduate',
            'icon_bg': 'stat-icon--sky',
        },
        {
            'label': 'Gallery Images',
            'count': get_model_count('school_app', 'GalleryPhoto'),
            'description': 'Total images',
            'url': safe_reverse('admin:school_app_galleryphoto_changelist'),
            'icon': 'fa-solid fa-image',
            'icon_bg': 'stat-icon--indigo',
        },
        {
            'label': 'Achievements',
            'count': get_model_count('school_app', 'Achievement'),
            'description': 'Student & school achievements',
            'url': safe_reverse('admin:school_app_achievement_changelist'),
            'icon': 'fa-solid fa-trophy',
            'icon_bg': 'stat-icon--gold',
        },
        {
            'label': 'Total Users',
            'count': User.objects.count(),
            'description': 'System users',
            'url': safe_reverse('admin:auth_user_changelist'),
            'icon': 'fa-solid fa-users',
            'icon_bg': 'stat-icon--teal',
        },
    ]


@register.simple_tag
def admin_dashboard_quick_actions():
    return [
        {
            'label': 'Add Notice',
            'icon': 'fa-solid fa-bullhorn',
            'url': safe_reverse('admin:school_app_notice_add'),
            'color': 'quick-action--blue',
        },
        {
            'label': 'Add Slider',
            'icon': 'fa-solid fa-panorama',
            'url': safe_reverse('admin:school_app_slider_add'),
            'color': 'quick-action--navy',
        },
        {
            'label': 'Add Gallery',
            'icon': 'fa-solid fa-images',
            'url': safe_reverse('admin:school_app_galleryphoto_add'),
            'color': 'quick-action--sky',
        },
        {
            'label': 'Add Teacher',
            'icon': 'fa-solid fa-person-chalkboard',
            'url': safe_reverse('admin:school_app_teacher_add'),
            'color': 'quick-action--indigo',
        },
        {
            'label': 'Add Student',
            'icon': 'fa-solid fa-user-plus',
            'url': safe_reverse('admin:school_app_admissionapplication_add'),
            'color': 'quick-action--teal',
        },
        {
            'label': 'Add Achievement',
            'icon': 'fa-solid fa-trophy',
            'url': safe_reverse('admin:school_app_achievement_add'),
            'color': 'quick-action--gold',
        },
        {
            'label': 'Add Page',
            'icon': 'fa-solid fa-file-circle-plus',
            'url': safe_reverse('admin:school_app_sitesettings_changelist'),
            'color': 'quick-action--slate',
        },
    ]


@register.simple_tag
def admin_sidebar_nav_items():
    return [
        {
            'label': 'Dashboard',
            'icon': 'fa-solid fa-gauge-high',
            'url': safe_reverse('admin:index'),
            'match': '/admin/',
            'exact': True,
        },
        {
            'label': 'Notices',
            'icon': 'fa-solid fa-bullhorn',
            'url': safe_reverse('admin:school_app_notice_changelist'),
            'match': safe_reverse('admin:school_app_notice_changelist'),
        },
        {
            'label': 'Sliders',
            'icon': 'fa-solid fa-panorama',
            'url': safe_reverse('admin:school_app_slider_changelist'),
            'match': safe_reverse('admin:school_app_slider_changelist'),
        },
        {
            'label': 'Gallery',
            'icon': 'fa-solid fa-images',
            'url': safe_reverse('admin:school_app_galleryphoto_changelist'),
            'match': safe_reverse('admin:school_app_galleryphoto_changelist'),
        },
        {
            'label': 'Teachers',
            'icon': 'fa-solid fa-chalkboard-user',
            'url': safe_reverse('admin:school_app_teacher_changelist'),
            'match': safe_reverse('admin:school_app_teacher_changelist'),
        },
        {
            'label': 'Achievements',
            'icon': 'fa-solid fa-trophy',
            'url': safe_reverse('admin:school_app_achievement_changelist'),
            'match': safe_reverse('admin:school_app_achievement_changelist'),
        },
        {
            'label': 'Students',
            'icon': 'fa-solid fa-user-graduate',
            'url': safe_reverse('admin:school_app_admissionapplication_changelist'),
            'match': safe_reverse('admin:school_app_admissionapplication_changelist'),
        },
        {
            'label': 'Programs',
            'icon': 'fa-solid fa-graduation-cap',
            'url': safe_reverse('admin:school_app_program_changelist'),
            'match': safe_reverse('admin:school_app_program_changelist'),
        },
        {
            'label': 'Pages',
            'icon': 'fa-solid fa-file-lines',
            'url': safe_reverse('admin:school_app_sitesettings_changelist'),
            'match': safe_reverse('admin:school_app_sitesettings_changelist'),
        },
        {
            'label': 'Popup Notices',
            'icon': 'fa-solid fa-window-restore',
            'url': safe_reverse('admin:school_app_popupnotice_changelist'),
            'match': safe_reverse('admin:school_app_popupnotice_changelist'),
        },
        {
            'label': 'Users',
            'icon': 'fa-solid fa-users',
            'url': safe_reverse('admin:auth_user_changelist'),
            'match': safe_reverse('admin:auth_user_changelist'),
        },
        {
            'label': 'Settings',
            'icon': 'fa-solid fa-gear',
            'url': safe_reverse('admin:school_app_sitesettings_changelist'),
            'match': safe_reverse('admin:school_app_sitesettings_changelist'),
        },
    ]


@register.simple_tag
def admin_dashboard_analytics_data():
    """Returns analytics data for the dashboard chart and mini cards."""
    return {
        'visitors': 0,
        'page_views': 0,
        'avg_session': '00:00',
        'bounce_rate': '0%',
        'chart_data': {
            'month': {
                'labels': ['Aug 1', 'Aug 5', 'Aug 9', 'Aug 13', 'Aug 17', 'Aug 21', 'Aug 25', 'Aug 29'],
                'visitors': [0, 0, 0, 0, 0, 0, 0, 0],
                'page_views': [0, 0, 0, 0, 0, 0, 0, 0],
            },
            'week': {
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'visitors': [0, 0, 0, 0, 0, 0, 0],
                'page_views': [0, 0, 0, 0, 0, 0, 0],
            },
            'year': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'visitors': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'page_views': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            },
        },
    }


@register.inclusion_tag('admin/includes/recent_notices.html')
def admin_dashboard_recent_notices():
    notice_model = get_model_queryset('school_app', 'Notice')
    notices = []
    if notice_model is not None:
        notices = list(notice_model.order_by('-created_at')[:5])

    week_ago = timezone.now() - timedelta(days=7)
    for notice in notices:
        if hasattr(notice, 'created_at'):
            notice.is_new = notice.created_at >= week_ago
        else:
            notice.is_new = getattr(notice, 'is_new', False)

    return {
        'notices': notices,
        'view_all_url': safe_reverse('admin:school_app_notice_changelist'),
    }


@register.inclusion_tag('admin/includes/recent_gallery.html')
def admin_dashboard_recent_gallery():
    gallery_model = get_model_queryset('school_app', 'GalleryPhoto')
    photos = []
    if gallery_model is not None:
        photos = list(gallery_model.filter(status=True).order_by('-created_at')[:5])

    return {
        'photos': photos,
        'view_all_url': safe_reverse('admin:school_app_galleryphoto_changelist'),
    }


@register.inclusion_tag('admin/includes/recent_achievements.html')
def admin_dashboard_recent_achievements():
    achievement_model = get_model_queryset('school_app', 'Achievement')
    achievements = []
    if achievement_model is not None:
        achievements = list(achievement_model.filter(status=True).order_by('-achievement_date', '-created_at')[:5])

    return {
        'achievements': achievements,
        'view_all_url': safe_reverse('admin:school_app_achievement_changelist'),
    }


@register.inclusion_tag('admin/dashboard_recent_activity.html')
def admin_dashboard_recent_activity():
    notice_model = get_model_queryset('school_app', 'Notice')
    application_model = get_model_queryset('school_app', 'AdmissionApplication')
    message_model = get_model_queryset('school_app', 'ContactMessage')

    return {
        'notices': list(notice_model.order_by('-created_at')[:5]) if notice_model is not None else [],
        'applications': list(application_model.order_by('-created_at')[:5]) if application_model is not None else [],
        'messages': list(message_model.order_by('-created_at')[:5]) if message_model is not None else [],
    }


