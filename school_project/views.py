from django.shortcuts import render, redirect
from django.db import models
from school_project.data import (
    school_data,
    department_choices,
    notice_category_choices,
    gallery_category_choices,
)
from school_app.models import (
    Notice,
    GalleryPhoto,
    Teacher,
    Program,
    DownloadResource,
    PopupNotice,
    Slider,
    SiteSettings,
)


def get_base_context(extra=None):
    site_settings = SiteSettings.objects.first()
    if site_settings is None:
        site_settings = SiteSettings.objects.create()

    settings = {
        'school_name': site_settings.school_name or school_data['settings']['school_name'],
        'tagline': site_settings.tagline or school_data['settings']['tagline'],
        'phone': site_settings.phone or school_data['settings']['phone'],
        'email': site_settings.email or school_data['settings']['email'],
        'address': site_settings.address or school_data['settings']['address'],
        'logo_url': site_settings.logo_url,
    }

    context = {
        'settings': settings,
        'schoolSettings': settings,
        'schoolData': school_data,
        'MARQUEE_NOTICES': list(Notice.objects.filter(status=True).order_by('display_order', '-created_at')[:5]),
        'showPreloader': True,
    }
    if extra:
        context.update(extra)
    return context


def home(request):
    active_popup = PopupNotice.objects.filter(is_active=True, status=True).order_by('-created_at').first()
    principal = Teacher.objects.filter(position__iexact='Principal', status=True).first()

    sliders = list(Slider.objects.filter(status=True).order_by('display_order'))
    programs_qs = list(Program.objects.filter(status=True).order_by('display_order'))
    # templates expect a `name` attribute for programs (data.py used 'name')
    for p in programs_qs:
        setattr(p, 'name', getattr(p, 'title', None))

    notices_qs = list(Notice.objects.filter(status=True).order_by('display_order', '-created_at')[:3])

    teachers_qs = list(Teacher.objects.filter(status=True).order_by('display_order', '-created_at')[:4])
    for t in teachers_qs:
        setattr(t, 'name', getattr(t, 'title', None))

    gallery_items = list(GalleryPhoto.objects.filter(status=True).order_by('display_order', '-created_at')[:8])

    return render(
        request,
        'home/index.html',
        get_base_context(
            {
                'sliders': sliders,
                'activePopup': active_popup,
                'principal': principal,
                'programs': programs_qs,
                'notices': notices_qs,
                'teachers': teachers_qs,
                'gallery_items': gallery_items,
                'testimonials': school_data.get('testimonials', []),
            }
        ),
    )


def about(request):
    return render(request, 'pages/about.html', get_base_context())


def principal_message(request):
    principal = Teacher.objects.filter(position__iexact='Principal', status=True).first()
    return render(request, 'pages/principal_message.html', get_base_context({'principal': principal}))


def facilities(request):
    return render(request, 'pages/facilities.html', get_base_context())


def notices(request):
    selected_category = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()
    notices_qs = Notice.objects.filter(status=True).order_by('display_order', '-created_at')
    if selected_category:
        notices_qs = notices_qs.filter(category=selected_category)
    if query:
        notices_qs = notices_qs.filter(models.Q(title__icontains=query) | models.Q(description__icontains=query))
    return render(
        request,
        'notice/notice_list.html',
        get_base_context(
            {
                'notices': list(notices_qs),
                'categories': notice_category_choices,
                'selected_category': selected_category,
                'query': query,
            }
        ),
    )


def notice_detail(request, slug):
    notice = Notice.objects.filter(slug=slug, status=True).first()
    if not notice:
        notice = {
            'title': 'Notice not found',
            'description': 'The requested notice could not be found.',
            'slug': slug,
        }
        recent_notices = list(Notice.objects.filter(status=True).order_by('-created_at')[:4])
    else:
        recent_notices = list(Notice.objects.filter(status=True).exclude(slug=slug).order_by('-created_at')[:4])
    return render(
        request,
        'notice/notice_detail.html',
        get_base_context({'notice': notice, 'recent_notices': recent_notices}),
    )


