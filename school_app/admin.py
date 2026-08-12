from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin, UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html

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


admin.site.site_header = 'Shree Jaljala Secondary School'
admin.site.site_title = 'SJSS Administration'
admin.site.index_title = 'School Administration'
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
    list_display = ('student_name', 'class_applying', 'parent_name', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student_name', 'parent_name', 'phone', 'address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('student_name', 'parent_name', 'class_applying', 'phone', 'address', 'status')}),
    )
    actions = ('mark_as_reviewed',)

    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='Reviewed')
    mark_as_reviewed.short_description = 'Mark selected applications as Reviewed'


@admin.register(ContactMessage)
class ContactMessageAdmin(AdminCSSMixin, admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'subject', 'email', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('name', 'email', 'subject', 'message')}),
    )


@admin.register(PopupNotice)
class PopupNoticeAdmin(StatusBaseAdmin):
    list_display = ('title', 'is_active', 'status', 'display_order', 'created_at', 'preview')
    list_filter = ('is_active', 'status', 'created_at')
    search_fields = ('title', 'subtitle', 'message')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Popup Content', {'fields': ('subtitle', 'image', 'message', 'button_text', 'button_url', 'is_active')}),
    )

    def preview(self, obj):
        if obj and getattr(obj, 'image', None):
            url = getattr(obj.image, 'url', '')
            if url:
                return format_html('<img src="{}" style="height:60px; object-fit:cover; border-radius:6px;" />', url)
        return '-'
    preview.short_description = 'Preview'


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
