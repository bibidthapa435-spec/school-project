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
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    # Generate unique application ID
    application_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Student Information
    student_name = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Parent Information
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    
    # Contact Information
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Academic Information
    class_applying = models.CharField(max_length=50)
    previous_school = models.CharField(max_length=255, blank=True)
    
    # Documents
    photo = models.ImageField(upload_to='admissions/photos/', blank=True, null=True)
    documents = models.FileField(upload_to='admissions/documents/', blank=True, null=True)
    
    # Status and Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admission Application'
        verbose_name_plural = 'Admission Applications'
    
    def __str__(self):
        return f"{self.application_id} - {self.student_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_id:
            # Generate unique application ID: ADM + year + random 6 digits
            import random
            from django.utils import timezone
            year = timezone.now().year
            random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            self.application_id = f"ADM{year}{random_digits}"
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class PopupNotice(BaseSlugModel):
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='popups/', blank=True, null=True)
    message = models.TextField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def is_currently_active(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True


class Slider(BaseSlugModel):
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='sliders/', blank=True, null=True)
    overlay_color = models.CharField(max_length=20, default='#0b1b2b')
    overlay_opacity = models.FloatField(default=0.5)



