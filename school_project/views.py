from django.shortcuts import render
from django.http import HttpResponse

school_settings = {
    'school_name': "Shree Jaljala Secondary School",
    'tagline': "Quality Education for a Brighter Future from Nursery to Class 10 (SEE)",
    'logo_url': "/static/images/logo.png",
    'phone': "+977-9842000000 / +977-9800000000",
    'email': "info@shreejaljala.edu.np",
    'address': "Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Nepal",
    'estd': "2045 B.S.",
    'facebook_url': "https://facebook.com",
    'youtube_url': "https://youtube.com"
}

def get_base_context(extra={}):
    context = {'settings': school_settings}
    context.update(extra)
    return context

def home(request):
    return render(request, 'home/index.html', get_base_context())

def about(request):
    return render(request, 'pages/about.html', get_base_context())

def notices(request):
    return render(request, 'notice/notice_list.html', get_base_context({'notices': []}))

def notice_detail(request, slug):
    return render(request, 'notice/notice_detail.html', get_base_context({'slug': slug}))

def gallery(request):
    return render(request, 'gallery/gallery_list.html', get_base_context({'gallery': []}))

def teachers(request):
    return render(request, 'teacher/teacher_list.html', get_base_context({'teachers': []}))

def teacher_detail(request, slug):
    return render(request, 'teacher/teacher_detail.html', get_base_context({'slug': slug}))

def programs(request):
    return render(request, 'programs/program_list.html', get_base_context({'programs': []}))

def program_detail(request, slug):
    return render(request, 'programs/program_detail.html', get_base_context({'slug': slug}))

def downloads(request):
    return render(request, 'pages/downloads.html', get_base_context({'downloads': []}))

def admission(request):
    return render(request, 'pages/admission.html', get_base_context())

def contact(request):
    return render(request, 'pages/contact.html', get_base_context())

def admin_portal(request):
    return render(request, 'admin/admin_dashboard.html', get_base_context())
