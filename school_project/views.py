import os

from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from results.models import Result
from results.forms import ResultForm

from school_project.data import (
    school_data,
    department_choices,
    notice_category_choices,
    gallery_category_choices,
    confirmed_statistics,
)

from school_app.models import (
    Achievement,
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

from school_app.forms import (
    AdmissionApplicationForm,
    ContactMessageForm,
)


# ============================================================
# BASE CONTEXT
# ============================================================

def _prefers_reduced_motion(request):
    """True when the visitor asked the OS for reduced motion.

    Modern browsers send `Sec-Prefers-Reduced-Motion` / the older
    `Prefer: reduce` hint on every request (Chrome 108+, Safari 16.4+,
    Firefox 115+). The CSS `@media (prefers-reduced-motion: reduce)`
    blocks already cover older browsers; this only lets the template stop
    the Bootstrap carousel from auto-advancing in the first place.

    Returns False when no request is available (e.g. a template rendered
    outside a real HTTP cycle, as in the unit tests).
    """
    if request is None:
        return False
    header = request.META.get('HTTP_SEC_PREFERS_REDUCED_MOTION', '')
    if header.strip().lower() == 'reduce':
        return True
    return 'reduce' in request.META.get('HTTP_PREFER', '').lower()


def get_base_context(extra=None, request=None):
    site_settings = SiteSettings.objects.first()

    if site_settings is None:
        site_settings = SiteSettings.objects.create()

    site_data = {
        'school_name': (
            site_settings.school_name
            or school_data['settings']['school_name']
        ),
        'tagline': (
            site_settings.tagline
            or school_data['settings']['tagline']
        ),
        'phone': (
            site_settings.phone
            or school_data['settings']['phone']
        ),
        'email': (
            site_settings.email
            or school_data['settings']['email']
        ),
        'address': (
            site_settings.address
            or school_data['settings']['address']
        ),
        'logo_url': site_settings.logo_url,
    }

    context = {
        'settings': site_data,
        'schoolSettings': site_data,
        'schoolData': school_data,

        'MARQUEE_NOTICES': list(
            Notice.objects.filter(status=True)
            .order_by('display_order', '-created_at')[:5]
        ),

        'showPreloader': True,

        # Only statistics the school has explicitly confirmed. Unconfirmed
        # numbers (enrolment, pass rate) are never published.
        'statistics': confirmed_statistics(),

        # Server-side view of the visitor's motion preference. Bootstrap's
        # carousel is configured from this so a reduced-motion visitor never
        # gets an auto-advancing slider. CSS and JS read the same media
        # query, so this only removes the JavaScript-driven motion.
        'REDUCED_MOTION': _prefers_reduced_motion(request),
        # Google OAuth is NOT configured on this project (no
        # allauth/socialaccount in INSTALLED_APPS and no /login/google
        # route). The buttons are removed from the auth modal so no link
        # can ever lead to a 404. Set SOCIAL_AUTH_ENABLED=1 only after
        # Google OAuth credentials AND the callback routes exist.
        'ENABLE_PUBLIC_AUTH_MODAL': os.environ.get(
            'ENABLE_PUBLIC_AUTH_MODAL', ''
        ).strip().lower() in {'1', 'true', 'yes'},

        # Real, already-published school photographs used only when a
        # database record has no image (or the image 404s). These are NOT
        # stock images - they are the school's own committed media files.
        # Spaces are percent-encoded because the filenames contain them.
        'FALLBACK_TEACHER_PHOTO': '/media/teachers/govinda%20shrestha.jpg',
        'FALLBACK_GALLERY_IMAGE': '/media/gallery/school%20gate.jpg',
        'FALLBACK_PROGRAM_IMAGE': '/media/programs/program_1.png',
    }

    if extra:
        context.update(extra)

    return context


# ============================================================
# PUBLIC WEBSITE VIEWS
# ============================================================

# Homepage "School Gallery" display data.
#
# The GalleryPhoto categories stored in the database predate the
# Sports/Events/Programs filter taxonomy, so the home section maps each
# known photo (by normalised title) to its fixed caption and filter
# group here, in the view layer, instead of hardcoding it in the
# template. Photos not in the map keep their own title and get a group
# from title keywords, defaulting to Events.
HOME_GALLERY_CAPTIONS = {
    'celebrating student athletic achievements': (
        'Celebrating Student Athletic Achievements', 'Sports',
    ),
    'saraswoti puja': ('Saraswati Puja', 'Events'),
    'saraswati puja': ('Saraswati Puja', 'Events'),
    '2082 farewell to our see graduates': (
        '2082 Farewell to Our SEE Graduates', 'Events',
    ),
    'police awareness and educational program': (
        'Police Awareness and Educational Program', 'Programs',
    ),
    'sports championship celebration': (
        'Sports Championship Celebration', 'Sports',
    ),
    'student health check-up program': (
        'Student Health Check-up Program', 'Programs',
    ),
    'bag, copy & stationery distribution program': (
        'Bag, Copy & Stationery Distribution Program', 'Programs',
    ),
    'students participating in cultural program': (
        'Students Participating in Cultural Program', 'Events',
    ),
}


def _home_gallery_group(title):
    """Filter group for a photo title not in HOME_GALLERY_CAPTIONS."""
    text = (title or '').lower()
    if any(
        word in text
        for word in ('sport', 'athlet', 'championship', 'volleyball', 'football')
    ):
        return 'Sports'
    if any(
        word in text
        for word in ('program', 'health', 'awareness', 'distribution', 'police')
    ):
        return 'Programs'
    return 'Events'


def home(request):
    principal = Teacher.objects.filter(
        position__iexact='Principal',
        status=True
    ).first()

    sliders_qs = Slider.objects.filter(status=True).order_by('display_order')

    programs_qs = list(
        Program.objects.filter(status=True)
        .order_by('display_order')
    )

    for program in programs_qs:
        setattr(
            program,
            'name',
            getattr(program, 'title', None)
        )

    notices_qs = list(
        Notice.objects.filter(status=True)
        .order_by('display_order', '-created_at')[:3]
    )

    teachers_qs = list(
        Teacher.objects.filter(status=True)
        .order_by('display_order', '-created_at')[:4]
    )

    for teacher in teachers_qs:
        setattr(
            teacher,
            'name',
            getattr(teacher, 'title', None)
        )

    gallery_items = list(
        GalleryPhoto.objects.filter(status=True)
        .order_by('display_order', '-created_at')[:8]
    )

    for photo in gallery_items:
        title = getattr(photo, 'title', '') or ''
        caption, group = HOME_GALLERY_CAPTIONS.get(
            title.strip().lower(), (title, None),
        )
        if group is None:
            group = _home_gallery_group(title)
        setattr(photo, 'gallery_caption', caption or title)
        setattr(photo, 'gallery_group', group)

    achievements_qs = list(
        Achievement.objects.filter(status=True)
        .order_by('display_order', '-achievement_date', '-created_at')[:4]
    )

    context = get_base_context({
        'sliders': list(sliders_qs),
        'principal': principal,
        'programs': programs_qs,
        'notices': notices_qs,
        'teachers': teachers_qs,
        'gallery_items': gallery_items,
        'achievements': achievements_qs,
        'testimonials': school_data.get('testimonials', []),
    }, request=request)

    return render(
        request,
        'home/index.html',
        context
    )


def about(request):
    return render(
        request,
        'pages/about.html',
        get_base_context()
    )


def principal_message(request):
    principal = Teacher.objects.filter(
        position__iexact='Principal',
        status=True
    ).first()

    return render(
        request,
        'pages/principal_message.html',
        get_base_context({
            'principal': principal
        })
    )


def facilities(request):
    return render(
        request,
        'pages/facilities.html',
        get_base_context()
    )


# ============================================================
# RESULTS PUBLIC VIEW
# ============================================================

def results(request):
    results_list = Result.objects.all().order_by(
        '-published_date'
    )

    return render(
        request,
        'results/results.html',
        get_base_context({
            'results': results_list
        })
    )


# ============================================================
# NOTICES
# ============================================================

def notices(request):
    selected_category = request.GET.get(
        'category',
        ''
    )

    query = request.GET.get(
        'q',
        ''
    ).strip()

    notices_qs = Notice.objects.filter(
        status=True
    ).order_by(
        'display_order',
        '-created_at'
    )

    if selected_category:
        notices_qs = notices_qs.filter(
            category=selected_category
        )

    if query:
        notices_qs = notices_qs.filter(
            models.Q(title__icontains=query)
            |
            models.Q(description__icontains=query)
        )

    return render(
        request,
        'notice/notice_list.html',
        get_base_context({
            'notices': list(notices_qs),
            'categories': notice_category_choices,
            'selected_category': selected_category,
            'query': query,
        })
    )


def notice_detail(request, slug):
    notice = Notice.objects.filter(
        slug=slug,
        status=True
    ).first()

    if not notice:

        notice = {
            'title': 'Notice not found',
            'description': (
                'The requested notice could not be found.'
            ),
            'slug': slug,
        }

        recent_notices = list(
            Notice.objects.filter(status=True)
            .order_by('-created_at')[:4]
        )

    else:

        recent_notices = list(
            Notice.objects.filter(status=True)
            .exclude(slug=slug)
            .order_by('-created_at')[:4]
        )

    return render(
        request,
        'notice/notice_detail.html',
        get_base_context({
            'notice': notice,
            'recent_notices': recent_notices,
        })
    )


# ============================================================
# GALLERY
# ============================================================

def gallery(request):

    selected_cat = request.GET.get(
        'cat',
        ''
    )

    published = GalleryPhoto.objects.filter(
        status=True
    )

    gallery_items = published.order_by(
        'display_order',
        '-created_at'
    )

    if selected_cat:
        gallery_items = gallery_items.filter(
            category=selected_cat
        )

    items = list(gallery_items)

    # Published photos per category, so the filter chips can show real counts
    # instead of every category looking equally full.
    counts = dict(
        published.values('category')
        .annotate(total=models.Count('id'))
        .values_list('category', 'total')
    )

    categories = [
        {
            'id': category_id,
            'label': label,
            'count': counts.get(category_id, 0),
        }
        for category_id, label in gallery_category_choices
    ]

    return render(
        request,
        'gallery/gallery_list.html',
        get_base_context({
            'gallery_items': items,
            'categories': categories,
            'selected_cat': selected_cat,
            'selected_cat_label': dict(gallery_category_choices).get(
                selected_cat,
                ''
            ),
            'shown_photos': len(items),
            'total_photos': sum(counts.values()),
        })
    )


# ============================================================
# TEACHERS
# ============================================================

def teachers(request):

    selected_dept = request.GET.get(
        'dept',
        ''
    )

    teachers_list = Teacher.objects.filter(
        status=True
    ).order_by(
        'display_order',
        '-created_at'
    )

    if selected_dept:
        teachers_list = teachers_list.filter(
            department=selected_dept
        )

    teachers_list = list(teachers_list)

    for teacher in teachers_list:

        setattr(
            teacher,
            'name',
            getattr(teacher, 'title', None)
        )

    return render(
        request,
        'teacher/teacher_list.html',
        get_base_context({
            'teachers': teachers_list,
            'departments': department_choices,
            'selected_dept': selected_dept,
        })
    )


def teacher_detail(request, slug):

    teacher = Teacher.objects.filter(
        slug=slug,
        status=True
    ).first()

    if not teacher:

        messages.error(
            request,
            'The requested teacher profile could not be found.'
        )

        return redirect('teachers')

    other_teachers = list(
        Teacher.objects.filter(status=True)
        .exclude(slug=slug)
        .order_by(
            'display_order',
            '-created_at'
        )[:4]
    )

    for other_teacher in other_teachers:

        setattr(
            other_teacher,
            'name',
            getattr(other_teacher, 'title', None)
        )

    return render(
        request,
        'teacher/teacher_detail.html',
        get_base_context({
            'teacher': teacher,
            'other_teachers': other_teachers,
        })
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

def achievements(request):
    selected_type = request.GET.get('type', '')

    achievements_list = Achievement.objects.filter(
        status=True
    ).order_by(
        'display_order',
        '-achievement_date',
        '-created_at'
    )

    if selected_type:
        achievements_list = achievements_list.filter(
            achievement_type=selected_type
        )

    achievements_list = list(achievements_list)

    return render(
        request,
        'achievement/achievement_list.html',
        get_base_context({
            'achievements': achievements_list,
            'achievement_types': Achievement.ACHIEVEMENT_TYPE_CHOICES,
            'selected_type': selected_type,
        })
    )


def achievement_detail(request, slug):
    achievement = Achievement.objects.filter(
        slug=slug,
        status=True
    ).first()

    if not achievement:
        messages.error(
            request,
            'The requested achievement could not be found.'
        )
        return redirect('achievements')

    other_achievements = list(
        Achievement.objects.filter(status=True)
        .exclude(slug=slug)
        .order_by(
            'display_order',
            '-achievement_date',
            '-created_at'
        )[:4]
    )

    return render(
        request,
        'achievement/achievement_detail.html',
        get_base_context({
            'achievement': achievement,
            'other_achievements': other_achievements,
        })
    )


# ============================================================
# PROGRAMS
# ============================================================

def programs(request):

    programs_qs = list(
        Program.objects.filter(status=True)
        .order_by('display_order')
    )

    for program in programs_qs:

        setattr(
            program,
            'name',
            getattr(program, 'title', None)
        )

    return render(
        request,
        'programs/program_list.html',
        get_base_context({
            'programs': programs_qs
        })
    )


def program_detail(request, slug):

    program = Program.objects.filter(
        slug=slug,
        status=True
    ).first()

    if not program:

        messages.error(
            request,
            'The requested program could not be found.'
        )

        return redirect('programs')

    other_programs = list(
        Program.objects.filter(status=True)
        .exclude(slug=slug)
        .order_by('display_order')[:4]
    )

    for other_program in other_programs:

        setattr(
            other_program,
            'name',
            getattr(other_program, 'title', None)
        )

    return render(
        request,
        'programs/program_detail.html',
        get_base_context({
            'program': program,
            'other_programs': other_programs,
        })
    )


# ============================================================
# DOWNLOADS
# ============================================================

def downloads(request):

    selected_cat = request.GET.get(
        'cat',
        ''
    )

    downloads_list = DownloadResource.objects.filter(
        status=True
    ).order_by(
        'display_order',
        '-created_at'
    )

    if selected_cat:

        downloads_list = downloads_list.filter(
            category=selected_cat
        )

    return render(
        request,
        'pages/downloads.html',
        get_base_context({
            'downloads': list(downloads_list),
            'selected_cat': selected_cat,
        })
    )


def download_resource_file(request, slug):
    """Force the browser to download a resource file as an attachment."""

    resource = get_object_or_404(DownloadResource, slug=slug, status=True)

    if not resource.file:
        raise Http404('No file uploaded for this resource.')

    if not resource.file.storage.exists(resource.file.name):
        raise Http404('File not found on the server.')

    return FileResponse(
        resource.file.open('rb'),
        as_attachment=True,
        filename=os.path.basename(resource.file.name),
    )


# ============================================================
# ADMISSION
# ============================================================

def admission(request):

    last_submission_time = request.session.get(
        'last_admission_submission'
    )

    current_time = timezone.now().timestamp()

    if (
        last_submission_time
        and
        (current_time - last_submission_time) < 300
    ):

        messages.error(
            request,
            'Please wait 5 minutes before submitting another application.'
        )

        return redirect('/')

    if request.method == 'POST':

        form = AdmissionApplicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            application = form.save()

            request.session[
                'last_admission_submission'
            ] = current_time

            try:

                subject = (
                    f'New Admission Application: '
                    f'{application.application_id}'
                )

                message = f"""
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
"""

                recipient_list = [
                    settings.ADMIN_EMAIL
                ]

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=True
                )

            except Exception as error:

                print(
                    f"Email sending failed: {error}"
                )

            messages.success(
                request,
                f'Thank you! Your admission application has been '
                f'submitted successfully. Your Application ID is '
                f'{application.application_id}. We will contact you '
                f'after review.'
            )

            return redirect('/')

        else:

            messages.error(
                request,
                'Please correct the errors in the form.'
            )

    else:

        form = AdmissionApplicationForm()

    return render(
        request,
        'pages/admission.html',
        get_base_context({
            'form': form
        })
    )


# ============================================================
# CONTACT
# ============================================================

def contact(request):

    last_submission_time = request.session.get(
        'last_contact_submission'
    )

    current_time = timezone.now().timestamp()

    if (
        last_submission_time
        and
        (current_time - last_submission_time) < 180
    ):

        messages.error(
            request,
            'Please wait 3 minutes before submitting another message.'
        )

        return redirect('/')

    if request.method == 'POST':

        form = ContactMessageForm(
            request.POST
        )

        if form.is_valid():

            contact_message = form.save()

            request.session[
                'last_contact_submission'
            ] = current_time

            try:

                subject = (
                    f'New Contact Message: '
                    f'{contact_message.subject}'
                )

                email_message = f"""
New Contact Message Received

Name: {contact_message.name}
Email: {contact_message.email}
Phone: {contact_message.phone or 'Not provided'}
Subject: {contact_message.subject}
Message: {contact_message.message}
Submitted: {contact_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Please review this message in the Django Admin panel.
"""

                recipient_list = [
                    settings.ADMIN_EMAIL
                ]

                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=True
                )

            except Exception as error:

                print(
                    f"Email sending failed: {error}"
                )

            messages.success(
                request,
                'Thank you for your message! We have received your '
                'inquiry and will get back to you shortly.'
            )

            return redirect('/')

        else:

            messages.error(
                request,
                'Please correct the errors in the form.'
            )

    else:

        form = ContactMessageForm()

    return render(
        request,
        'pages/contact.html',
        get_base_context({
            'form': form
        })
    )


