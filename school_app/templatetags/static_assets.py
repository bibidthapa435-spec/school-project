import os

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def static_v(path):
    """Return the URL for a static file, versioned by that file's mtime.

    Why this tag exists
    --------------------
    `templates/base.html` used to link its stylesheets and scripts with
    hard-coded strings - `href="/static/css/gallery.css"`. Those URLs never
    change when the file behind them does, so browsers (and WhiteNoise) are
    free to keep serving a stale copy indefinitely.

    That is not hypothetical. An earlier `gallery.css` desaturated every photo
    with `filter: grayscale(1)` and only restored colour on hover. The rule was
    deleted from source, but visitors kept seeing black-and-white photos for as
    long as their cache held the old file, because the URL - and therefore the
    cache key - was identical.

    Appending `?v=<mtime>` ties the URL to the file's contents: edit the CSS and
    the URL changes, so the next page load is guaranteed to fetch the new file.
    The path stays plain and readable, which also keeps the dev server and
    WhiteNoise serving the same URL in both DEBUG and production.

    If the file cannot be found we fall back to the unhashed URL rather than
    raising, so a missing asset degrades to a 404 instead of a 500.
    """
    url = static(path)

    # Already versioned by the storage backend (e.g. ManifestStaticFilesStorage
    # appends a content hash in production) - nothing left to add.
    absolute = finders.find(path)
    if not absolute:
        return url

    try:
        stamp = int(os.path.getmtime(absolute))
    except OSError:
        return url

    # Preserve any existing query string on the storage-generated URL.
    joiner = '&' if '?' in url else '?'
    return '%s%sv=%d' % (url, joiner, stamp)