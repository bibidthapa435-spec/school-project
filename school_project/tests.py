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


class AdmissionCtaGlowTests(SimpleTestCase):
    """Guards the "respiration" glow on the two admission CTAs.

    Both conversion points share ONE class, defined in
    static/css/admission-cta.css and loaded last in templates/base.html:

      * templates/includes/navbar.html - the ONLINE ADMISSION brand-header button
      * templates/home/index.html      - the home-hero "Enroll Your Child" button

    History: each button used to carry its own copy of a maroon/marigold
    conic ring (1.8s and 2.4s linear sweeps, declared twice - in
    modern-enhancements.css and jaljala-redesign.css), which read as a flash
    rather than a breath. Those copies were replaced by one shared treatment
    in the school's own palette - a pine face, a marigold rim, a marigold
    halo over a rhododendron under-glow - so what is pinned here is:

      * one shared class, with both links and labels left untouched
      * the site's own colour tokens, not an outside colour scheme
      * a 3-4s ease-in-out breath (never a blink: no steps(), no alternate,
        no sub-second duration) on BOTH the rim glow and the halo, on one beat
      * an amplitude wide enough to be seen: a sub-.35 ember at the bottom of
        the breath and a near-opaque peak whose bloom is clearly larger - the
        "I can barely see the glow" bug is what these two pins catch
      * a 2px hover lift that leaves the animated box-shadows alone
      * a focus ring drawn with outline (box-shadow is taken by the breath)
      * prefers-reduced-motion switching the animation off, and still lit
      * the old maroon/gold CTA selectors and the discarded navy/cyan palette
        not coming back
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
        """Return the first declaration block for `selector`, comments stripped.

        Comments are removed so an explanatory note can never be mistaken for
        an actual declaration.
        """
        idx = self.css.find(selector)
        self.assertNotEqual(idx, -1, f'missing rule for {selector}')
        block = self.css[idx:self.css.find('}', idx)]
        return re.sub(r'/\*.*?\*/', '', block, flags=re.S)

    def _keyframes(self, name):
        """Body of the `@keyframes <name>` block, comments stripped."""
        match = re.search(
            r'@keyframes ' + name + r' \{(.*?)\n\}', self.css, re.S
        )
        self.assertIsNotNone(match, f'missing @keyframes {name}')
        return re.sub(r'/\*.*?\*/', '', match.group(1), flags=re.S)

    @staticmethod
    def _largest_bloom(block):
        """Widest `0 0 <blur>px` radius declared in a block of declarations."""
        radii = [int(n) for n in re.findall(r'0 0 (\d+)px', block)]
        return max(radii, default=0)

    @staticmethod
    def _strongest_alpha(block):
        """Highest rgba() alpha declared in a block of declarations."""
        alphas = [
            float(a) for a in re.findall(
                r'rgba\(\s*\d+,\s*\d+,\s*\d+,\s*(\.?\d+)\)', block
            )
        ]
        return max(alphas, default=0.0)

    def test_both_ctas_share_one_class_and_keep_links_and_labels(self):
        for rel, link, label in self.CTAS:
            html = self.templates[rel]
            self.assertIn('class="btn jj-admission-cta"', html,
                          f'{rel} no longer uses the shared CTA class')
            self.assertIn(link, html, f'{rel} lost its admission link')
            self.assertIn(label, html, f'{rel} lost its label')
            # Two per-button variants would let the effect drift apart again.
            self.assertNotIn('admission-glow-btn', html)
            self.assertNotIn('jj-admission-glow', html)

    def test_stylesheet_is_loaded_after_the_layers_it_replaces(self):
        self.assertIn(
            '<link rel="stylesheet" href="/static/css/admission-cta.css">',
            self.base_html,
        )
        # Later in the document wins at equal specificity, so this layer has
        # to come after every stylesheet that used to colour these buttons.
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

    def test_breathing_is_slow_eased_and_never_blinks(self):
        halo = self._block('.jj-admission-cta::after {')
        match = re.search(
            r'animation:\s*jjCtaBreathe\s+([\d.]+)s\s+ease-in-out\s+infinite;',
            halo,
        )
        self.assertIsNotNone(
            match,
            'the halo must breathe on a <duration>s ease-in-out infinite loop',
        )
        duration = float(match.group(1))
        self.assertGreaterEqual(duration, 3.0)
        self.assertLessEqual(duration, 4.0)
        # A blink or strobe would need steps()/alternate; a slow breath does not.
        self.assertNotIn('steps(', self.css)
        self.assertNotIn('alternate', self.css)
        # The quiet end is declared on the rule itself too, so a browser that
        # never starts the animation still shows the ember instead of a flat
        # button.
        self.assertIn('opacity: .3;', halo)
        self.assertIn('box-shadow:', halo)

        body = self._keyframes('jjCtaBreathe')
        self.assertIn('0%, 100%', body)   # the quiet end of the breath
        self.assertIn('50%', body)        # the peak
        self.assertIn('opacity: 1', body)

    def test_the_breath_is_wide_enough_to_be_seen(self):
        """A glow nobody notices is the bug: the breath has to be obvious.

        An earlier pass breathed .4 -> 1 on the halo alone and read on screen
        as "almost no glow", so the amplitude is pinned numerically here.
        """
        quiet = float(re.search(
            r'opacity:\s*(\.?\d+);',
            self._block('.jj-admission-cta::after {'),
        ).group(1))
        self.assertGreaterEqual(quiet, .2, 'the exhale must stay a warm ember')
        self.assertLessEqual(quiet, .35, 'the exhale must really dim')

        ember, peak = self._keyframes('jjCtaBreathe').split('50%', 1)
        peak_opacity = float(re.search(r'opacity:\s*([\d.]+);', peak).group(1))
        self.assertEqual(peak_opacity, 1, 'the inhale must reach full bloom')
        self.assertGreaterEqual(
            peak_opacity / quiet, 2.5,
            'a breath this shallow cannot be seen on screen',
        )
        # It does not merely brighten - the bloom visibly grows.
        self.assertIn('transform: scale(1.045);', peak)
        self.assertGreater(
            self._largest_bloom(peak), self._largest_bloom(ember) * 1.4,
            'the peak bloom must be clearly larger than the ember',
        )
        self.assertGreater(
            self._strongest_alpha(peak), self._strongest_alpha(ember),
            'the peak bloom must be brighter than the ember',
        )
        self.assertGreaterEqual(
            self._strongest_alpha(peak), .8,
            'the peak must be near-opaque, not a whisper',
        )

    def test_the_button_face_breathes_in_step_with_the_halo(self):
        """One faint layer was not enough, so the rim glows on the same beat."""
        base = self._block('.jj-admission-cta {')
        face_breath = re.search(
            r'animation:\s*jjCtaFaceBreathe\s+([\d.]+)s\s+ease-in-out\s+infinite;',
            base,
        )
        self.assertIsNotNone(face_breath, 'the rim glow must breathe as well')
        halo_breath = re.search(
            r'animation:\s*jjCtaBreathe\s+([\d.]+)s\s+ease-in-out\s+infinite;',
            self._block('.jj-admission-cta::after {'),
        )
        self.assertEqual(
            face_breath.group(1), halo_breath.group(1),
            'both layers must breathe on one rhythm',
        )
        ember, peak = self._keyframes('jjCtaFaceBreathe').split('50%', 1)
        self.assertGreater(
            self._strongest_alpha(peak), self._strongest_alpha(ember),
            'the rim glow must brighten at the peak of the breath',
        )

    def test_it_wears_the_schools_own_palette(self):
        """Rhododendron face + marigold rim, and nothing else.

        Crimson + marigold is the button pair the whole site already speaks
        (.btn-primary, .jj-btn-primary, .btn-gold all wear --color-accent), so
        the CTA belongs to the page instead of carrying an outside scheme.
        Only two hues appear, which is what stops the glow looking busy.
        """
        base = self._block('.jj-admission-cta {')
        self.assertIn('border: 2px solid var(--jj-cta-gold) !important;', base)
        self.assertIn('background-image: linear-gradient(', base)
        self.assertIn('color: var(--jj-cta-white) !important;', base)
        self.assertIn('box-shadow:', base)   # never a flat button

        self.assertIn('--jj-cta-crimson: #A6314B;', self.css)      # accent
        self.assertIn('--jj-cta-crimson-deep: #8C2740;', self.css)  # deep accent
        self.assertIn('--jj-cta-gold: #E8A33D;', self.css)          # highlight
        self.assertIn('--jj-cta-amber: #C9871F;', self.css)         # halo depth
        self.assertIn('var(--jj-cta-crimson) 0%', base)

        # Discarded paints must not survive anywhere in this stylesheet: the
        # navy/cyan first pass and the pine/gold/crimson three-hue second pass.
        self.assertNotIn('--jj-cta-pine', self.css)
        for dropped in ('22d3ee', '67e8f9', '082f49', '0f172a',
                        '1f3a34', '122c26', '166, 49, 75', '16, 38, 32'):
            self.assertNotIn(dropped, self.css.lower())

        # Two hues is the whole point: every glow layer is marigold or amber,
        # never the crimson of the face (that would smear the button's edge).
        for layer in (self._block('.jj-admission-cta::after {')
                      + self._keyframes('jjCtaBreathe')):
            self.assertNotIn('rgba(166', layer)
            self.assertNotIn('rgba(60', layer)

    def test_hover_answers_without_fighting_the_keyframes(self):
        hover = self._block('.jj-admission-cta:hover {')
        self.assertIn('transform: translateY(-2px);', hover)
        # Both box-shadows belong to the animations now; a hover rule that set
        # one would lose the cascade and leave the hover looking dead.
        self.assertNotIn('box-shadow', hover)
        self.assertIn('filter: brightness(', hover)
        self.assertIn('border-color: var(--jj-cta-gold-bright) !important;',
                      hover)

        # The halo brightens on top of whatever mid-breath opacity it has.
        self.assertIn('filter: brightness(',
                      self._block('.jj-admission-cta:hover::after {'))

        icons = self._block('.jj-admission-cta:hover :is(')
        self.assertIn('transform: translateX(3px);', icons)

    def test_focus_ring_is_an_outline_not_a_shadow(self):
        """box-shadow is taken by the breath, so focus needs its own channel."""
        focus = self._block('.jj-admission-cta:focus-visible {')
        self.assertIn(
            'outline: 3px solid var(--jj-cta-gold-bright) !important;', focus
        )
        self.assertIn('outline-offset: 3px;', focus)
        self.assertNotIn('outline: none', self.css)

    def test_reduced_motion_switches_the_animation_off(self):
        block = self.css[
            self.css.index('@media (prefers-reduced-motion: reduce)'):
        ]
        self.assertIn('animation: none !important;', block)
        self.assertIn('transform: none;', block)  # the lift is motion too
        # Still lit while standing still: the steady glow is set between the
        # two ends of the breath instead of dropping to nothing.
        self.assertIn('opacity: .55;', block)
        self.assertIn('box-shadow:', block)

    def test_old_maroon_gold_cta_styling_is_gone(self):
        canonical = 'admission-cta.css'
        for path in sorted((self.root / 'static' / 'css').glob('*.css')):
            if path.name == canonical:
                continue  # the one stylesheet allowed to own these buttons
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

