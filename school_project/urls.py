from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('notices/', views.notices, name='notices'),
    path('notices/<slug:slug>/', views.notice_detail, name='notice_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('teachers/', views.teachers, name='teachers'),
    path('teachers/<slug:slug>/', views.teacher_detail, name='teacher_detail'),
    path('programs/', views.programs, name='programs'),
    path('programs/<slug:slug>/', views.program_detail, name='program_detail'),
    path('downloads/', views.downloads, name='downloads'),
    path('admission/', views.admission, name='admission'),
    path('contact/', views.contact, name='contact'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
