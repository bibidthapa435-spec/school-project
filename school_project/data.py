from typing import List, Dict, Optional


def slugify(text: str) -> str:
    return (
        text
        .lower()
        .strip()
        .replace(' ', '-')
        .replace('_', '-')
    )


school_settings = {
    'school_name': 'Shree Jaljala Secondary School',
    'tagline': 'Quality Education for a Brighter Future from Nursery to Class 10 (SEE)',
    'logo_url': '/static/images/logo.png',
    'phone': '+977-9842000000 / +977-9800000000',
    'email': 'info@shreejaljala.edu.np',
    'address': 'Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Nepal',
    'estd': '2045 B.S.',
    'facebook_url': 'https://facebook.com',
    'youtube_url': 'https://youtube.com',
    'instagram_url': 'https://instagram.com',
}


school_data = {
    'settings': school_settings,
    'sliders': [],
    'teachers': [],
    'notices': [],
    'gallery': [],
    'programs': [],
    'downloads': [],
    'popups': [],
    'admissions': [],
    'contacts': [],
    'testimonials': [],
}


department_choices = [
    ['management', 'School Management & Administration'],
    ['science', 'Science & Mathematics'],
    ['language', 'Languages (Nepali & English)'],
    ['social', 'Social Studies & Arts'],
    ['primary', 'Primary & Early Childhood'],
    ['sports', 'Sports & Physical Education'],
]

notice_category_choices = [
    ['admission', 'Admission Notice'],
    ['exam', 'Examination Notice'],
    ['academic', 'Academic Notice'],
    ['event', 'Event & Activity'],
    ['general', 'General Announcement'],
]

gallery_category_choices = [
    ['school', 'School Campus & Buildings'],
    ['cultural', 'Cultural & Saraswati Puja'],
    ['sports', 'Sports & Physical Education'],
    ['classroom', 'Classroom Learning'],
    ['laboratory', 'Science & Computer Labs'],
    ['events', 'Events & Official Visits'],
    ['tour', 'Educational Tours'],
]


def get_item_by_slug(items: List[Dict], slug: str) -> Optional[Dict]:
    if not slug:
        return None
    return next((item for item in items if item.get('slug') == slug), None)


def filter_by_category(items: List[Dict], category: str) -> List[Dict]:
    if not category:
        return list(items)
    return [item for item in items if item.get('category') == category]


def filter_teachers_by_department(items: List[Dict], department: str) -> List[Dict]:
    if not department:
        return list(items)
    return [item for item in items if item.get('department') == department]
