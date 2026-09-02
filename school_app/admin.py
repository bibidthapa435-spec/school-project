from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin, UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User
from django.forms import DateTimeInput, TextInput
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django.db import models

# Custom DateTime Widget with better UX
class CustomDateTimeInput(DateTimeInput):
    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'datetime-local',
            'class': 'form-control datetime-picker',
            'style': 'width: 100%; padding: 0.7rem 0.9rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.9rem;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def format_value(self, value):
        """Format datetime value for datetime-local input (YYYY-MM-DDTHH:MM format)"""
        if value is None:
            return ''
        # If value is a string (may be localized), try to parse common formats
        if isinstance(value, str):
            from datetime import datetime
            for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %I:%M %p'):
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except Exception:
                    continue
            else:
                # Fallback: return empty so the input stays blank instead of invalid string
                return ''

        # Convert to local time and format for datetime-local input
        from django.utils import timezone
        if hasattr(value, 'tzinfo') and value.tzinfo is not None:
            value = timezone.localtime(value)
        return value.strftime('%Y-%m-%dT%H:%M')

from .models import (
    AdmissionApplication,
    ContactMessage,
    DownloadResource,
    GalleryPhoto,
    Notice,
    PopupNotice,
    Program,
    SiteSettings,
    Slider,
    Teacher,
)

from django import forms
from django.utils import timezone
from django.utils.dateparse import parse_datetime