def gallery(request):
    selected_cat = request.GET.get('cat', '')
    gallery_items = GalleryPhoto.objects.filter(status=True).order_by('display_order', '-created_at')
    if selected_cat:
        gallery_items = gallery_items.filter(category=selected_cat)
    return render(
        request,
        'gallery/gallery_list.html',
        get_base_context(
            {
                'gallery_items': list(gallery_items),
                'categories': gallery_category_choices,
                'selected_cat': selected_cat,
            }
        ),
    )


def teachers(request):
    selected_dept = request.GET.get('dept', '')
    teachers_list = Teacher.objects.filter(status=True).order_by('display_order', '-created_at')
    if selected_dept:
        teachers_list = teachers_list.filter(department=selected_dept)
    teachers_list = list(teachers_list)
    for t in teachers_list:
        setattr(t, 'name', getattr(t, 'title', None))
    return render(
        request,
        'teacher/teacher_list.html',
        get_base_context(
            {
                'teachers': teachers_list,
                'departments': department_choices,
                'selected_dept': selected_dept,
            }
        ),
    )


def teacher_detail(request, slug):
    teacher = Teacher.objects.filter(slug=slug, status=True).first()
    if not teacher:
        teacher = {
            'name': 'Teacher not found',
            'position': 'N/A',
            'photo': {'url': '/static/images/logo.png'},
            'slug': slug,
            'biography': 'No biography is available for this teacher.',
        }
        other_teachers = list(Teacher.objects.filter(status=True).order_by('display_order', '-created_at')[:4])
    else:
        setattr(teacher, 'name', getattr(teacher, 'title', None))
        other_teachers = list(Teacher.objects.filter(status=True).exclude(slug=slug).order_by('display_order', '-created_at')[:4])
        for t in other_teachers:
            setattr(t, 'name', getattr(t, 'title', None))
    return render(
        request,
        'teacher/teacher_detail.html',
        get_base_context({'teacher': teacher, 'other_teachers': other_teachers}),
    )


def programs(request):
    programs_qs = list(Program.objects.filter(status=True).order_by('display_order'))
    for p in programs_qs:
        setattr(p, 'name', getattr(p, 'title', None))
    return render(request, 'programs/program_list.html', get_base_context({'programs': programs_qs}))


def program_detail(request, slug):
    program = Program.objects.filter(slug=slug, status=True).first()
    if not program:
        program = {
            'name': 'Program not found',
            'description': 'The requested program could not be found.',
            'slug': slug,
            'duration': 'N/A',
            'fee': 'N/A',
            'image': {'url': '/static/images/logo.png'},
            'eligibility': 'N/A',
        }
        other_programs = list(Program.objects.filter(status=True).order_by('display_order')[:4])
    else:
        setattr(program, 'name', getattr(program, 'title', None))
        other_programs = list(Program.objects.filter(status=True).exclude(slug=slug).order_by('display_order')[:4])
        for p in other_programs:
            setattr(p, 'name', getattr(p, 'title', None))
    return render(
        request,
        'programs/program_detail.html',
        get_base_context({'program': program, 'other_programs': other_programs}),
    )


def downloads(request):
    selected_cat = request.GET.get('cat', '')
    downloads_list = DownloadResource.objects.filter(status=True).order_by('display_order', '-created_at')
    if selected_cat:
        downloads_list = downloads_list.filter(category=selected_cat)
    return render(
        request,
        'pages/downloads.html',
        get_base_context({'downloads': list(downloads_list), 'selected_cat': selected_cat}),
    )


def admission(request):
    return render(request, 'pages/admission.html', get_base_context())


def contact(request):
    return render(request, 'pages/contact.html', get_base_context())


def admin_portal(request):
    return redirect('/admin/')
