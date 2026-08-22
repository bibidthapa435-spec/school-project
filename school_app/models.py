from django.db import models
from django.utils.text import slugify


class BaseSlugModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    status = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['display_order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    school_name = models.CharField(max_length=255, default='Shree Jaljala Secondary School')
    tagline = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return self.school_name

    @property
    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return '/static/images/logo.jpg'

    @property
    def favicon_url(self):
        if self.favicon and hasattr(self.favicon, 'url'):
            return self.favicon.url
        return '/static/images/image/tilogo.png'


class Notice(BaseSlugModel):
    CATEGORY_CHOICES = [
        ('admission', 'Admission Notice'),
        ('exam', 'Examination Notice'),
        ('academic', 'Academic Notice'),
        ('event', 'Event & Activity'),
        ('general', 'General Announcement'),
    ]

    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    image = models.ImageField(upload_to='notices/', blank=True, null=True)
    pdf_attachment = models.FileField(upload_to='notices/pdfs/', blank=True, null=True)
    category_display = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.category_display:
            self.category_display = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        super().save(*args, **kwargs)


class GalleryPhoto(BaseSlugModel):
    CATEGORY_CHOICES = [
        ('school', 'School Campus & Buildings'),
        ('cultural', 'Cultural & Saraswati Puja'),
        ('sports', 'Sports & Physical Education'),
        ('classroom', 'Classroom Learning'),
        ('laboratory', 'Science & Computer Labs'),
        ('events', 'Events & Official Visits'),
        ('tour', 'Educational Tours'),
    ]

    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='school')
    category_display = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.category_display:
            self.category_display = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        super().save(*args, **kwargs)


class Teacher(BaseSlugModel):
    DEPARTMENT_CHOICES = [
        ('management', 'School Management & Administration'),
        ('science', 'Science & Mathematics'),
        ('language', 'Languages (Nepali & English)'),
        ('social', 'Social Studies & Arts'),
        ('primary', 'Primary & Early Childhood'),
        ('sports', 'Sports & Physical Education'),
    ]

    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='management')
    department_display = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    biography = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.department_display:
            self.department_display = dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)
        super().save(*args, **kwargs)


class Program(BaseSlugModel):
    image = models.ImageField(upload_to='programs/', blank=True, null=True)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=100, blank=True)
    fee = models.CharField(max_length=100, blank=True)
    eligibility = models.CharField(max_length=255, blank=True)


class DownloadResource(BaseSlugModel):
    CATEGORY_CHOICES = [
        ('syllabus', 'Syllabus & Curriculum'),
        ('routine', 'Exam Routines & Calendar'),
        ('form', 'Application Forms'),
        ('other', 'Other Resources'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    file = models.FileField(upload_to='downloads/', blank=True, null=True)
    file_size = models.CharField(max_length=50, blank=True)
    category_display = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.category_display:
            self.category_display = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        super().save(*args, **kwargs)


class AdmissionApplication(models.Model):
    student_name = models.CharField(max_length=255)
    parent_name = models.CharField(max_length=255, blank=True)
    class_applying = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=100, default='Pending Review')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.class_applying}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class PopupNotice(BaseSlugModel):
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='popups/', blank=True, null=True)
    message = models.TextField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False)


class Slider(BaseSlugModel):
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='sliders/', blank=True, null=True)
    overlay_color = models.CharField(max_length=20, default='#0b1b2b')
    overlay_opacity = models.FloatField(default=0.5)
