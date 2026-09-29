"""Template helpers for the Latest Notices ticker.

WHY THIS EXISTS
---------------
The ticker needs an "effective" notice list: the notices the view
passed, or - when that is empty - the site's fallback ticker
notices (the same list the old `MARQUEE_NOTICES` context key
carried).

That fallback used to be written inline as::

    {% with ticker_items=notices|default:MARQUEE_NOTICES %}

which is a latent crash. Django resolves EVERY filter argument
eagerly, and `{% with %}` does not tolerate a missing variable
(only `{% for %}` passes ``ignore_failures=True``). So any render
that supplies ``notices`` but omits ``MARQUEE_NOTICES`` - a unit
test, a partial context, a future caller - dies with
``VariableDoesNotExist`` even though ``notices`` was perfectly
usable and the default would never have been needed.

``ticker_items`` takes no template argument at all: it fetches the
fallback itself, so it cannot raise.
"""
from django import template

from school_app.models import Notice

register = template.Library()

#: Mirrors the fallback the old MARQUEE_NOTICES context key used.
FALLBACK_LIMIT = 5


@register.filter
def ticker_items(value):
    """Return `value` when it has items, else the fallback notices.

    Accepts a queryset, list, tuple or None. Never raises: an empty or
    missing value falls back to the latest active notices (at most
    FALLBACK_LIMIT items), and even a failing fallback query returns []
    so the ticker renders its empty state instead of 500ing.
    """
    try:
        items = list(value) if value else []
    except TypeError:
        items = []
    if items:
        return items[:10]
    try:
        return list(
            Notice.objects.filter(status=True).order_by(
                'display_order', '-created_at'
            )[:FALLBACK_LIMIT]
        )
    except Exception:
        return []
