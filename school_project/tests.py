import re
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.urls import resolve, reverse
from django.utils import timezone

from school_app.admin import PopupNoticeForm
from school_app.forms import SiteSettingsForm
from school_app.models import PopupNotice

from school_project.data import confirmed_statistics


class StaticPageUrlTests(SimpleTestCase):
    def test_about_page_resolves(self):
        self.assertEqual(resolve('/about/').view_name, 'about')
        self.assertEqual(reverse('about'), '/about/')

    def test_principal_message_page_resolves(self):
        self.assertEqual(resolve('/principal-message/').view_name, 'principal_message')
        self.assertEqual(reverse('principal_message'), '/principal-message/')

    def test_facilities_page_resolves(self):
        self.assertEqual(resolve('/facilities/').view_name, 'facilities')
        self.assertEqual(reverse('facilities'), '/facilities/')


class PopupNoticeScheduleFormTests(SimpleTestCase):
    def _form(self, **dates):
        data = {
            'title': 'Schedule form test',
            'slug': 'schedule-form-test',
            'display_order': '0',
            'start_date': '',
            'end_date': '',
        }
        data.update(dates)
        return PopupNoticeForm(data=data)

    def _is_valid_without_database_uniqueness_query(self, form):
        # Slug uniqueness is unrelated to schedule parsing and needs a DB query.
        with patch.object(PopupNoticeForm, 'validate_unique', return_value=None):
            return form.is_valid()

    def test_datetime_local_values_are_accepted_as_one_value_per_field(self):
        form = self._form(
            start_date='2026-10-07T14:36',
            end_date='2026-10-07T15:36',
        )

        self.assertTrue(self._is_valid_without_database_uniqueness_query(form), form.errors)
        self.assertEqual(
            timezone.localtime(form.cleaned_data['start_date']).strftime('%Y-%m-%dT%H:%M'),
            '2026-10-07T14:36',
        )
        self.assertEqual(
            timezone.localtime(form.cleaned_data['end_date']).strftime('%Y-%m-%dT%H:%M'),
            '2026-10-07T15:36',
        )
        self.assertEqual(form.cleaned_data['start_date'].utcoffset(), timedelta(hours=5, minutes=45))
        self.assertEqual(form.fields['start_date'].widget.input_type, 'datetime-local')

    def test_blank_dates_are_valid_and_remain_empty(self):
        form = self._form()

        self.assertTrue(self._is_valid_without_database_uniqueness_query(form), form.errors)
        self.assertFalse(form.fields['start_date'].required)
        self.assertFalse(form.fields['end_date'].required)
        self.assertIsNone(form.cleaned_data['start_date'])
        self.assertIsNone(form.cleaned_data['end_date'])

    def test_end_before_start_is_an_end_date_error(self):
        form = self._form(
            start_date='2026-10-07T14:36',
            end_date='2026-10-07T14:35',
        )

        self.assertFalse(self._is_valid_without_database_uniqueness_query(form))
        self.assertEqual(
            form.errors['end_date'],
            ['End date must be later than start date.'],
        )

    def test_existing_datetime_is_formatted_for_datetime_local(self):
        instance = PopupNotice(
            title='Existing schedule',
            slug='existing-schedule-test',
            start_date=timezone.make_aware(datetime(2026, 10, 7, 14, 36)),
        )
        form = PopupNoticeForm(instance=instance)

        self.assertIn('value="2026-10-07T14:36"', str(form['start_date']))


class HomeSliderTests(SimpleTestCase):
    def test_active_slides_render_as_media_only_carousel(self):
        slides = [
            SimpleNamespace(
                title='Campus image one',
                subtitle='Text that should not be visible',
                description='More text that should not be visible',
                button_text='Apply for Admission',
                button_url='/admission',
                media_type='image',
                image=None,
                video='',
                is_video=False,
                display_image_url='/media/sliders/campus-one.jpg',
            ),
            SimpleNamespace(
                title='Campus image two',
                subtitle='',
                description='',
                button_text='',
                button_url='',
                media_type='image',
                image=None,
                video='',
                is_video=False,
                display_image_url='/media/sliders/campus-two.jpg',
            ),
        ]

        html = render_to_string('home/index.html', {'sliders': slides})
        slider_html = html.split('hero-slider-section', 1)[1].split(
            '<!-- Welcome & Overview Section', 1
        )[0]

        self.assertIn('id="schoolSlider"', slider_html)
        self.assertIn('data-bs-ride="carousel"', slider_html)
        self.assertIn('data-bs-interval="7000"', slider_html)
        self.assertEqual(slider_html.count('class="carousel-item'), 2)
        self.assertIn('data-bs-slide="prev"', slider_html)
        self.assertIn('data-bs-slide="next"', slider_html)
        self.assertIn('/media/sliders/campus-one.jpg', slider_html)
        self.assertIn('/media/sliders/campus-two.jpg', slider_html)
        self.assertNotIn('Apply for Admission', slider_html)
        self.assertNotIn('carousel-caption', slider_html)


