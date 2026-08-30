from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    # =========================
    # MAIN WEBSITE URLs
    # =========================
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('principal-message/', views.principal_message, name='principal_message'),

    path('facilities/', views.facilities, name='facilities'),

    path('notices/', views.notices, name='notices'),
    path('notices/<slug:slug>/', views.notice_detail, name='notice_detail'),

    path('results/', include('results.urls'), name='results'),

    path('gallery/', views.gallery, name='gallery'),

    path('teachers/', views.teachers, name='teachers'),
    path('teachers/<slug:slug>/', views.teacher_detail, name='teacher_detail'),

    path('programs/', views.programs, name='programs'),
    path('programs/<slug:slug>/', views.program_detail, name='program_detail'),

    path('downloads/', views.downloads, name='downloads'),

    path('admission/', views.admission, name='admission'),

    path('contact/', views.contact, name='contact'),

    path('admin-portal/', views.admin_portal, name='admin_portal'),

    # Django Admin
    path('admin/', admin.site.urls),


    # =========================
    # ADMIN DASHBOARD URLs
    # =========================

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'admin-dashboard/notices/',
        views.admin_notices,
        name='admin_notices'
    ),

    path(
        'admin-dashboard/gallery/',
        views.admin_gallery,
        name='admin_gallery'
    ),

    path(
        'admin-dashboard/teachers/',
        views.admin_teachers,
        name='admin_teachers'
    ),

    path(
        'admin-dashboard/students/',
        views.admin_students,
        name='admin_students'
    ),

    path(
        'admin-dashboard/programs/',
        views.admin_programs,
        name='admin_programs'
    ),

    path(
        'admin-dashboard/admissions/',
        views.admin_admissions,
        name='admin_admissions'
    ),

    path(
        'admin-dashboard/messages/',
        views.admin_messages,
        name='admin_messages'
    ),

    path(
        'admin-dashboard/sliders/',
        views.admin_sliders,
        name='admin_sliders'
    ),

    path(
        'admin-dashboard/popups/',
        views.admin_popups,
        name='admin_popups'
    ),

    path(
        'admin-dashboard/downloads/',
        views.admin_downloads,
        name='admin_downloads'
    ),

    path(
        'admin-dashboard/settings/',
        views.admin_settings,
        name='admin_settings'
    ),

    path(
        'admin-dashboard/users/',
        views.admin_users,
        name='admin_users'
    ),

    # Results
    path(
        'admin-dashboard/results/',
        views.admin_results,
        name='admin_results'
    ),

    # Edit Result
    path(
        'admin-dashboard/results/<int:pk>/edit/',
        views.admin_result_edit,
        name='admin_result_edit'
    ),

    # Delete Result
    path(
        'admin-dashboard/results/<int:pk>/delete/',
        views.admin_result_delete,
        name='admin_result_delete'
    ),
]


# =========================
# STATIC & MEDIA FILES
# =========================

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATICFILES_DIRS[0]
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )