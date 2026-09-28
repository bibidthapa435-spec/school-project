import re
from types import SimpleNamespace

from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.urls import resolve, reverse

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