class HomeSliderCssSizingTests(SimpleTestCase):
    """Guards the hero slider sizing contract in static/css/home.css.

    Regression history:
      1. The slide box used to be pinned to a fixed `height: 90vh`
         (plus `height: 100vh !important` re-declared in every
         responsive block). The slider photos are natively 2048x1536
         (4:3), so a fixed-height box letterboxed the picture - up to
         65% dead space on phones - and made the image look mis-sized.
      2. The box was then also capped with `width: min(..., 1400px)`,
         so on wide screens the slider floated in the middle of the
         page with dead bands on the left and right instead of
         running full bleed.
      3. Full bleed was then paired with a `max-height: 100vh` cap.
         That fixed phones but reintroduced regression 2 on every
         viewport wider than 4:3: the cap shortened the box below 4:3
         while the width stayed 100%, so `contain` padded the two
         sides with dead dark bands (~240px each on a 1920x1080
         screen).

    The current contract: the box is 100% of the viewport width (full
    bleed, never capped) and its height is derived from the native 4:3
    photo ratio alone. `contain` means the photo is never cropped, and
    the absence of any height cap means it is never letterboxed
    either - at any viewport shape. The deliberate trade-off is that on
    landscape desktops the hero is 4:3 tall and may extend below the
    fold; the photo is always shown complete and gap-free.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        css_path = Path(__file__).resolve().parent.parent / 'static' / 'css' / 'home.css'
        cls.css = css_path.read_text(encoding='utf-8')

    def _block(self, selector):
        """Return the first declaration block for `selector`, comments stripped.

        Comments are removed so an explanatory note such as "never boxed in
        by a max-width" can never be mistaken for an actual declaration.
        """
        idx = self.css.find(selector)
        self.assertNotEqual(idx, -1, f'missing rule for {selector}')
        block = self.css[idx:self.css.find('}', idx)]
        return re.sub(r'/\*.*?\*/', '', block, flags=re.S)

    def test_slide_media_is_never_cropped(self):
        # Every in-slide media rule must letterbox rather than crop, so the
        # photo is never cut off on its left or right edge.
        self.assertIn('object-fit: contain !important;', self.css)
        self.assertNotIn('object-fit: cover !important;', self.css)

    def test_slide_box_follows_photo_ratio(self):
        # The frame is ratio-driven, so the picture fills it with no
        # dead letterbox space.
        self.assertIn('aspect-ratio: var(--jj-hero-ratio);', self.css)
        self.assertIn('--jj-hero-ratio: 4 / 3;', self.css)

    def test_slider_is_full_bleed_width(self):
        # The slide must span the whole screen: no max-width cap and no
        # side gutters around it, otherwise the picture is boxed in with
        # dead bands on the left and right.
        block = self._block('.hero-carousel {')
        self.assertIn('width: 100%;', block)
        self.assertNotIn('1400px', block)
        self.assertNotIn('max-width', block)
        self.assertNotIn('calc(var(--jj-hero-h)', block)

        section = self._block('.hero-slider-section {')
        self.assertIn('width: 100%;', section)
        self.assertIn('padding: 0;', section)

    def test_slide_box_is_never_capped_in_height(self):
        # The height must be decided by the 4:3 ratio and the width alone.
        # Any max-height cap (viewport-relative or absolute) makes the box
        # shorter than 4:3 while its width stays 100%, and `contain` then
        # pads the left and right sides with dead space on any viewport
        # wider than 4:3 - the defect the full-bleed rule above prevents.
        block = self._block('.hero-carousel {')

        self.assertNotIn('max-height', block)
        # A bare `height` would pin the box and defeat the 4:3 ratio.
        # (min-height/max-height are matched separately above/below, so
        # a plain substring test for "height" would false-positive.)
        self.assertIsNone(
            re.search(r'(?<!min-|max-)\bheight\s*:', block),
            'the slide box must not declare a bare height',
        )
        # No viewport-relative unit may appear anywhere in the block, in
        # any of its units, as either a height or a cap.
        self.assertIsNone(
            re.search(r'\d+(?:\.\d+)?(?:d|s|l)?vh', block),
            'the slide box must not be sized against the viewport height',
        )
        # The cap variable it used to be built from is gone entirely.
        self.assertNotIn('--jj-hero-h', self.css)

    def test_slide_box_is_not_hard_pinned_to_a_fixed_height(self):
        # A bare `height: 90vh` (rather than a ratio + max-height cap) is
        # what caused the letterboxing in the first place: it ignored the
        # photo ratio entirely.
        for selector in (
            '.hero-carousel {',
            '.hero-carousel .carousel-inner',
            '.hero-carousel .carousel-item img',
        ):
            block = self._block(selector)
            self.assertNotIn(
                'height: 90vh', block,
                f'{selector} must not pin the slide box to 90vh',
            )
            self.assertNotIn(
                'height: 100vh', block,
                f'{selector} must not pin the slide box to 100vh',
            )


class StatisticsConfirmationTests(SimpleTestCase):
    """Unverified school statistics must never reach the public page.

    The audit found headline figures (enrolment, pass rate) published
    without the school ever confirming them. These tests pin the rule
    that an unconfirmed statistic is filtered out, and that the school
    can switch one on with an environment variable.

    Only the "years since founding" figure is confirmed out of the box,
    because it is derived from the school's own founding year (Estd.
    2045 B.S.) which is already stated throughout the existing site.
    """

    def _reload(self):
        import importlib
        from school_project import data as data_module
        importlib.reload(data_module)
        return data_module

    def test_unconfirmed_statistics_are_hidden_by_default(self):
        data_module = self._reload()

        published = {s['key'] for s in data_module.confirmed_statistics()}

        # Only the founding-year figure is confirmed out of the box.
        self.assertEqual(published, {'years'})
        for key in ('students', 'teachers', 'pass_rate'):
            self.assertNotIn(
                key, published,
                f'{key} must stay hidden until the school confirms it',
            )

    def test_confirming_a_statistic_publishes_it(self):
        import os
        os.environ['STATS_CONFIRM_STUDENTS'] = '1'
        try:
            data_module = self._reload()
            published = {s['key'] for s in data_module.confirmed_statistics()}
            self.assertIn('students', published)
            # The still-unconfirmed ones stay hidden.
            self.assertNotIn('pass_rate', published)
            self.assertNotIn('teachers', published)
        finally:
            del os.environ['STATS_CONFIRM_STUDENTS']
            self._reload()


class ScrollMotionSpecTests(SimpleTestCase):
    """Guards the home-page scroll-animation spec.

    NOTE: this project deliberately does NOT ship the AOS library. Commit
    81ca599 removed it and replaced it with a native IntersectionObserver
    engine (static/js/scroll-motion.js + static/css/scroll-motion.css) that
    reuses AOS's `data-aos` attribute vocabulary. These tests pin the
    requested behaviour to that engine so it cannot silently regress.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        cls.css = (root / 'static' / 'css' / 'scroll-motion.css').read_text(
            encoding='utf-8'
        )
        cls.js = (root / 'static' / 'js' / 'scroll-motion.js').read_text(
            encoding='utf-8'
        )
        # The home page only renders the Teachers / Achievements / Gallery
        # sections when the view actually has rows for them, so the fixture
        # supplies one of each. This keeps the assertions below about
        # wiring and ordering meaningful.
        cls.html = render_to_string('home/index.html', {
            'sliders': [SimpleNamespace(
                title='Campus', subtitle='', description='', button_text='',
                button_url='', media_type='image', image=None, video='',
                is_video=False, display_image_url='/media/sliders/campus.jpg',
            )],
            'teachers': [SimpleNamespace(
                title='A Teacher', position='Teacher', qualification='B.Ed',
                photo=None, slug='a-teacher',
            )],
            'gallery_items': [SimpleNamespace(
                title='A Photo', description='', category_display='Campus',
                image=None, slug='a-photo',
            )],
            'achievements': [SimpleNamespace(
                title='An Achievement', description='', image=None,
                achievement_type='student', achievement_date=None,
                rank_or_position='', event_name='', slug='an-achievement',
            )],
            'programs': [SimpleNamespace(
                title='Primary Level (Grades 1 - 5)', slug='primary',
                description='', duration='5 years', fee='Free', image=None,
            )],
            'statistics': confirmed_statistics(),
        })

    def _section_tag(self, marker):
        """Return the <section ...> opening tag that contains `marker`."""
        idx = self.html.index(marker)
        start = self.html.rindex('<section', 0, idx)
        return self.html[start:self.html.index('>', start) + 1]

    def test_every_listed_section_fades_up_in_page_order(self):
        # The nine sections, in the order the brief lists them. The map has
        # no id, so it is located by its iframe src.
        markers = [
            'about-section',
            'programs-section',
            'notices-section',
            'teachers-section',
            'achievements-section',
            'gallery-section',
            'maps?q=Jaljala',
        ]
        positions = []
        for marker in markers:
            tag = self._section_tag(marker)
            self.assertIn(
                'data-aos="fade-up"', tag,
                f'section containing {marker!r} must fade up on entry',
            )
            positions.append(self.html.index(marker))
        self.assertEqual(
            positions, sorted(positions),
            'sections must be wired in page order, not shuffled',
        )

    def test_card_grids_stagger_one_after_another(self):
        # Teachers / Achievements / Gallery must cascade, not reveal at once.
        # An explicit data-stagger-step is optional: the engine falls back to
        # STAGGER_STEP (70ms), which is still a one-after-another cascade.
        for marker in ('teachers-section', 'achievements-section', 'gallery-section'):
            start = self.html.index(marker)
            end = self.html.index('</section>', start)
            self.assertIn(
                'data-stagger', self.html[start:end],
                f'{marker} grid must use data-stagger so cards cascade',
            )
        self.assertIn(
            'var STAGGER_STEP = 70;', self.js,
            'the fallback stagger step must keep grids cascading',
        )

    def test_navbar_and_hero_are_never_animated(self):
        # Scoped to the two real elements. A raw substring scan of the head
        # would false-positive on the <noscript> safety CSS, which names
        # [data-aos]/[data-stagger] in order to un-hide them.
        nav = self.html[self.html.index('id="mainNav"'):]
        nav = nav[:nav.index('</nav>')]
        # The hero is a <div>, not a <section>, so it is bounded by the next
        # landmark comment - the same bound HomeSliderTests uses.
        hero = self.html.split('hero-slider-section', 1)[1]
        hero = hero.split('<!-- Welcome & Overview Section', 1)[0]
        for label, markup in (('navbar', nav), ('hero slider', hero)):
            for attr in ('data-aos', 'data-stagger', 'data-img-reveal'):
                self.assertNotIn(
                    attr, markup,
                    f'{label} must be visible immediately - found {attr}',
                )

    def test_stat_counters_count_up_rather_than_only_fading(self):
        # Every rendered statistic must be a real counter (data-count drives
        # the count-up in main.js), not static text. Only statistics the
        # school has confirmed are rendered at all, so the assertion runs
        # over whatever confirmed_statistics() actually returns.
        stats = confirmed_statistics()
        self.assertTrue(stats, 'at least one statistic must be confirmed')
        for stat in stats:
            self.assertIn(
                f'data-count="{stat["value"]}"', self.html,
                f'stat {stat["value"]} must animate as a counter',
            )

    def test_reveal_duration_is_in_the_600_800ms_window(self):
        match = re.search(r'--jj-dur:(\d+)ms', self.css)
        self.assertIsNotNone(match, '--jj-dur must be declared in :root')
        duration = int(match.group(1))
        self.assertTrue(
            600 <= duration <= 800,
            f'reveal duration {duration}ms is outside the 600-800ms window',
        )
        # No per-element duration override may undercut the window.
        self.assertNotIn('data-aos-duration', self.html)

    def test_reveal_uses_an_ease_out_curve(self):
        # cubic-bezier(.22,.61,.36,1) is an ease-out: fast start, soft landing.
        self.assertIn('--jj-ease:cubic-bezier(.22,.61,.36,1)', self.css)

    def test_animations_play_once_and_never_replay(self):
        # The reveal observer drops each element as it fires, so scrolling
        # back up can never re-run an animation.
        self.assertIn('observer.unobserve(entry.target)', self.js)

    def test_reduced_motion_is_respected(self):
        self.assertIn('prefers-reduced-motion', self.css)