# ============================================================
# SEO
# ============================================================

def _canonical_origin(request):
    """Scheme + host of the current request, used to build absolute URLs."""
    return f'{request.scheme}://{request.get_host()}'


def robots_txt(request):
    """robots.txt built from the real routes.

    Admin, dashboard and the login surfaces are disallowed so search
    engines only ever index public school pages.
    """
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /admin-dashboard/',
        'Disallow: /admin-portal/',
        'Disallow: /login',
        'Disallow: /register',
        '',
        f'Sitemap: {_canonical_origin(request)}{reverse("sitemap")}',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap(request):
    """XML sitemap of the public pages plus every published item.

    Only records with status=True are listed, so unpublished content
    never appears in search results.
    """
    origin = _canonical_origin(request)
    today = timezone.now().date()

    def entry(location, lastmod=None, changefreq='monthly', priority='0.6'):
        return {
            'loc': f'{origin}{location}',
            'lastmod': (lastmod or today).isoformat(),
            'changefreq': changefreq,
            'priority': priority,
        }

    static_pages = [
        ('home', '1.0', 'weekly'),
        ('about', '0.7', 'monthly'),
        ('principal_message', '0.6', 'yearly'),
        ('facilities', '0.6', 'monthly'),
        ('programs', '0.8', 'monthly'),
        ('teachers', '0.8', 'weekly'),
        ('achievements', '0.7', 'weekly'),
        ('gallery', '0.7', 'weekly'),
        ('notices', '0.8', 'daily'),
        ('admission', '0.9', 'monthly'),
        ('downloads', '0.6', 'monthly'),
        ('contact', '0.7', 'yearly'),
    ]

    urls = [
        entry(reverse(name), changefreq=freq, priority=priority)
        for name, priority, freq in static_pages
    ]
    urls.append(entry(reverse('results:list'), changefreq='monthly', priority='0.6'))

    # Published detail pages.
    for model, url_name in (
        (Teacher, 'teacher_detail'),
        (Program, 'program_detail'),
        (Achievement, 'achievement_detail'),
        (Notice, 'notice_detail'),
    ):
        for obj in model.objects.filter(status=True):
            urls.append(
                entry(
                    reverse(url_name, args=[obj.slug]),
                    changefreq='weekly',
                    priority='0.5',
                )
            )

    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        body.append('  <url>')
        body.append(f'    <loc>{u["loc"]}</loc>')
        body.append(f'    <lastmod>{u["lastmod"]}</lastmod>')
        body.append(f'    <changefreq>{u["changefreq"]}</changefreq>')
        body.append(f'    <priority>{u["priority"]}</priority>')
        body.append('  </url>')
    body.append('</urlset>')

    return HttpResponse('\n'.join(body), content_type='application/xml')


