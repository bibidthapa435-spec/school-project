from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import (
    Notice,
    GalleryPhoto,
    Teacher,
    Program,
    DownloadResource,
    AdmissionApplication,
    ContactMessage,
    PopupNotice,
    Slider,
    SiteSettings,
)


admin.site.site_header = 'Shree Jaljala Secondary School Admin'
admin.site.site_title = 'Jaljala School Admin'
admin.site.index_title = 'School Management Dashboard'


class StatusBaseAdmin(admin.ModelAdmin):
    save_on_top = True
    list_per_page = 30
    ordering = ('display_order', '-created_at')
    readonly_fields = ('created_at',)
    list_editable = ('status', 'display_order')
    actions = ('make_active', 'make_inactive')
    
    class Media:
        css = {
            'all': ('admin/custom_admin.css',)
        }

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
        return mark_safe(
            f"<a class='button' href='{change_url}'>Edit</a> "
            f"<a class='button button-danger' href='{delete_url}'>Delete</a>"
        )
    row_actions.short_description = 'Actions'

    def get_list_display(self, request):
        base = super().get_list_display(request)
        if 'row_actions' not in base:
            return tuple(list(base) + ['row_actions'])
        return base


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'phone', 'email')
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
    list_display = ('title', 'category', 'preview', 'status', 'display_order', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description')
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Notice Content', {'fields': ('category', 'category_display', 'description', 'image', 'pdf_attachment')}),
    )
    def preview(self, obj):
        if obj and getattr(obj, 'image'):
            url = getattr(obj.image, 'url', '')
            if url:
                return mark_safe(f"<img src='{url}' style='height:60px; object-fit:cover; border-radius:6px;' />")
        return '-'
    preview.short_description = 'Preview'


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(StatusBaseAdmin):
    list_display = ('title', 'category', 'preview', 'status', 'display_order', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title',)
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Gallery Photo', {'fields': ('category', 'category_display', 'image')}),
    )
    def preview(self, obj):
        if obj and getattr(obj, 'image'):
            url = getattr(obj.image, 'url', '')
            if url:
                return mark_safe(f"<img src='{url}' style='height:60px; object-fit:cover; border-radius:6px;' />")
        return '-'
    preview.short_description = 'Preview'


@admin.register(Teacher)
class TeacherAdmin(StatusBaseAdmin):
    list_display = ('title', 'position', 'department', 'preview', 'status', 'display_order')
    list_filter = ('department', 'status', 'created_at')
    search_fields = ('title', 'position', 'qualification', 'email')
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Professional Info', {'fields': ('position', 'qualification', 'department', 'department_display')}),
        ('Contact & Biography', {'fields': ('photo', 'email', 'phone', 'biography')}),
    )
    def preview(self, obj):
        if obj and getattr(obj, 'photo'):
            url = getattr(obj.photo, 'url', '')
            if url:
                return mark_safe(f"<img src='{url}' style='height:60px; width:60px; object-fit:cover; border-radius:50%;' />")
        return '-'
    preview.short_description = 'Photo'


@admin.register(Program)
class ProgramAdmin(StatusBaseAdmin):
    list_display = ('title', 'duration', 'fee', 'status', 'display_order')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Program Details', {'fields': ('image', 'duration', 'fee', 'eligibility', 'description')}),
    )


@admin.register(DownloadResource)
class DownloadResourceAdmin(StatusBaseAdmin):
    list_display = ('title', 'category', 'status', 'display_order', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title',)
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Download Info', {'fields': ('category', 'category_display', 'file', 'file_size')}),
    )


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'class_applying', 'parent_name', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student_name', 'parent_name', 'phone', 'address')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('student_name', 'parent_name', 'class_applying', 'phone', 'address', 'status')}),
    )
    actions = ('mark_as_reviewed',)

    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='Reviewed')
    mark_as_reviewed.short_description = 'Mark selected applications as Reviewed'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'subject', 'email', 'message')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('name', 'email', 'subject', 'message')}),
    )


@admin.register(PopupNotice)
class PopupNoticeAdmin(StatusBaseAdmin):
    list_display = ('title', 'is_active', 'status', 'preview', 'display_order', 'created_at')
    list_filter = ('is_active', 'status', 'created_at')
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Popup Content', {'fields': ('subtitle', 'image', 'message', 'button_text', 'button_url', 'is_active')}),
    )
    def preview(self, obj):
        if obj and getattr(obj, 'image'):
            url = getattr(obj.image, 'url', '')
            if url:
                return mark_safe(f"<img src='{url}' style='height:60px; object-fit:cover; border-radius:6px;' />")
        return '-'
    preview.short_description = 'Preview'


@admin.register(Slider)
class SliderAdmin(StatusBaseAdmin):
    list_display = ('title', 'button_text', 'preview', 'status', 'display_order', 'created_at')
    list_filter = ('status', 'created_at')
    fieldsets = (
        (None, {'fields': ('title', 'status', 'display_order')}),
        ('Slider Content', {'fields': ('subtitle', 'description', 'button_text', 'button_url', 'image', 'overlay_color', 'overlay_opacity')}),
    )
    def preview(self, obj):
        if obj and getattr(obj, 'image'):
            url = getattr(obj.image, 'url', '')
            if url:
                return mark_safe(f"<img src='{url}' style='height:60px; object-fit:cover; border-radius:6px;' />")
        return '-'
    preview.short_description = 'Preview'