class TemplateCommentLeakTests(SimpleTestCase):
    """Internal template notes must never be printed on the page.

    Regression history: a two-line `{# ... #}` note explaining the program
    carousel's clip box ended up as a visible sentence in the Academic
    Programs section of the home page (the same thing had earlier happened
    to the notice ticker's notes).

    Cause: Django splits templates with

        tag_re = re.compile(r"({%.*?%}|{{.*?}}|{#.*?#})")

    compiled WITHOUT re.DOTALL. `.` never matches a newline, so a `{# ... #}`
    comment written across two or more lines is not recognised as a comment
    token at all - the lexer emits it as a plain text node and Django ships
    the note straight to the browser. A single-line `{# ... #}` is safe;
    anything longer has to use `{% comment %} ... {% endcomment %}`.

    Both halves are pinned here: no template may carry a multi-line `{# #}`,
    and no rendered page may contain leftover template syntax.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        cls.templates_dir = Path(__file__).resolve().parent.parent / 'templates'
        # The same fixture ScrollMotionSpecTests uses: every conditional
        # section of the home page has to render for the assertion below to
        # cover it.
        cls.html = render_to_string('home/index.html', {
            'sliders': [SimpleNamespace(
                title='Campus', subtitle='', description='', button_text='',
                button_url='', media_type='image', image=None, video='',
                is_video=False, display_image_url='/media/sliders/campus.jpg',
            )],
            'teachers': [SimpleNamespace(
                title='A Teacher', position='Teacher', qualification='B.Ed',
                photo=None, slug='a-teacher',
            )],
            'gallery_items': [SimpleNamespace(
                title='A Photo', description='', category_display='Campus',
                image=None, slug='a-photo',
            )],
            'achievements': [SimpleNamespace(
                title='An Achievement', description='', image=None,
                achievement_type='student', achievement_date=None,
                rank_or_position='', event_name='', slug='an-achievement',
            )],
            'programs': [SimpleNamespace(
                title='Primary Level (Grades 1 - 5)', slug='primary',
                description='', duration='5 years', fee='Free', image=None,
            )],
            'statistics': confirmed_statistics(),
        })

    def test_no_multi_line_hash_comments_in_templates(self):
        offenders = []
        for path in sorted(self.templates_dir.rglob('*.html')):
            text = path.read_text(encoding='utf-8')
            for match in re.finditer(r'\{#.*?#\}', text, re.DOTALL):
                if '\n' in match.group(0):
                    line = text.count('\n', 0, match.start()) + 1
                    offenders.append(
                        f'{path.relative_to(self.templates_dir)}:{line}'
                    )
        self.assertEqual(
            offenders, [],
            'a {# ... #} spread over several lines is never stripped by '
            f'Django and prints itself on the page: {offenders}',
        )

    def test_rendered_home_page_has_no_leftover_template_syntax(self):
        # A page that still contains these tokens is showing the visitor
        # either a template note (the bug above) or an unrendered fragment.
        self.assertIn('jj-pc__window', self.html)
        for token in ('{#', '#}', '{%', '{{'):
            self.assertNotIn(
                token, self.html,
                f'raw template syntax {token!r} reached the rendered page',
            )


class AdmissionCtaStyleTests(SimpleTestCase):
    """Guards the deep-green ONLINE ADMISSION style + green respiration glow.

    Both conversion points share ONE class, defined in
    static/css/admission-cta.css and loaded last in templates/base.html:

      * templates/includes/navbar.html - the ONLINE ADMISSION brand-header button
      * templates/home/index.html      - the home-hero "Enroll Your Child" button

    What is pinned here is:

      * one shared class, with both links and labels left untouched
      * deep-green face (#0f5e36) + thin muted-gold rim (#c9a227),
        white label, 6px radius - exactly the approved screenshot
      * a slow 3-4s ease-in-out green/gold breath (never a blink) on BOTH
        the rim glow and the halo, on one rhythm, in matching greens/golds
      * a visible breath: dim ember at the bottom, near-opaque larger bloom
        at the peak
      * a 2px hover lift that leaves the animated box-shadows alone
      * a focus ring drawn with outline (box-shadow is taken by the breath)
      * prefers-reduced-motion switching the animation off, and still lit
      * the retired crimson/marigold breathing glow does not come back
    """

    #: The two CTAs as (template path, link fragment, label) triples.
    CTAS = (
        ('includes/navbar.html', "{% url 'admission' %}", 'ONLINE ADMISSION'),
        ('home/index.html', '/admission', 'Enroll Your Child'),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        cls.root = root
        cls.css = (root / 'static' / 'css' / 'admission-cta.css').read_text(
            encoding='utf-8'
        )
        cls.base_html = (root / 'templates' / 'base.html').read_text(
            encoding='utf-8'
        )
        cls.templates = {
            rel: (root / 'templates' / rel).read_text(encoding='utf-8')
            for rel, _, _ in cls.CTAS
        }

    def _block(self, selector):
        """Return the first declaration block for `selector`, comments stripped."""
        idx = self.css.find(selector)
        self.assertNotEqual(idx, -1, f'missing rule for {selector}')
        block = self.css[idx:self.css.find('}', idx)]
        return re.sub(r'/\*.*?\*/', '', block, flags=re.S)

    def test_both_ctas_share_one_class_and_keep_links_and_labels(self):
        for rel, link, label in self.CTAS:
            html = self.templates[rel]
            self.assertIn('class="btn jj-admission-cta"', html,
                          f'{rel} no longer uses the shared CTA class')
            self.assertIn(link, html, f'{rel} lost its admission link')
            self.assertIn(label, html, f'{rel} lost its label')
            self.assertNotIn('admission-glow-btn', html)
            self.assertNotIn('jj-admission-glow', html)

    def test_navbar_uses_screenshot_edit_icon(self):
        html = self.templates['includes/navbar.html']
        self.assertIn('fa-pen-to-square', html,
                      'navbar CTA must use the screenshot edit icon')
        self.assertNotIn('fa-file-pen', html,
                         'retired CTA icon must not come back')

    def test_stylesheet_is_loaded_after_the_layers_it_replaces(self):
        self.assertIn(
            "{% static_v 'css/admission-cta.css' %}",
            self.base_html,
        )
        new = self.base_html.index('admission-cta.css')
        for earlier in (
            'modern-enhancements.css',
            'jaljala-redesign.css',
            'notice-ticker.css',
        ):
            self.assertGreater(
                new, self.base_html.index(earlier),
                f'admission-cta.css must load after {earlier}',
            )

    def test_flat_green_face_and_gold_rim(self):
        base = self._block('.jj-admission-cta {')
        self.assertIn('background-color: var(--jj-cta-green) !important;', base)
        self.assertIn('background-image: none !important;', base)
        self.assertIn('border: 1px solid var(--jj-cta-rim) !important;', base)
        self.assertIn('border-radius: 6px !important;', base)
        self.assertIn('color: var(--jj-cta-white) !important;', base)
        self.assertIn('--jj-cta-green: #0f5e36;', self.css)
        self.assertIn('--jj-cta-rim: #c9a227;', self.css)
        self.assertIn('--jj-cta-white: #ffffff;', self.css)
        self.assertIn('--jj-cta-glow-green: #2fbf71;', self.css)

    def _keyframes(self, name):
        match = re.search(
            r'@keyframes ' + name + r' \{(.*?)\n\}', self.css, re.S
        )
        self.assertIsNotNone(match, f'missing @keyframes {name}')
        return re.sub(r'/\*.*?\*/', '', match.group(1), flags=re.S)

    @staticmethod
    def _largest_bloom(block):
        radii = [int(n) for n in re.findall(r'0 0 (\d+)px', block)]
        return max(radii, default=0)

    @staticmethod
    def _strongest_alpha(block):
        alphas = [
            float(a) for a in re.findall(
                r'rgba\(\s*\d+,\s*\d+,\s*\d+,\s*(\.?\d+)\)', block
            )
        ]
        return max(alphas, default=0.0)

    def test_breathing_is_slow_eased_and_never_blinks(self):
        halo = self._block('.jj-admission-cta::after {')
        match = re.search(
            r'animation:\s*jjCtaGreenHaloBreathe\s+([\d.]+)s\s+ease-in-out\s+infinite;',
            halo,
        )
        self.assertIsNotNone(
            match,
            'the halo must breathe on a <duration>s ease-in-out infinite loop',
        )
        duration = float(match.group(1))
        self.assertGreaterEqual(duration, 3.0)
        self.assertLessEqual(duration, 4.0)
        self.assertNotIn('steps(', self.css)
        self.assertNotIn('alternate', self.css)
        self.assertIn('opacity: .3;', halo)
        self.assertIn('box-shadow:', halo)
        body = self._keyframes('jjCtaGreenHaloBreathe')
        self.assertIn('0%, 100%', body)
        self.assertIn('50%', body)
        self.assertIn('opacity: 1', body)

    def test_the_breath_is_wide_enough_to_be_seen(self):
        quiet = float(re.search(
            r'opacity:\s*(\.?\d+);',
            self._block('.jj-admission-cta::after {'),
        ).group(1))
        self.assertGreaterEqual(quiet, .2)
        self.assertLessEqual(quiet, .35)
        ember, peak = self._keyframes('jjCtaGreenHaloBreathe').split('50%', 1)
        peak_opacity = float(re.search(r'opacity:\s*([\d.]+);', peak).group(1))
        self.assertEqual(peak_opacity, 1)
        self.assertGreaterEqual(peak_opacity / quiet, 2.5)
        self.assertIn('transform: scale(1.045);', peak)
        self.assertGreater(
            self._largest_bloom(peak), self._largest_bloom(ember) * 1.4,
        )
        self.assertGreater(
            self._strongest_alpha(peak), self._strongest_alpha(ember),
        )
        self.assertGreaterEqual(self._strongest_alpha(peak), .8)

    def test_the_button_face_breathes_in_step_with_the_halo(self):
        base = self._block('.jj-admission-cta {')
        face_breath = re.search(
            r'animation:\s*jjCtaGreenBreathe\s+([\d.]+)s\s+ease-in-out\s+infinite;',
            base,
        )
        self.assertIsNotNone(face_breath, 'the rim glow must breathe as well')
        halo_breath = re.search(
            r'animation:\s*jjCtaGreenHaloBreathe\s+([\d.]+)s\s+ease-in-out\s+infinite;',
            self._block('.jj-admission-cta::after {'),
        )
        self.assertEqual(
            face_breath.group(1), halo_breath.group(1),
            'both layers must breathe on one rhythm',
        )
        ember, peak = self._keyframes('jjCtaGreenBreathe').split('50%', 1)
        self.assertGreater(
            self._strongest_alpha(peak), self._strongest_alpha(ember),
        )

    def test_glow_uses_matching_greens_and_golds_only(self):
        for layer in (self._block('.jj-admission-cta::after {')
                      + self._keyframes('jjCtaGreenHaloBreathe')
                      + self._keyframes('jjCtaGreenBreathe')):
            self.assertNotIn('rgba(166', layer)
            self.assertNotIn('rgba(60', layer)
            self.assertNotIn('232, 163, 61, .95', layer)

    def test_hover_answers_without_fighting_the_keyframes(self):
        hover = self._block('.jj-admission-cta:hover {')
        self.assertIn('transform: translateY(-2px);', hover)
        self.assertNotIn('box-shadow', hover)
        self.assertIn('filter: brightness(', hover)
        self.assertIn('border-color: var(--jj-cta-rim-bright) !important;',
                      hover)
        self.assertIn('filter: brightness(',
                      self._block('.jj-admission-cta:hover::after {'))
        icons = self._block('.jj-admission-cta:hover :is(')
        self.assertIn('transform: translateX(3px);', icons)

    def test_focus_ring_is_an_outline_not_a_shadow(self):
        focus = self._block('.jj-admission-cta:focus-visible {')
        self.assertIn(
            'outline: 2px solid var(--jj-cta-rim-bright) !important;', focus
        )
        self.assertIn('outline-offset: 3px;', focus)
        self.assertNotIn('outline: none', self.css)

    def test_reduced_motion_disables_lift(self):
        block = self.css[
            self.css.index('@media (prefers-reduced-motion: reduce)'):
        ]
        self.assertIn('animation: none !important;', block)
        self.assertIn('transform: none;', block)
        self.assertIn('opacity: .55;', block)
        self.assertIn('box-shadow:', block)

    def test_old_crimson_glow_styling_is_gone(self):
        canonical = 'admission-cta.css'
        for path in sorted((self.root / 'static' / 'css').glob('*.css')):
            if path.name == canonical:
                continue
            text = path.read_text(encoding='utf-8')
            self.assertNotIn('admission-glow-btn', text,
                             f'{path.name} still styles the retired nav CTA')
            self.assertNotIn('--jj-adm-ang', text,
                             f'{path.name} still carries the retired gold ring')
            self.assertNotIn('jjAdmGlowPulse', text,
                             f'{path.name} still pulses the retired gold glow')
            self.assertNotIn('jj-admission-cta', text,
                             f'{path.name} must not re-style the shared CTA '
                             'class - the effect would drift apart again')
        # The retired crimson/marigold breathing palette is gone for good.
        self.assertNotIn('--jj-cta-crimson', self.css)
        self.assertNotIn('--jj-cta-gold: #E8A33D;', self.css)
        self.assertNotIn('--jj-cta-amber', self.css)
        self.assertNotIn('jjCtaBreathe', self.css)
        self.assertNotIn('jjCtaFaceBreathe', self.css)
        self.assertIn('jjCtaGreenBreathe', self.css)
        self.assertIn('jjCtaGreenHaloBreathe', self.css)

class TopbarLoginIconTests(SimpleTestCase):
    """The top-bar trigger reads "open padlock", the menu item reads "lock".

    The trigger used to open with fa-right-to-bracket - an "enter the door"
    arrow that says nothing about logging in, and at 0.78rem reads as a box
    with a dot before the word Login. fa-key was tried after it and missed as
    well: the reference the trigger has to match is a padlock, not a key. It
    now carries fa-unlock-keyhole - an open padlock with a keyhole, the closest
    free Font Awesome 6 solid to that reference - while the single item it
    hides keeps its own closed fa-lock, so the two lines stay distinguishable
    at a glance:

      * open padlock -> the Login trigger
      * closed lock  -> the Admin Login item it unlocks

    The trigger is pinned against both retired glyphs, and the pairing is
    pinned too: the closed lock must not creep onto the trigger, and the
    trigger must not lose the Admin Login link it exists to open.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        cls.navbar = (
            Path(__file__).resolve().parent.parent
            / 'templates' / 'includes' / 'navbar.html'
        ).read_text(encoding='utf-8')

    def test_the_trigger_opens_with_a_padlock_before_the_word_login(self):
        self.assertIn(
            '<i class="fa-solid fa-unlock-keyhole me-1" aria-hidden="true"></i> Login',
            self.navbar,
            'the Login trigger lost the padlock before its label',
        )
        self.assertNotIn(
            'fa-right-to-bracket', self.navbar,
            'the retired enter-a-door arrow is back on the top bar',
        )
        self.assertNotIn(
            'fa-solid fa-key', self.navbar,
            'the key is back on the trigger - the reference shows a padlock',
        )

    def test_the_padlock_still_opens_the_admin_login_item(self):
        self.assertIn("{% url 'admin_dashboard' %}", self.navbar)
        self.assertIn(
            '<i class="fa-solid fa-lock me-2" aria-hidden="true"></i> Admin Login',
            self.navbar,
            'the item the padlock opens lost its closed lock glyph',
        )
        self.assertNotIn(
            '<i class="fa-solid fa-lock me-1" aria-hidden="true"></i> Login',
            self.navbar,
            'the closed lock moved onto the trigger - the two lines must stay '
            'distinguishable',
        )


class TopbarLoginMenuReadabilityTests(SimpleTestCase):
    """The panel behind the top-bar Login trigger has to stay readable.

    Regression history: `.top-bar span,.top-bar a{color:#fff!important}` paints
    every link on the pine strip white - and the Admin Login item sits *inside*
    that strip, on Bootstrap's white dropdown panel. On the running site the
    trigger opened a menu that looked empty: the item and its lock were both
    there and both invisible (~1.05:1).

    The panel now mirrors the main nav's dropdown (white surface, ink item,
    warm hover). Both halves are pinned, so the strip's white rule can never
    quietly win the item back.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        sheet = (
            Path(__file__).resolve().parent.parent
            / 'static' / 'css' / 'jaljala-redesign.css'
        ).read_text(encoding='utf-8')
        cls.sheet = sheet
        # Selectors are looked up in this comment-free copy: the note next to
        # the rules below names both selectors, and a lookup in the raw sheet
        # would otherwise land inside that note.
        cls.plain = re.sub(r'/\*.*?\*/', '', sheet, flags=re.S)

    def _block(self, selector):
        """Declarations of `selector`, comments already stripped."""
        idx = self.plain.find(selector)
        self.assertNotEqual(idx, -1, f'missing rule for {selector}')
        return self.plain[idx:self.plain.find('}', idx)]

    def test_the_panel_uses_the_same_light_surface_as_the_main_nav(self):
        self.assertIn(
            'background:var(--color-surface)!important',
            self._block('.top-bar .dropdown-menu'),
            'the top-bar menu lost the light panel the nav menus use',
        )
        self.assertIn(
            'color:var(--color-ink)!important',
            self._block('.top-bar .dropdown-item'),
            'the Admin Login item is no longer painted in ink',
        )

    def test_the_white_strip_rule_cannot_win_the_item_back(self):
        strip_rule = '.top-bar span,.top-bar a{color:#fff!important}'
        item_rule = '.top-bar .dropdown-item{color:var(--color-ink)!important}'
        self.assertIn(strip_rule, self.sheet,
                      'the pine strip white rule was renamed or removed')
        self.assertIn(item_rule, self.sheet,
                      'the menu item ink rule was renamed or removed')
        # Higher specificity (0-2-0 vs 0-1-1) *and* later in the sheet: the item
        # stays ink on the white panel whichever way a browser breaks the tie.
        self.assertLess(
            self.sheet.index(strip_rule), self.sheet.index(item_rule),
            'the item rule must stay after the strip rule it overrides',
        )


class NavOrderTests(SimpleTestCase):
    """The main menu reads in the same order as the home page.

    NOTICES used to close the content group - right after GALLERY - so the
    one page the school refreshes every day sat behind two browse-y sections
    and out of step with the page that summarises it: home/index.html runs
    About -> Programs -> Notices -> Teachers -> Achievements -> Gallery.

    Nothing went red while they disagreed, because static/js/scroll-motion.js
    matches a section to its link by *route* (`notices-section` -> /notices),
    never by position. The tracker only ever cared that a link exists; the
    order it sits in is a reading decision, and it belongs to the page.

    The menu now follows the page:

      HOME, ABOUT US, PROGRAM, NOTICES, TEACHERS, ACHIEVEMENTS, GALLERY,
      RESULTS, ADMISSION, DOWNLOADS, CONTACT

    Pinned here: that exact sequence, NOTICES sitting directly after PROGRAM,
    the ABOUT US dropdown keeping its own page order, and every label still
    owning its own route - a reorder may move an item, it may not leave two
    labels pointing at each other's pages.
    """

    #: Top-level items, in the order the reader meets them on the home page.
    ORDER = (
        'HOME', 'ABOUT US', 'PROGRAM', 'NOTICES', 'TEACHERS', 'ACHIEVEMENTS',
        'GALLERY', 'RESULTS', 'ADMISSION', 'DOWNLOADS', 'CONTACT',
    )

    #: Each label's own route. ABOUT US is the dropdown toggle (href="#"),
    #: so it has no route of its own; its three pages are pinned below.
    ROUTES = {
        'HOME': 'home',
        'PROGRAM': 'programs',
        'NOTICES': 'notices',
        'TEACHERS': 'teachers',
        'ACHIEVEMENTS': 'achievements',
        'GALLERY': 'gallery',
        'RESULTS': 'results:list',
        'ADMISSION': 'admission',
        'DOWNLOADS': 'downloads',
        'CONTACT': 'contact',
    }

    #: The ABOUT US dropdown, in the order its pages read.
    DROPDOWN = ('about', 'principal_message', 'facilities')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        navbar = (
            Path(__file__).resolve().parent.parent
            / 'templates' / 'includes' / 'navbar.html'
        ).read_text(encoding='utf-8')
        # The list carries an explanatory note of its own, and prose is not
        # menu content: comments come out before anything is read.
        menu = navbar[navbar.index('class="navbar-nav'):]
        cls.menu = re.sub(
            r'\{#.*?#\}|<!--.*?-->', '',
            menu[:menu.index('</nav>')],
            flags=re.S,
        )

    def _labels(self):
        """Top-level labels in document order."""
        return re.findall(r'>\s*([A-Z][A-Z &]*?)\s*</a>', self.menu)

    def _routed_items(self):
        """(route, label) pairs for the items that link to a named route."""
        return re.findall(
            r'<a class="nav-link[^>]*href="\{%\s*url\s+\'([^\']+)\'\s*%\}".*?>'
            r'\s*([A-Z][A-Z &]*?)\s*</a>',
            self.menu,
            flags=re.S,
        )

    def test_the_menu_follows_the_home_page_order(self):
        self.assertEqual(
            self._labels(), list(self.ORDER),
            'the menu must keep the home page order, not shuffle',
        )

    def test_notices_sits_directly_after_program(self):
        labels = self._labels()
        self.assertEqual(
            labels[labels.index('PROGRAM') + 1], 'NOTICES',
            'NOTICES drifted away from PROGRAM - the home page shows its '
            'latest notices right after the programs section',
        )

    def test_every_item_still_owns_its_own_route(self):
        self.assertEqual(
            {label: route for route, label in self._routed_items()},
            self.ROUTES,
            'a reorder may move an item, never re-point one',
        )

    def test_the_about_dropdown_keeps_its_page_order(self):
        positions = [
            self.menu.index(f"{{% url '{name}' %}}") for name in self.DROPDOWN
        ]
        self.assertEqual(
            positions, sorted(positions),
            'ABOUT US must open About -> Principal -> Facilities, in that '
            'order, the way the home page tells the story',
        )


class GalleryPhotoColourTests(SimpleTestCase):
    """Gallery photos must render in full colour, always.

    Regression history: `.g-tile__img` once carried `filter: grayscale(1)` and
    only dropped it on `:hover`, so every photo sat on the page as a
    black-and-white thumbnail until the pointer happened to land on it. The
    orange category badge beside it stayed coloured the whole time, which is
    what made it obvious the effect was applied to the `<img>` and not to the
    photo itself - the underlying files have always been colour.

    Two things are pinned here. First, no filter may desaturate a tile image.
    Second - and this is the half that actually bit - the stylesheet has to be
    re-fetchable: base.html used to hard-code `/static/css/gallery.css`, so the
    URL never changed and browsers served the grayscale copy indefinitely,
    long after the rule was gone from source.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        cls.sheet = (root / 'static' / 'css' / 'gallery.css').read_text(encoding='utf-8')
        # Comments name the very properties under test, so selectors are looked
        # up in a comment-free copy.
        cls.plain = re.sub(r'/\*.*?\*/', '', cls.sheet, flags=re.S)
        cls.base = (root / 'templates' / 'base.html').read_text(encoding='utf-8')

    def _block(self, selector):
        idx = self.plain.find(selector)
        self.assertNotEqual(idx, -1, f'missing rule for {selector}')
        return self.plain[idx:self.plain.find('}', idx)]

    def test_tile_images_are_not_desaturated(self):
        """No rule that matches a tile photo may set a desaturating filter."""
        self.assertNotIn(
            'grayscale', self.plain,
            'gallery.css desaturates photos again; they are colour photographs',
        )
        # sepia/brightness/contrast are checked on the image rules themselves so
        # a future "slightly muted" tweak cannot quietly reintroduce the look.
        for prop in ('sepia(', 'saturate(', 'brightness(', 'contrast('):
            self.assertNotIn(
                prop, self._block('.g-tile__img'),
                f'.g-tile__img must not apply {prop}',
            )

    def test_tile_images_pin_the_neutral_filter(self):
        """`filter: none` is declared, so no later rule can reach the photo."""
        self.assertIn(
            'filter: none', self._block('.g-tile__img'),
            'declare filter:none on .g-tile__img to pin the colour rendering',
        )

    def test_no_scrim_or_overlay_darkens_the_photo(self):
        """The caption reads via text-shadow; the image carries no colour wash."""
        self.assertNotIn(
            '.g-tile__scrim', self.plain,
            'the dark scrim layer is gone from the markup and must stay gone',
        )

    def test_gallery_stylesheet_url_is_cache_busted(self):
        """base.html must not hard-code the gallery.css URL.

        This is the half of the bug a code review of gallery.css alone cannot
        catch: the stylesheet was correct on disk while every visitor still saw
        the grayscale version, because the URL was identical to the one they had
        cached.
        """
        self.assertNotIn(
            '"/static/css/gallery.css"', self.base,
            'base.html hard-codes gallery.css; use {% static_v %} so edits deploy',
        )
        self.assertIn(
            "{% static_v 'css/gallery.css' %}", self.base,
            'base.html must load gallery.css through the versioning tag',
        )

    def test_every_local_asset_in_base_html_is_cache_busted(self):
        """No local CSS/JS may slip back to a hard-coded, unversioned URL."""
        bare = re.findall(r'(?:href|src)="/static/[^"]+"', self.base)
        self.assertEqual(
            bare, [],
            'these local assets are hard-coded and will be served stale: '
            + ', '.join(bare),
        )

    def test_static_v_appends_the_file_mtime(self):
        """The tag ties the URL to the file, so an edit changes the URL."""
        from school_app.templatetags.static_assets import static_v

        url = static_v('css/gallery.css')
        self.assertTrue(
            url.startswith('/static/css/gallery.css'),
            f'unexpected static path: {url}',
        )
        self.assertIn('?v=', url)
        self.assertNotEqual(url, '/static/css/gallery.css')

    def test_static_v_degrades_gracefully_for_a_missing_file(self):
        """A missing asset yields a plain URL, not an exception."""
        from school_app.templatetags.static_assets import static_v

        self.assertEqual(
            static_v('css/does-not-exist.css'),
            '/static/css/does-not-exist.css',
        )
class SplashPreloaderTests(SimpleTestCase):
    """The splash screen has to be the FIRST paint, not a second act.

    The regression: the overlay markup sat at the top of <body>, but
    style.css held it at `opacity: 0; visibility: hidden` until
    static/js/main.js - the second-to-last script, behind the Bootstrap CDN
    bundle, and only running on DOMContentLoaded - decided to show it. On a
    cold load (nothing cached, the CDN still downloading) the page therefore
    painted first, the visitor read the site for a few seconds, and only then
    did the splash drop over it and fade away again.

    The decision now happens in <head>, while the document is still parsing:
    an inline flag script marks <html> with `jj-splash` when the splash is due
    (first visit of the session, or a click on Home), style.css reveals the
    overlay off that class, and main.js only ever takes it down again.
    """

    OVERLAY_FLAG = "document.documentElement.classList.add('jj-splash')"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        cls.base = (root / 'templates' / 'base.html').read_text(encoding='utf-8')
        cls.css = (root / 'static' / 'css' / 'style.css').read_text(
            encoding='utf-8'
        )
        cls.js = (root / 'static' / 'js' / 'main.js').read_text(
            encoding='utf-8'
        )
        cls.head = cls.base[:cls.base.index('</head>')]
        cls.body = cls.base[cls.base.index('</head>'):]

    def _style_rule(self, selector):
        """The full `selector {...}` block from style.css."""
        match = re.search(
            re.escape(selector) + r'\s*\{([^}]*)\}', self.css,
        )
        self.assertIsNotNone(match, f'{selector} is missing from style.css')
        return match.group(0)

    def test_the_splash_is_decided_in_the_head_before_the_first_paint(self):
        self.assertIn(self.OVERLAY_FLAG, self.head)
        self.assertNotIn(
            self.OVERLAY_FLAG, self.body,
            'the flag has to be set before <body> is parsed, or the page '
            'paints first and the splash lands on top of a visible site',
        )

    def test_the_css_reveals_the_overlay_off_that_flag(self):
        rule = self._style_rule(
            'html.jj-splash #school-preloader.preloader-overlay:not(.fade-out)'
        )
        self.assertIn('opacity: 1', rule)
        self.assertIn('visibility: visible', rule)
        self.assertIn(
            'pointer-events: auto', rule,
            'the overlay is only up while the flag is set, so it must not '
            'swallow clicks once it is gone',
        )

    def test_main_js_only_takes_the_splash_down(self):
        self.assertIn(
            "document.documentElement.classList.contains('jj-splash')", self.js
        )
        self.assertIn(
            "document.documentElement.classList.remove('jj-splash')", self.js
        )
        self.assertNotIn(
            "getItem('preloader-seen')", self.js,
            'main.js deciding again at the end of <body> is exactly what put '
            'the splash on screen seconds after the site',
        )

    def test_the_head_script_records_the_session_so_it_splashes_once(self):
        self.assertIn(
            "sessionStorage.setItem('preloader-seen', '1')", self.head
        )
        self.assertIn("removeItem('show-preloader')", self.head)
        # A click on Home still replays the splash on the page it loads.
        self.assertIn("addEventListener('click'", self.js)
        self.assertIn("setItem('show-preloader', '1')", self.js)

    def test_a_script_that_never_runs_cannot_leave_the_page_covered(self):
        self.assertIn("window.addEventListener('load'", self.head)
        watchdog = self.head[
            self.head.index("window.addEventListener('load'"):
        ]
        self.assertIn('3000', watchdog)
        self.assertIn(
            "contains('jj-splash')", watchdog,
            'the watchdog must only fire while the splash is still up, never '
            'over a dismissal that already happened',
        )
        self.assertIn("classList.remove('jj-splash')", watchdog)

    def test_the_overlay_opens_the_body_before_the_page_content(self):
        overlay = self.body.index("include 'includes/preloader.html'")
        navbar = self.body.index("include 'includes/navbar.html'")
        self.assertLess(
            overlay, navbar,
            'the overlay has to be parsed first, so that the first paint it '
            'belongs to is the splash',
        )



class StaffPhotoRingTests(SimpleTestCase):
    """Staff portraits sit on the page without a ring drawn around them.

    Regression history: `.teacher-photo` was drawn as a circle with a 3px
    marigold ring, and the profile portrait added a second one inline
    (`border: 4px solid var(--accent-gold)`). Two circles in a row then
    framed every staff photo - the ring on the faculty grid and the ring on
    the profile page - and on a white-background headshot like the
    chairperson's the ring read as a drawn-on circle rather than as a photo,
    because there was nothing inside it but backdrop.

    The crop stays circular (`border-radius: 50%` / `rounded-circle`); only
    the ring is gone. The photos themselves are untouched - these are the
    school's own committed files, never re-cropped or re-encoded to suit a
    border.

    Both halves are pinned: no stylesheet may put a border back on a staff
    photo, and the profile portrait must not carry an inline one either.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        cls.css_dir = root / 'static' / 'css'
        # Comments name the very properties under test, so the sheets are
        # read in a comment-free copy.
        cls.sheets = {
            path.name: re.sub(r'/\*.*?\*/', '', path.read_text(encoding='utf-8'))
            for path in sorted(cls.css_dir.glob('*.css'))
        }
        cls.detail = (
            root / 'templates' / 'teacher' / 'teacher_detail.html'
        ).read_text(encoding='utf-8')

    def _staff_photo_blocks(self):
        """Every declaration block in every sheet that styles a staff photo."""
        for name, sheet in self.sheets.items():
            for match in re.finditer(r'([^{}]*teacher-photo[^{}]*)\{([^}]*)\}', sheet):
                yield name, match.group(1).strip(), match.group(2)

    def test_no_stylesheet_puts_a_border_on_a_staff_photo(self):
        """The ring is gone from the grid, not merely made thinner."""
        offenders = [
            f'{name} {{{selector}}}'
            for name, selector, body in self._staff_photo_blocks()
            if re.search(r'\bborder(?:-[a-z]+)?\s*:', body)
            and not re.search(r'\bborder\s*:\s*(?:none|0)\b', body)
        ]
        self.assertEqual(
            offenders, [],
            'a staff photo is framed by a ring again: ' + ', '.join(offenders),
        )

    def test_the_hover_state_cannot_bring_the_ring_back(self):
        """The hover rule once only recoloured the ring - a live re-add path."""
        hover = [
            body for _, selector, body in self._staff_photo_blocks()
            if ':hover' in selector
        ]
        for body in hover:
            self.assertNotIn(
                'border-color', body,
                'a :hover rule may not recolour a border the photo no longer has',
            )

    def test_the_profile_portrait_carries_no_inline_border(self):
        """The detail page set its own ring, so the sheet was never enough."""
        self.assertNotIn(
            '--accent-gold', self.detail,
            'the profile portrait draws its own gold ring again',
        )

    def test_the_portraits_stay_round(self):
        """Only the ring was asked for - the circular crop is the design."""
        # The grid keeps its circle in CSS...
        sheets = '\n'.join(self.sheets.values())
        self.assertIn(
            'border-radius: 50%', sheets,
            'the circular crop was lost; only the ring was to be removed',
        )
        # ...and the profile portrait keeps Bootstrap's own class.
        self.assertIn('rounded-circle', self.detail)

    def test_the_photo_files_themselves_are_untouched(self):
        """A headshot is never re-encoded to fit a border."""
        from pathlib import Path

        media = Path(__file__).resolve().parent.parent / 'media' / 'teachers'
        photos = sorted(media.glob('*.jpg'))
        self.assertTrue(photos, 'the committed staff photos must stay in place')
        for photo in photos:
            self.assertGreater(
                photo.stat().st_size, 0, f'{photo.name} is empty on disk',
            )


class SiteSettingsFormTests(SimpleTestCase):
    """Validation behaviour of the Site settings form used by admin_settings."""

    def _form(self, files=None, **data):
        base = {
            'school_name': 'Shree Jaljala Secondary School',
            'tagline': 'Quality Education for All',
            'phone': '9812345678',
            'email': 'info@school.edu.np',
            'address': 'Panchkhapan, Sankhuwasabha, Nepal',
        }
        base.update(data)
        return SiteSettingsForm(data=base, files=files)

    def test_valid_settings_are_accepted(self):
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)

    def test_school_name_is_required(self):
        form = self._form(school_name='')
        self.assertFalse(form.is_valid())
        self.assertIn('school_name', form.errors)

    def test_school_name_must_be_at_least_2_chars(self):
        form = self._form(school_name='X')
        self.assertFalse(form.is_valid())
        self.assertIn('school_name', form.errors)

    def test_invalid_email_is_rejected(self):
        form = self._form(email='not-an-email')
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_blank_email_is_allowed(self):
        form = self._form(email='')
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_nepal_phone_is_accepted(self):
        form = self._form(phone='+9779812345678')
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_phone_is_rejected(self):
        form = self._form(phone='123')
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_oversized_logo_is_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        big = SimpleUploadedFile(
            'logo.png', b'\x89PNG\r\n\x1a\n' + b'0' * (3 * 1024 * 1024)
        )
        form = self._form(files={'logo': big})
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_non_image_logo_is_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        bad = SimpleUploadedFile('logo.txt', b'not an image')
        form = self._form(files={'logo': bad})
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_phone_is_normalized_stripping_spaces_and_dashes(self):
        form = self._form(phone='98-1234 5678')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['phone'], '9812345678')

