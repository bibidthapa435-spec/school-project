from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
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
    AdmissionApplication,
    ContactMessage,
)
from school_app.forms import AdmissionApplicationForm, ContactMessageForm


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
    principal = Teacher.objects.filter(position__iexact='Principal', status=True).first()

    sliders = list(Slider.objects.filter(status=True).order_by('display_order'))
    programs_qs = list(Program.objects.filter(status=True).order_by('display_order'))
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
            'photo': {'url': '/static/images/logo.jpg'},
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
            'image': {'url': '/static/images/image/firstphoto.jpg'},
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
    last_submission_time = request.session.get('last_admission_submission')
    current_time = timezone.now().timestamp()
    
    if last_submission_time and (current_time - last_submission_time) < 300:
        messages.error(request, 'Please wait 5 minutes before submitting another application.')
        return redirect('/')
    
    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save()
            request.session['last_admission_submission'] = current_time
            
            try:
                subject = f'New Admission Application: {application.application_id}'
                message = f'''
New Admission Application Received

Application ID: {application.application_id}
Student Name: {application.student_name}
Class Applying: {application.class_applying}
Parent Phone: {application.phone}
Email: {application.email or 'Not provided'}
Address: {application.address}
Father's Name: {application.father_name}
Mother's Name: {application.mother_name}
Date of Birth: {application.dob}
Gender: {application.get_gender_display()}
Previous School: {application.previous_school or 'Not provided'}
Submitted: {application.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Please review this application in the Django Admin panel.
'''
                recipient_list = [settings.ADMIN_EMAIL]
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            messages.success(
                request,
                f'Thank you! Your admission application has been submitted successfully. '
                f'Your Application ID is {application.application_id}. We will contact you after review.'
            )
            return redirect('/')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = AdmissionApplicationForm()
    
    return render(request, 'pages/admission.html', get_base_context({'form': form}))


def contact(request):
    last_submission_time = request.session.get('last_contact_submission')
    current_time = timezone.now().timestamp()
    
    # Rate limit check: Redirect to Home instead of 'contact' to prevent infinite loop
    if last_submission_time and (current_time - last_submission_time) < 180:
        messages.error(request, 'Please wait 3 minutes before submitting another message.')
        return redirect('/')
    
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            request.session['last_contact_submission'] = current_time
            
            try:
                subject = f'New Contact Message: {message.subject}'
                email_message = f'''
New Contact Message Received

Name: {message.name}
Email: {message.email}
Phone: {message.phone or 'Not provided'}
Subject: {message.subject}
Message: {message.message}
Submitted: {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Please review this message in the Django Admin panel.
'''
                recipient_list = [settings.ADMIN_EMAIL]
                send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            messages.success(
                request,
                'Thank you for your message! We have received your inquiry and will get back to you shortly.'
            )
            return redirect('/')  # Redirect to Home page after success
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ContactMessageForm()
    
    return render(request, 'pages/contact.html', get_base_context({'form': form}))

def admin_portal(request):
    return redirect('/admin/')


# ============ ADMIN DASHBOARD VIEWS ============

@login_required
def admin_dashboard(request):
    """Main admin dashboard with counts and recent content"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('/')
    
    # Get database counts
    stats = {
        'total_notices': Notice.objects.count(),
        'total_gallery': GalleryPhoto.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_students': AdmissionApplication.objects.filter(status='approved').count(),
        'new_admissions': AdmissionApplication.objects.filter(status='pending').count(),
        'unread_messages': ContactMessage.objects.filter(status='unread').count(),
    }
    
    # Recent content
    recent_notices = Notice.objects.all().order_by('-created_at')[:5]
    recent_admissions = AdmissionApplication.objects.all().order_by('-created_at')[:5]
    recent_messages = ContactMessage.objects.all().order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_notices': recent_notices,
        'recent_admissions': recent_admissions,
        'recent_messages': recent_messages,
        'page_title': 'Dashboard',
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required(login_url='/admin/')
def admin_notices(request):
    """Notices management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    
    notices = Notice.objects.all()
    
    if status_filter:
        notices = notices.filter(status=status_filter == 'active')
    if category_filter:
        notices = notices.filter(category=category_filter)
    if search_query:
        notices = notices.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(description__icontains=search_query)
        )
    
    notices = notices.order_by('-created_at')
    
    context = {
        'notices': notices,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': Notice.CATEGORY_CHOICES,
        'page_title': 'Notices',
    }
    
    return render(request, 'admin/notices.html', context)


@login_required(login_url='/admin/')
def admin_gallery(request):
    """Gallery management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    
    gallery_items = GalleryPhoto.objects.all()
    
    if status_filter:
        gallery_items = gallery_items.filter(status=status_filter == 'active')
    if category_filter:
        gallery_items = gallery_items.filter(category=category_filter)
    if search_query:
        gallery_items = gallery_items.filter(title__icontains=search_query)
    
    gallery_items = gallery_items.order_by('-created_at')
    
    context = {
        'gallery_items': gallery_items,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': GalleryPhoto.CATEGORY_CHOICES,
        'page_title': 'Gallery',
    }
    
    return render(request, 'admin/gallery.html', context)


@login_required(login_url='/admin/')
def admin_teachers(request):
    """Teachers management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')
    search_query = request.GET.get('q', '')
    
    teachers = Teacher.objects.all()
    
    if status_filter:
        teachers = teachers.filter(status=status_filter == 'active')
    if department_filter:
        teachers = teachers.filter(department=department_filter)
    if search_query:
        teachers = teachers.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(position__icontains=search_query)
        )
    
    teachers = teachers.order_by('-created_at')
    
    context = {
        'teachers': teachers,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'search_query': search_query,
        'departments': Teacher.DEPARTMENT_CHOICES,
        'page_title': 'Teachers',
    }
    
    return render(request, 'admin/teachers.html', context)