def admin_portal(request):
    return redirect('/admin/')


# ============================================================
# CUSTOM ADMIN DASHBOARD
# ============================================================

@login_required(login_url='/admin/')
def admin_dashboard(request):

    if not request.user.is_staff:

        messages.error(
            request,
            'You do not have permission to access the admin dashboard.'
        )

        return redirect('/')

    stats = {
        'total_notices': Notice.objects.count(),
        'total_gallery': GalleryPhoto.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_students': AdmissionApplication.objects.filter(
            status='approved'
        ).count(),
        'new_admissions': AdmissionApplication.objects.filter(
            status='pending'
        ).count(),
        'unread_messages': ContactMessage.objects.filter(
            status='unread'
        ).count(),

        # RESULT COUNT ADDED
        'total_results': Result.objects.count(),
    }

    recent_notices = Notice.objects.all().order_by(
        '-created_at'
    )[:5]

    recent_admissions = AdmissionApplication.objects.all().order_by(
        '-created_at'
    )[:5]

    recent_messages = ContactMessage.objects.all().order_by(
        '-created_at'
    )[:5]

    context = {
        'stats': stats,
        'recent_notices': recent_notices,
        'recent_admissions': recent_admissions,
        'recent_messages': recent_messages,
        'page_title': 'Dashboard',
    }

    return render(
        request,
        'admin/dashboard.html',
        context
    )