class PopupNoticeForm(forms.ModelForm):
    class Meta:
        model = PopupNotice
        fields = '__all__'

    # Simple preset schedule selector (not stored on model)
    schedule_preset = forms.ChoiceField(
        required=False,
        choices=(
            ('', 'Select schedule'),
            ('always', 'Always (no dates)'),
            ('today', 'Today Only'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('custom', 'Custom Range'),
        ),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Choose a quick schedule option or pick a custom range.'
    )

    def __init__(self, *args, **kwargs):
        # Normalize QueryDict list values (from duplicated inputs or widgets)
        data = None
        if 'data' in kwargs and kwargs['data'] is not None:
            try:
                qd = kwargs['data']
                # QueryDict can be immutable; make a copy
                qd_copy = qd.copy()
                for key in ('start_date', 'end_date'):
                    values = qd_copy.getlist(key)
                    if values and len(values) > 1:
                        # prefer non-empty first value
                        qd_copy.setlist(key, [v for v in values if v is not None and v != ''][:1])
                kwargs['data'] = qd_copy
            except Exception:
                pass
        super().__init__(*args, **kwargs)
        # expose the preset field at form rendering time
        if 'schedule_preset' in self.fields:
            self.fields['schedule_preset'].initial = ''

    def _parse_datetime_input(self, value):
        if value in (None, ''):
            return None
        # If it's already a datetime object, return it
        import datetime
        if isinstance(value, datetime.datetime):
            return value

        # Try django's ISO parser first
        dt = parse_datetime(str(value))
        if dt:
            return dt

        # Try several common formats
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %I:%M %p', '%m/%d/%Y %H:%M'):
            try:
                return datetime.datetime.strptime(str(value), fmt)
            except Exception:
                continue

        # Last resort: return None so validation will catch it
        return None

    def clean_start_date(self):
        val = self.cleaned_data.get('start_date')
        parsed = self._parse_datetime_input(val)
        if parsed is None and val not in (None, ''):
            raise forms.ValidationError('Invalid start date format.')
        # If timezone-aware handling is desired, make naive -> aware in current timezone
        if parsed is not None and timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed

    def clean_end_date(self):
        val = self.cleaned_data.get('end_date')
        parsed = self._parse_datetime_input(val)
        if parsed is None and val not in (None, ''):
            raise forms.ValidationError('Invalid end date format.')
        if parsed is not None and timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed



admin.site.site_header = 'Shree Jaljala Secondary School'
admin.site.site_title = 'SJSS Administration'
admin.site.index_title = 'Admin Panel'
admin.site.index_template = 'admin/index.html'


def safe_reverse(name, fallback='#'):
    try:
        return reverse(name)
    except NoReverseMatch:
        return fallback


class AdminCSSMixin:
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(AdminCSSMixin, DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    list_per_page = 25


@admin.register(Group)
class CustomGroupAdmin(AdminCSSMixin, DjangoGroupAdmin):
    search_fields = ('name',)
    list_per_page = 25


class StatusBaseAdmin(AdminCSSMixin, admin.ModelAdmin):
    save_on_top = True
    list_per_page = 25
    ordering = ('display_order', '-created_at')
    readonly_fields = ('created_at',)
    list_editable = ('status', 'display_order')
    actions = ('make_active', 'make_inactive')

    def make_active(self, request, queryset):
        queryset.update(status=True)
    make_active.short_description = 'Mark selected items as active'

    def make_inactive(self, request, queryset):
        queryset.update(status=False)
    make_inactive.short_description = 'Mark selected items as inactive'

    def row_actions(self, obj):
        app = obj._meta.app_label
        model = obj._meta.model_name
        change_url = reverse(f'admin:{app}_{model}_change', args=[obj.pk])
        delete_url = reverse(f'admin:{app}_{model}_delete', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">Edit</a> <a class="button button-danger" href="{}">Delete</a>',
            change_url,
            delete_url,
        )
    row_actions.short_description = 'Actions'

    def get_list_display(self, request):
        base = super().get_list_display(request)
        if 'row_actions' not in base:
            return tuple(list(base) + ['row_actions'])
        return base


@admin.register(SiteSettings)
class SiteSettingsAdmin(AdminCSSMixin, admin.ModelAdmin):
    list_display = ('school_name', 'tagline', 'phone', 'email')
    fieldsets = (
        (None, {'fields': ('school_name', 'tagline', 'phone', 'email', 'address')}),
        ('Branding', {'fields': ('logo', 'favicon')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Notice)
class NoticeAdmin(StatusBaseAdmin):
    list_display = ('title', 'category', 'status', 'display_order', 'created_at', 'preview')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Notice Content', {'fields': ('category', 'category_display', 'description', 'image', 'pdf_attachment')}),
    )

    def preview(self, obj):
        if obj and getattr(obj, 'image', None):
            url = getattr(obj.image, 'url', '')
            if url:
                return format_html('<img src="{}" style="height:60px; object-fit:cover; border-radius:6px;" />', url)
        return '-'
    preview.short_description = 'Preview'


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(StatusBaseAdmin):
    list_display = ('title', 'category', 'status', 'display_order', 'created_at', 'preview')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'category')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Gallery Photo', {'fields': ('category', 'category_display', 'image')}),
    )

    def preview(self, obj):
        if obj and getattr(obj, 'image', None):
            url = getattr(obj.image, 'url', '')
            if url:
                return format_html('<img src="{}" style="height:60px; object-fit:cover; border-radius:6px;" />', url)
        return '-'
    preview.short_description = 'Preview'


@admin.register(Teacher)
class TeacherAdmin(StatusBaseAdmin):
    list_display = ('title', 'position', 'department', 'status', 'display_order', 'created_at', 'preview')
    list_filter = ('department', 'status', 'created_at')
    search_fields = ('title', 'position', 'qualification', 'email')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Professional Info', {'fields': ('position', 'qualification', 'department', 'department_display')}),
        ('Contact & Biography', {'fields': ('photo', 'email', 'phone', 'biography')}),
    )

    def preview(self, obj):
        if obj and getattr(obj, 'photo', None):
            url = getattr(obj.photo, 'url', '')
            if url:
                return format_html('<img src="{}" style="height:60px; width:60px; object-fit:cover; border-radius:50%;" />', url)
        return '-'
    preview.short_description = 'Photo'


@admin.register(Program)
class ProgramAdmin(StatusBaseAdmin):
    list_display = ('title', 'duration', 'fee', 'status', 'display_order', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Program Details', {'fields': ('image', 'duration', 'fee', 'eligibility', 'description')}),
    )


