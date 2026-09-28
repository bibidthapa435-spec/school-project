from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
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

    path('achievements/', views.achievements, name='achievements'),
    path('achievements/<slug:slug>/', views.achievement_detail, name='achievement_detail'),

    path('programs/', views.programs, name='programs'),
    path('programs/<slug:slug>/', views.program_detail, name='program_detail'),

    path('downloads/', views.downloads, name='downloads'),
    path(
        'downloads/<slug:slug>/file/',
        views.download_resource_file,
        name='download_resource_file'
    ),

    path('admission/', views.admission, name='admission'),

    path('contact/', views.contact, name='contact'),

    # =========================
    # SEO
    # =========================

    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap, name='sitemap'),

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

    # Achievements
    path(
        'admin-dashboard/achievements/',
        views.admin_achievements,
        name='admin_achievements'
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

# MEDIA FILES
#
# Root cause of the audit's 404s. In DEBUG, django.conf.urls.static.static()
# registers the /media/ pattern. In production (DEBUG=False) that helper
# returns an EMPTY list, so unless the web server itself serves the folder,
# every /media/... request 404s.
#
# Render's free dynos are also ephemeral: any file uploaded through the
# admin disappears on the next deploy/redeploy. The two 404s in the audit
# had different causes and this fixes one of them:
#
#   /media/sliders/sport_3.jpg
#       The database referenced "sliders/sport_3.jpg" but the committed
#       file was at "slider/sport_3.jpg" (singular). The real school
#       photo was copied to the path the database points at, so it now
#       resolves. No image was invented.
#
#   /media/notices/1000031894.jpg
#       The database references a file that exists NOWHERE in the
#       repository and was never committed. There is no honest way to
#       recreate it, so it is listed under Remaining Issues: the school
#       must re-upload that image from the admin. Until then the
#       frontend fallback hides it cleanly instead of showing a broken
#       image box.
#
# Serving MEDIA_ROOT in production is safe (Django's serve view blocks
# path traversal) and makes every committed school photo reliably
# reachable. Making NEW uploads durable additionally requires shared
# object storage (S3 / R2 / Spaces) - an infrastructure change that needs
# the school owner's Render account and billing approval, and which is
# deliberately NOT made here. See DEPLOYMENT.md.
_re_path = re_path(
    r'^media/(?P<path>.*)$',
    serve,
    {'document_root': settings.MEDIA_ROOT},
)
urlpatterns += [_re_path]