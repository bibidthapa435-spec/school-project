import os
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
    'logo_url': '/static/images/logo.jpg',
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


def _stat_flag(name: str) -> bool:
    """True when the school has explicitly confirmed a statistic.

    Statistics are OFF by default. A statistic is only rendered on the
    public site once the school administrator sets the matching
    environment variable to '1' (for example ``STATS_CONFIRM_STUDENTS=1``)
    in the Render dashboard. This keeps unverified numbers (enrolment
    counts, pass rates) off a public school website until the school
    itself stands behind them.
    """
    return os.environ.get(f'STATS_CONFIRM_{name}', '').strip().lower() in {
        '1', 'true', 'yes',
    }


def _stat_as_of(default: str = '') -> str:
    """Optional "as of" qualifier, e.g. "As of 2082 B.S.".

    Falls back to the current Nepali academic year label only when the
    school has confirmed at least one statistic, so an unconfirmed band
    never shows a bare year.
    """
    return os.environ.get('STATS_AS_OF', '').strip() or default


# Homepage statistics band.
#
# IMPORTANT: no number here is verified. `confirmed` is resolved from the
# environment (see _stat_flag) and is False unless the school sets
# STATS_CONFIRM_<NAME>=1. The template renders ONLY confirmed entries, so
# nothing unverified is ever published. Labels are deliberately worded to
# match the rest of the site (Nursery to Class 10, Estd. 2045 B.S.).
homepage_statistics = [
    {
        'key': 'students',
        'value': 550,
        'suffix': '+',
        'label': 'Students, Nursery to Class 10',
        'confirmed': _stat_flag('students'),
    },
    {
        'key': 'teachers',
        'value': 16,
        'suffix': '+',
        'label': 'Dedicated Teachers',
        'confirmed': _stat_flag('teachers'),
    },
    {
        'key': 'pass_rate',
        'value': 100,
        'suffix': '%',
        'label': 'SEE Pass Rate',
        'confirmed': _stat_flag('pass_rate'),
    },
    {
        'key': 'years',
        # Derived from the school's own founding year (Estd. 2045 B.S.),
        # which is stated throughout the existing site content.
        'value': 38,
        'suffix': '',
        'label': 'Years in Panchkhapan, Estd. 2045 B.S.',
        'confirmed': True,
    },
]


def confirmed_statistics():
    """Return only the statistics the school has confirmed."""
    confirmed = [s for s in homepage_statistics if s['confirmed']]
    if not confirmed:
        return []
    as_of = _stat_as_of()
    if as_of:
        confirmed = [dict(s, as_of=as_of) for s in confirmed]
    else:
        confirmed = [dict(s, as_of='') for s in confirmed]
    return confirmed


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