@admin.register(DownloadResource)
class DownloadResourceAdmin(StatusBaseAdmin):
    list_display = ('title', 'category', 'status', 'display_order', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Download Info', {'fields': ('category', 'category_display', 'file', 'file_size')}),
    )


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(AdminCSSMixin, admin.ModelAdmin):
    list_display = ('application_id', 'student_name', 'class_applying', 'phone', 'status', 'created_at')
    list_filter = ('status', 'gender', 'class_applying', 'created_at')
    search_fields = ('application_id', 'student_name', 'father_name', 'mother_name', 'phone', 'email', 'address')
    readonly_fields = ('application_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 25
    ordering = ['-created_at']
    
    fieldsets = (
        ('Application Information', {'fields': ('application_id', 'status')}),
        ('Student Details', {'fields': ('student_name', 'dob', 'gender')}),
        ('Parent Information', {'fields': ('father_name', 'mother_name')}),
        ('Contact Information', {'fields': ('address', 'phone', 'email')}),
        ('Academic Information', {'fields': ('class_applying', 'previous_school')}),
        ('Documents', {'fields': ('photo', 'documents')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ('mark_as_approved', 'mark_as_rejected', 'mark_as_pending')

    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved')
    mark_as_approved.short_description = 'Mark selected applications as Approved'

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = 'Mark selected applications as Rejected'

    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = 'Mark selected applications as Pending'


@admin.register(ContactMessage)
class ContactMessageAdmin(AdminCSSMixin, admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    ordering = ['-created_at']
    
    fieldsets = (
        ('Message Information', {'fields': ('name', 'email', 'phone', 'subject', 'status')}),
        ('Message Content', {'fields': ('message',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    
    actions = ('mark_as_read', 'mark_as_unread', 'mark_as_replied')

    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    mark_as_read.short_description = 'Mark selected messages as Read'

    def mark_as_unread(self, request, queryset):
        queryset.update(status='unread')
    mark_as_unread.short_description = 'Mark selected messages as Unread'

    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_as_replied.short_description = 'Mark selected messages as Replied'


@admin.register(PopupNotice)
class PopupNoticeAdmin(StatusBaseAdmin):
    list_display = ('title', 'is_active', 'status', 'schedule_status', 'display_order', 'created_at', 'preview')
    list_filter = ('is_active', 'status', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'subtitle', 'message')
    date_hierarchy = 'created_at'

    # Use better date/time widgets
    formfield_overrides = {
        models.DateTimeField: {'widget': CustomDateTimeInput},
    }
    form = PopupNoticeForm

    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Popup Content', {'fields': ('subtitle', 'image', 'message', 'button_text', 'button_url', 'is_active')}),
        ('Schedule', {
            'fields': ('schedule_preset', 'start_date', 'end_date'),
            'description': 'Choose a quick schedule from the preset selector, or pick a custom start/end range below.',
            'classes': ('wide',)
        }),
    )

    def preview(self, obj):
        if obj and getattr(obj, 'image', None):
            url = getattr(obj.image, 'url', '')
            if url:
                return format_html('<img src="{}" style="height:60px; object-fit:cover; border-radius:6px;" />', url)
        return '-'
    preview.short_description = 'Preview'

    def schedule_status(self, obj):
        """Display the current schedule status of the popup"""
        from django.utils import timezone
        now = timezone.now()
        
        if not obj.is_active:
            return format_html('<span style="color: #999;">{}</span>', '⏸ Disabled')
        
        if obj.start_date and obj.start_date > now:
            return format_html('<span style="color: #f59e0b;">⏳ Starts {}</span>', 
                             timezone.localtime(obj.start_date).strftime('%b %d, %Y %I:%M %p'))
        
        if obj.end_date and obj.end_date < now:
            return format_html('<span style="color: #ef4444;">⏹ Ended {}</span>', 
                             timezone.localtime(obj.end_date).strftime('%b %d, %Y %I:%M %p'))
        
        return format_html('<span style="color: #10b981;">{}</span>', '▶ Active Now')
    schedule_status.short_description = 'Schedule Status'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/popup_admin.js',)

    def save_model(self, request, obj, form, change):
        # Log incoming POST values for debugging date parsing issues
        import logging
        logger = logging.getLogger('school_app.popup_admin')
        # getlist to see if multiple values were submitted
        start_list = request.POST.getlist('start_date')
        end_list = request.POST.getlist('end_date')
        start_value = request.POST.get('start_date')
        end_value = request.POST.get('end_date')
        logger.debug('PopupNotice save_model POST start_date list=%s value=%s', start_list, start_value)
        logger.debug('PopupNotice save_model POST end_date list=%s value=%s', end_list, end_value)

        super().save_model(request, obj, form, change)


@admin.register(Slider) 
class SliderAdmin(StatusBaseAdmin):
    list_display = ('title', 'subtitle', 'button_text', 'status', 'display_order', 'created_at', 'preview')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'subtitle', 'description')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Slider Content', {'fields': ('subtitle', 'description', 'button_text', 'button_url', 'image', 'overlay_color', 'overlay_opacity')}),
    )

    def preview(self, obj):
        if obj and getattr(obj, 'image', None):
            url = getattr(obj.image, 'url', '')
            if url:
                return format_html('<img src="{}" style="height:60px; object-fit:cover; border-radius:6px;" />', url)
        return '-'
    preview.short_description = 'Preview'