@login_required(login_url='/admin/')
def admin_students(request):
    """Students/Admissions management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    students = AdmissionApplication.objects.all()
    
    if status_filter:
        students = students.filter(status=status_filter)
    if search_query:
        students = students.filter(
            models.Q(student_name__icontains=search_query) | 
            models.Q(application_id__icontains=search_query) |
            models.Q(father_name__icontains=search_query)
        )
    
    students = students.order_by('-created_at')
    
    context = {
        'students': students,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': AdmissionApplication.STATUS_CHOICES,
        'page_title': 'Students',
    }
    
    return render(request, 'admin/students.html', context)


@login_required(login_url='/admin/')
def admin_programs(request):
    """Programs management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    programs = Program.objects.all()
    
    if status_filter:
        programs = programs.filter(status=status_filter == 'active')
    if search_query:
        programs = programs.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(description__icontains=search_query)
        )
    
    programs = programs.order_by('-created_at')
    
    context = {
        'programs': programs,
        'status_filter': status_filter,
        'search_query': search_query,
        'page_title': 'Programs',
    }
    
    return render(request, 'admin/programs.html', context)


@login_required(login_url='/admin/')
def admin_admissions(request):
    """Admissions management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    admissions = AdmissionApplication.objects.all()
    
    if status_filter:
        admissions = admissions.filter(status=status_filter)
    if search_query:
        admissions = admissions.filter(
            models.Q(student_name__icontains=search_query) | 
            models.Q(application_id__icontains=search_query)
        )
    
    admissions = admissions.order_by('-created_at')
    
    context = {
        'admissions': admissions,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': AdmissionApplication.STATUS_CHOICES,
        'page_title': 'Admissions',
    }
    
    return render(request, 'admin/admissions.html', context)


@login_required(login_url='/admin/')
def admin_messages(request):
    """Contact messages management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    messages = ContactMessage.objects.all()
    
    if status_filter:
        messages = messages.filter(status=status_filter)
    if search_query:
        messages = messages.filter(
            models.Q(name__icontains=search_query) | 
            models.Q(subject__icontains=search_query) |
            models.Q(message__icontains=search_query)
        )
    
    messages = messages.order_by('-created_at')
    
    context = {
        'messages': messages,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': ContactMessage.STATUS_CHOICES,
        'page_title': 'Messages',
    }
    
    return render(request, 'admin/messages.html', context)


@login_required(login_url='/admin/')
def admin_sliders(request):
    """Sliders management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    sliders = Slider.objects.all()
    
    if status_filter:
        sliders = sliders.filter(status=status_filter == 'active')
    if search_query:
        sliders = sliders.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(subtitle__icontains=search_query)
        )
    
    sliders = sliders.order_by('-created_at')
    
    context = {
        'sliders': sliders,
        'status_filter': status_filter,
        'search_query': search_query,
        'page_title': 'Sliders',
    }
    
    return render(request, 'admin/sliders.html', context)


@login_required(login_url='/admin/')
def admin_popups(request):
    """Popup notices management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    active_filter = request.GET.get('is_active', '')
    search_query = request.GET.get('q', '')
    
    popups = PopupNotice.objects.all()
    
    if status_filter:
        popups = popups.filter(status=status_filter == 'active')
    if active_filter:
        popups = popups.filter(is_active=active_filter == 'true')
    if search_query:
        popups = popups.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(message__icontains=search_query)
        )
    
    popups = popups.order_by('-created_at')
    
    context = {
        'popups': popups,
        'status_filter': status_filter,
        'active_filter': active_filter,
        'search_query': search_query,
        'page_title': 'Popup Notices',
    }
    
    return render(request, 'admin/popups.html', context)


@login_required(login_url='/admin/')
def admin_downloads(request):
    """Downloads management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    
    downloads = DownloadResource.objects.all()
    
    if status_filter:
        downloads = downloads.filter(status=status_filter == 'active')
    if category_filter:
        downloads = downloads.filter(category=category_filter)
    if search_query:
        downloads = downloads.filter(title__icontains=search_query)
    
    downloads = downloads.order_by('-created_at')
    
    context = {
        'downloads': downloads,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': DownloadResource.CATEGORY_CHOICES,
        'page_title': 'Downloads',
    }
    
    return render(request, 'admin/downloads.html', context)


@login_required(login_url='/admin/')
def admin_settings(request):
    """Site settings management page"""
    if not request.user.is_staff:
        return redirect('/')
    
    settings_obj = SiteSettings.objects.first()
    if not settings_obj:
        settings_obj = SiteSettings.objects.create()
    
    if request.method == 'POST':
        settings_obj.school_name = request.POST.get('school_name', settings_obj.school_name)
        settings_obj.tagline = request.POST.get('tagline', settings_obj.tagline)
        settings_obj.phone = request.POST.get('phone', settings_obj.phone)
        settings_obj.email = request.POST.get('email', settings_obj.email)
        settings_obj.address = request.POST.get('address', settings_obj.address)
        
        if 'logo' in request.FILES:
            settings_obj.logo = request.FILES['logo']
        if 'favicon' in request.FILES:
            settings_obj.favicon = request.FILES['favicon']
        
        settings_obj.save()
        messages.success(request, 'Settings updated successfully.')
        return redirect('admin_settings')
    
    context = {
        'settings': settings_obj,
        'page_title': 'Settings',
    }
    
    return render(request, 'admin/settings.html', context)


@login_required(login_url='/admin/')
def admin_users(request):
    """Users management page (redirects to Django admin)"""
    if not request.user.is_staff:
        return redirect('/')
    
    return redirect('/admin/auth/user/')