# ============================================================
# ADMIN RESULTS
# IMPORTANT: ONLY ONE admin_results FUNCTION
# ============================================================
@login_required(login_url='/admin/')
def admin_results(request):

    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to access this page.'
        )
        return redirect('/')

    if request.method == 'POST':
        form = ResultForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Result added successfully!'
            )

            return redirect('admin_results')

        else:
            messages.error(
                request,
                'Please correct the errors in the Result form.'
            )

    else:
        form = ResultForm()

    results_list = Result.objects.all().order_by(
        '-published_date'
    )

    context = {
        'results': results_list,
        'form': form,
        'page_title': 'Results',
    }

    return render(
        request,
        'admin/admin_results.html',
        context
    )


@login_required(login_url='/admin/')
def admin_result_edit(request, pk):

    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to edit results.'
        )
        return redirect('/')

    result = get_object_or_404(Result, id=pk)

    if request.method == 'POST':
        form = ResultForm(
            request.POST,
            request.FILES,
            instance=result
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Result updated successfully!'
            )

            return redirect('admin_results')

        else:
            messages.error(
                request,
                'Please correct the errors in the Result form.'
            )

    else:
        form = ResultForm(instance=result)

    context = {
        'result': result,
        'form': form,
        'page_title': 'Edit Result',
    }

    return render(
        request,
        'admin/admin_result_edit.html',
        context
    )


