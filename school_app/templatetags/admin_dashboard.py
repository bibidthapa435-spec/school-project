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
    if student_count == 0:
        student_count = 349

    return [
        {
            'label': 'Total Notices',
            'count': get_model_count('school_app', 'Notice') or 25,
            'description': 'Active notices',
            'url': safe_reverse('admin:school_app_notice_changelist'),
            'icon': 'fa-solid fa-file-lines',
            'icon_bg': 'stat-icon--blue',
        },
        {
            'label': 'Total Teachers',
            'count': get_model_count('school_app', 'Teacher') or 18,
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
            'count': get_model_count('school_app', 'GalleryPhoto') or 126,
            'description': 'Total images',
            'url': safe_reverse('admin:school_app_galleryphoto_changelist'),
            'icon': 'fa-solid fa-image',
            'icon_bg': 'stat-icon--indigo',
        },
        {
            'label': 'Total Users',
            'count': User.objects.count() or 7,
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


@register.inclusion_tag('admin/includes/recent_notices.html')
def admin_dashboard_recent_notices():
    notice_model = get_model_queryset('school_app', 'Notice')
    notices = []
    if notice_model is not None:
        notices = list(notice_model.order_by('-created_at')[:5])

    if not notices:
        notices = _sample_notices()

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

    if not photos:
        photos = _sample_gallery_photos()

    return {
        'photos': photos,
        'view_all_url': safe_reverse('admin:school_app_galleryphoto_changelist'),
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


def _sample_notices():
    from types import SimpleNamespace

    samples = [
        ('School Re-opens After Summer Vacation', 'Aug 15, 2026', True, True),
        ('SEE Result 2081 Published', 'Jun 28, 2026', True, False),
        ('Parent-Teacher Meeting', 'May 10, 2026', False, True),
        ('Basketball Competition – Inter House', 'Apr 22, 2026', True, False),
        ('Admission Open for Grade 11', 'Mar 01, 2026', True, True),
    ]
    return [
        SimpleNamespace(
            title=title,
            created_at=timezone.now(),
            status=active,
            is_new=is_new,
            pk=None,
            display_date=date,
        )
        for title, date, active, is_new in samples
    ]


def _sample_gallery_photos():
    from types import SimpleNamespace

    samples = [
        ('Students', '/media/gallery/firstphoto.jpg'),
        ('School Building', '/media/gallery/school gate.jpg'),
        ('Sports Activities', '/media/gallery/fourthphoto.jpg'),
        ('Teachers', '/media/gallery/mayor.jpg'),
        ('School Programs', '/media/gallery/fifthphoto.jpg'),
    ]
    return [
        SimpleNamespace(
            title=title,
            image=SimpleNamespace(url=url),
            pk=None,
        )
        for title, url in samples
    ]