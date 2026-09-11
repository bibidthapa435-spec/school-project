# Shree Jaljala Secondary School - Project Structure

## Overview
Django-based school management system with website for Shree Jaljala Secondary School, Panchkhapan, Sankhuwasabha, Nepal.

## Directory Structure

```
management/
├── school_project/              # Django project configuration
│   ├── __init__.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
│
├── school_app/                  # Main Django application
│   ├── __init__.py
│   ├── admin.py                 # Admin panel configuration
│   ├── apps.py                  # App configuration
│   ├── context_processors.py    # Template context processors
│   ├── forms.py                 # Django forms
│   ├── models.py                # Database models
│   ├── views.py                 # View functions
│   ├── urls.py                  # App URL configuration
│   ├── templatetags/            # Custom template tags
│   │   ├── __init__.py
│   │   └── admin_dashboard.py   # Admin dashboard template tags
│   ├── management/              # Management commands
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_school_data.py
│   └── migrations/              # Database migrations
│
├── results/                     # Results application
│
├── templates/                   # HTML templates
│   ├── base.html                # Base template
│   ├── includes/                # Shared components
│   │   ├── navbar.html          # Navigation bar
│   │   ├── footer.html          # Footer
│   │   ├── auth_modal.html      # Authentication modal
│   │   ├── messages.html        # Messages/alerts
│   │   ├── notice_marquee.html  # Notice marquee
│   │   ├── popup_notice.html    # Popup notices
│   │   └── preloader.html       # Page preloader
│   ├── home/                    # Home page templates
│   ├── pages/                   # Static pages
│   ├── admin/                   # Admin panel templates
│   ├── teacher/                 # Teacher templates
│   ├── gallery/                 # Gallery templates
│   ├── notice/                  # Notice templates
│   ├── programs/                # Programs templates
│   └── achievement/             # Achievement templates
│
├── static/                      # Static files (CSS, JS, images)
│   ├── css/                     # Stylesheets
│   │   ├── style.css            # Main stylesheet
│   │   ├── home.css             # Home page styles
│   │   ├── about.css            # About page styles
│   │   ├── navbar.css           # Navbar styles
│   │   ├── popup.css            # Popup styles
│   │   ├── responsive.css       # Responsive styles
│   │   └── modern-enhancements.css
│   ├── js/                      # JavaScript files
│   │   ├── main.js              # Main JavaScript
│   │   └── popup.js             # Popup JavaScript
│   ├── images/                  # Images
│   │   ├── image/               # General images
│   │   ├── saraswotipuja/       # Saraswati Puja images
│   │   └── sport/               # Sports images
│   └── admin/                   # Admin static files
│       ├── css/
│       │   └── custom_admin.css
│       └── js/
│           ├── custom_admin.js
│           └── popup_admin.js
│
├── media/                       # User-uploaded files
│   ├── achievements/            # Achievement images
│   ├── downloads/               # Download files
│   ├── gallery/                 # Gallery images
│   ├── notices/                 # Notice images
│   ├── popups/                  # Popup images
│   ├── programs/                # Program images
│   ├── results/                 # Results files
│   ├── site/                    # Site settings files
│   ├── slider/                  # Slider images
│   ├── teachers/                # Teacher photos
│   └── uploads/                 # General uploads
│
├── venv/                        # Virtual environment
├── requirements.txt             # Python dependencies
├── manage.py                    # Django management script
├── .env.example                 # Environment variables example
├── .gitignore                   # Git ignore file
├── .editorconfig                # Editor configuration
├── README.md                    # Project readme
├── DEPLOYMENT.md                # Deployment guide
├── render_setup.md              # Render setup guide
└── PROJECT_STRUCTURE.md         # This file
```

## Key Features
- **Public Website**: Home, About, Programs, Teachers, Gallery, Notices, Results, Contact
- **Admin Panel**: Custom admin dashboard with management features
- **Student Portal**: Login/Register system for students
- **Admission System**: Online admission form
- **Results Management**: Exam results publishing
- **Notice Management**: School notices with popup support
- **Gallery**: Photo gallery with lightbox
- **Achievements**: Student and school achievements

## Technology Stack
- **Backend**: Django 6.1 (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: PostgreSQL (production), SQLite (development)
- **Deployment**: Render

## Setup Instructions
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run development server: `python manage.py runserver`

## Environment Variables
Create a `.env` file with the following variables:
- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_DEBUG` - Debug mode (True/False)
- `DJANGO_ALLOWED_HOSTS` - Allowed hosts
- `DATABASE_URL` - Database URL (optional)
- `EMAIL_HOST` - Email host
- `EMAIL_PORT` - Email port
- `EMAIL_HOST_USER` - Email username
- `EMAIL_HOST_PASSWORD` - Email password

## License
© 2026 Shree Jaljala Secondary School. All Rights Reserved.