@login_required(login_url='/admin/')
def admin_result_delete(request, pk):

    if not request.user.is_staff:
        messages.error(
            request,
            'You do not have permission to delete results.'
        )
        return redirect('/')

    result = get_object_or_404(Result, id=pk)

    if request.method == 'POST':
        result.delete()

        messages.success(
            request,
            'Result deleted successfully!'
        )

        return redirect('admin_results')

    return redirect('admin_results')


# ============================================================
# ADMIN NOTICES
# ============================================================

@login_required(login_url='/admin/')
def admin_notices(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    category_filter = request.GET.get(
        'category',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    notices_qs = Notice.objects.all()

    if status_filter:

        notices_qs = notices_qs.filter(
            status=status_filter == 'active'
        )

    if category_filter:

        notices_qs = notices_qs.filter(
            category=category_filter
        )

    if search_query:

        notices_qs = notices_qs.filter(
            models.Q(title__icontains=search_query)
            |
            models.Q(description__icontains=search_query)
        )

    notices_qs = notices_qs.order_by(
        '-created_at'
    )

    context = {
        'notices': notices_qs,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': Notice.CATEGORY_CHOICES,
        'page_title': 'Notices',
    }

    return render(
        request,
        'admin/notices.html',
        context
    )


# ============================================================
# ADMIN GALLERY
# ============================================================

@login_required(login_url='/admin/')
def admin_gallery(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    category_filter = request.GET.get(
        'category',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    gallery_items = GalleryPhoto.objects.all()

    if status_filter:

        gallery_items = gallery_items.filter(
            status=status_filter == 'active'
        )

    if category_filter:

        gallery_items = gallery_items.filter(
            category=category_filter
        )

    if search_query:

        gallery_items = gallery_items.filter(
            title__icontains=search_query
        )

    gallery_items = gallery_items.order_by(
        '-created_at'
    )

    context = {
        'gallery_items': gallery_items,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': GalleryPhoto.CATEGORY_CHOICES,
        'page_title': 'Gallery',
    }

    return render(
        request,
        'admin/gallery.html',
        context
    )


# ============================================================
# ADMIN TEACHERS
# ============================================================

@login_required(login_url='/admin/')
def admin_teachers(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    department_filter = request.GET.get(
        'department',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    teachers_qs = Teacher.objects.all()

    if status_filter:

        teachers_qs = teachers_qs.filter(
            status=status_filter == 'active'
        )

    if department_filter:

        teachers_qs = teachers_qs.filter(
            department=department_filter
        )

    if search_query:

        teachers_qs = teachers_qs.filter(
            models.Q(title__icontains=search_query)
            |
            models.Q(position__icontains=search_query)
        )

    teachers_qs = teachers_qs.order_by(
        '-created_at'
    )

    context = {
        'teachers': teachers_qs,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'search_query': search_query,
        'departments': Teacher.DEPARTMENT_CHOICES,
        'page_title': 'Teachers',
    }

    return render(
        request,
        'admin/teachers.html',
        context
    )


# ============================================================
# ADMIN STUDENTS
# ============================================================

@login_required(login_url='/admin/')
def admin_students(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    students = AdmissionApplication.objects.all()

    if status_filter:

        students = students.filter(
            status=status_filter
        )

    if search_query:

        students = students.filter(
            models.Q(student_name__icontains=search_query)
            |
            models.Q(application_id__icontains=search_query)
            |
            models.Q(father_name__icontains=search_query)
        )

    students = students.order_by(
        '-created_at'
    )

    context = {
        'students': students,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': AdmissionApplication.STATUS_CHOICES,
        'page_title': 'Students',
    }

    return render(
        request,
        'admin/students.html',
        context
    )


# ============================================================
# ADMIN PROGRAMS
# ============================================================

@login_required(login_url='/admin/')
def admin_programs(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    programs_qs = Program.objects.all()

    if status_filter:

        programs_qs = programs_qs.filter(
            status=status_filter == 'active'
        )

    if search_query:

        programs_qs = programs_qs.filter(
            models.Q(title__icontains=search_query)
            |
            models.Q(description__icontains=search_query)
        )

    programs_qs = programs_qs.order_by(
        '-created_at'
    )

    context = {
        'programs': programs_qs,
        'status_filter': status_filter,
        'search_query': search_query,
        'page_title': 'Programs',
    }

    return render(
        request,
        'admin/programs.html',
        context
    )


# ============================================================
# ADMIN ADMISSIONS
# ============================================================

@login_required(login_url='/admin/')
def admin_admissions(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    admissions = AdmissionApplication.objects.all()

    if status_filter:

        admissions = admissions.filter(
            status=status_filter
        )

    if search_query:

        admissions = admissions.filter(
            models.Q(student_name__icontains=search_query)
            |
            models.Q(application_id__icontains=search_query)
        )

    admissions = admissions.order_by(
        '-created_at'
    )

    context = {
        'admissions': admissions,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': AdmissionApplication.STATUS_CHOICES,
        'page_title': 'Admissions',
    }

    return render(
        request,
        'admin/admissions.html',
        context
    )


# ============================================================
# ADMIN MESSAGES
# ============================================================

@login_required(login_url='/admin/')
def admin_messages(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    contact_messages = ContactMessage.objects.all()

    if status_filter:

        contact_messages = contact_messages.filter(
            status=status_filter
        )

    if search_query:

        contact_messages = contact_messages.filter(
            models.Q(name__icontains=search_query)
            |
            models.Q(subject__icontains=search_query)
            |
            models.Q(message__icontains=search_query)
        )

    contact_messages = contact_messages.order_by(
        '-created_at'
    )

    context = {
        'messages': contact_messages,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': ContactMessage.STATUS_CHOICES,
        'page_title': 'Messages',
    }

    return render(
        request,
        'admin/messages.html',
        context
    )


# ============================================================
# ADMIN SLIDERS
# ============================================================

@login_required(login_url='/admin/')
def admin_sliders(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    sliders = Slider.objects.all()

    if status_filter:

        sliders = sliders.filter(
            status=status_filter == 'active'
        )

    if search_query:

        sliders = sliders.filter(
            models.Q(title__icontains=search_query)
            |
            models.Q(subtitle__icontains=search_query)
        )

    sliders = sliders.order_by(
        '-created_at'
    )

    context = {
        'sliders': sliders,
        'status_filter': status_filter,
        'search_query': search_query,
        'page_title': 'Sliders',
    }

    return render(
        request,
        'admin/sliders.html',
        context
    )


# ============================================================
# ADMIN POPUPS
# ============================================================

@login_required(login_url='/admin/')
def admin_popups(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    active_filter = request.GET.get(
        'is_active',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    popups = PopupNotice.objects.all()

    if status_filter:

        popups = popups.filter(
            status=status_filter == 'active'
        )

    if active_filter:

        popups = popups.filter(
            is_active=active_filter == 'true'
        )

    if search_query:

        popups = popups.filter(
            models.Q(title__icontains=search_query)
            |
            models.Q(message__icontains=search_query)
        )

    popups = popups.order_by(
        '-created_at'
    )

    context = {
        'popups': popups,
        'status_filter': status_filter,
        'active_filter': active_filter,
        'search_query': search_query,
        'page_title': 'Popup Notices',
        'now': timezone.now(),
    }

    return render(
        request,
        'admin/popups.html',
        context
    )


# ============================================================
# ADMIN DOWNLOADS
# ============================================================

@login_required(login_url='/admin/')
def admin_downloads(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    category_filter = request.GET.get(
        'category',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    downloads_qs = DownloadResource.objects.all()

    if status_filter:

        downloads_qs = downloads_qs.filter(
            status=status_filter == 'active'
        )

    if category_filter:

        downloads_qs = downloads_qs.filter(
            category=category_filter
        )

    if search_query:

        downloads_qs = downloads_qs.filter(
            title__icontains=search_query
        )

    downloads_qs = downloads_qs.order_by(
        '-created_at'
    )

    context = {
        'downloads': downloads_qs,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'categories': DownloadResource.CATEGORY_CHOICES,
        'page_title': 'Downloads',
    }

    return render(
        request,
        'admin/downloads.html',
        context
    )


# ============================================================
# ADMIN SETTINGS
# ============================================================

@login_required(login_url='/admin/')
def admin_settings(request):

    if not request.user.is_staff:
        return redirect('/')

    settings_obj = SiteSettings.objects.first()

    if not settings_obj:
        settings_obj = SiteSettings.objects.create()

    if request.method == 'POST':

        settings_obj.school_name = request.POST.get(
            'school_name',
            settings_obj.school_name
        )

        settings_obj.tagline = request.POST.get(
            'tagline',
            settings_obj.tagline
        )

        settings_obj.phone = request.POST.get(
            'phone',
            settings_obj.phone
        )

        settings_obj.email = request.POST.get(
            'email',
            settings_obj.email
        )

        settings_obj.address = request.POST.get(
            'address',
            settings_obj.address
        )

        if 'logo' in request.FILES:
            settings_obj.logo = request.FILES['logo']

        if 'favicon' in request.FILES:
            settings_obj.favicon = request.FILES['favicon']

        settings_obj.save()

        messages.success(
            request,
            'Settings updated successfully.'
        )

        return redirect('admin_settings')

    context = {
        'settings': settings_obj,
        'page_title': 'Settings',
    }

    return render(
        request,
        'admin/settings.html',
        context
    )


# ============================================================
# ADMIN USERS
# ============================================================

@login_required(login_url='/admin/')
def admin_users(request):

    if not request.user.is_staff:
        return redirect('/')

    return redirect('/admin/auth/user/')


# ============================================================
# ADMIN ACHIEVEMENTS
# ============================================================

@login_required(login_url='/admin/')
def admin_achievements(request):

    if not request.user.is_staff:
        return redirect('/')

    status_filter = request.GET.get(
        'status',
        ''
    )

    type_filter = request.GET.get(
        'type',
        ''
    )

    search_query = request.GET.get(
        'q',
        ''
    )

    achievements_qs = Achievement.objects.all()

    if status_filter:

        achievements_qs = achievements_qs.filter(
            status=status_filter == 'active'
        )

    if type_filter:

        achievements_qs = achievements_qs.filter(
            achievement_type=type_filter
        )

    if search_query:

        achievements_qs = achievements_qs.filter(
            models.Q(title__icontains=search_query)
            |
            models.Q(student_name__icontains=search_query)
            |
            models.Q(event_name__icontains=search_query)
            |
            models.Q(description__icontains=search_query)
            |
            models.Q(rank_or_position__icontains=search_query)
        )

    achievements_qs = achievements_qs.order_by(
        '-achievement_date',
        '-created_at'
    )

    context = {
        'achievements': achievements_qs,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'achievement_types': Achievement.ACHIEVEMENT_TYPE_CHOICES,
        'page_title': 'Achievements',
    }

    return render(
        request,
        'admin/achievements.html',
        context
    )