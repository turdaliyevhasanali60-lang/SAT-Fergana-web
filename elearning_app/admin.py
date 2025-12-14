# media/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['course_count']


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = [
        'profile_picture_preview',
        'name',
        'designation',
        'experience',
        'is_featured',
        'display_order',
        'created_at'
    ]
    list_display_links = ['name', 'profile_picture_preview']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'designation', 'bio', 'experience']
    list_editable = ['is_featured', 'display_order']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'designation',
                'experience',
                'bio',
                'email',
                'phone'
            )
        }),
        ('Profile Media', {
            'fields': ('profile_picture', 'profile_picture_preview')
        }),
        ('Social Media Links', {
            'fields': (
                'telegram',
                'twitter',
                'instagram',
                'linkedin'
            ),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['profile_picture_preview', 'created_at']

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%; object-fit:cover;" />',
                obj.profile_picture.url
            )
        return "No Photo"

    profile_picture_preview.short_description = 'Profile Picture'

    # Add some helpful actions
    actions = ['mark_as_featured', 'duplicate_instructor']

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} instructors marked as featured.')

    mark_as_featured.short_description = "Mark selected instructors as featured"

    def duplicate_instructor(self, request, queryset):
        for instructor in queryset:
            instructor.pk = None
            instructor.name = f"{instructor.name} (Copy)"
            instructor.save()
        self.message_user(request, f'{queryset.count()} instructors duplicated.')

    duplicate_instructor.short_description = "Duplicate selected instructors"


# elearning_app/admin.py - Update CourseAdmin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'instructor',
        'price',
        'current_price',
        'is_featured',
        'is_published',
        'rating',
        'enrolled_students',
        'created_at'
    ]
    list_filter = [
        'category',
        'is_featured',
        'is_published',
        'level',
        'status'
    ]
    search_fields = ['title', 'short_description', 'instructor__name']
    list_editable = ['is_featured', 'is_published', 'price']
    readonly_fields = [
        'rating',
        'rating_count',
        'enrolled_students',
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'instructor', 'level', 'status')
        }),
        ('Description', {
            'fields': ('short_description', 'full_description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Media', {
            'fields': ('thumbnail', 'featured_image')
        }),
        ('Course Details', {
            'fields': ('duration_hours', 'max_students', 'enrolled_students')
        }),
        ('Ratings', {
            'fields': ('rating', 'rating_count')
        }),
        ('Publication', {
            'fields': ('is_featured', 'is_published', 'published_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    prepopulated_fields = {'slug': ('title',)}

    actions = ['publish_courses', 'feature_courses', 'duplicate_courses']

    def publish_courses(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} courses published.')

    publish_courses.short_description = "Publish selected courses"

    def feature_courses(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} courses marked as featured.')

    feature_courses.short_description = "Feature selected courses"

    def duplicate_courses(self, request, queryset):
        for course in queryset:
            course.pk = None
            course.title = f"{course.title} (Copy)"
            course.is_published = False
            course.save()
        self.message_user(request, f'{queryset.count()} courses duplicated.')

    duplicate_courses.short_description = "Duplicate selected courses"

# elearning_app/admin.py - Update TestimonialAdmin
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = [
        'photo_preview',
        'name',
        'profession',
        'company',
        'rating_stars',
        'is_featured',
        'is_active',
        'display_order',
        'verified',
        'created_at'
    ]
    list_display_links = ['name', 'photo_preview']
    list_filter = [
        'is_featured',
        'is_active',
        'verified',
        'rating',
        'created_at'
    ]
    search_fields = ['name', 'profession', 'company', 'message']
    list_editable = [
        'is_featured',
        'is_active',
        'display_order',
        'verified'
    ]

    fieldsets = (
        ('Student Information', {
            'fields': (
                'name',
                'profession',
                'company',
                'graduation_year',
                'photo',
                'photo_preview'
            )
        }),
        ('Testimonial Content', {
            'fields': ('message', 'rating', 'course')
        }),
        ('Display Settings', {
            'fields': (
                'is_featured',
                'display_order',
                'is_active',
                'verified'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = [
        'photo_preview',
        'created_at',
        'updated_at',
        'rating_stars'
    ]

    actions = ['mark_as_featured', 'mark_as_verified', 'activate_testimonials']

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%; object-fit:cover;" />',
                obj.photo.url
            )
        return "No Photo"

    photo_preview.short_description = 'Photo'

    def rating_stars(self, obj):
        return mark_safe('<span style="color: gold;">' + '★' * obj.rating + '</span>')

    rating_stars.short_description = 'Rating'

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonials marked as featured.')

    mark_as_featured.short_description = "Mark selected testimonials as featured"

    def mark_as_verified(self, request, queryset):
        updated = queryset.update(verified=True)
        self.message_user(request, f'{updated} testimonials verified.')

    mark_as_verified.short_description = "Mark selected testimonials as verified"

    def activate_testimonials(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} testimonials activated.')

    activate_testimonials.short_description = "Activate selected testimonials"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'display_order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'display_order']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Banner Preview'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'is_active', 'display_order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'display_order']


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only one instance should exist
        return False if SiteSetting.objects.count() > 0 else True

    def has_delete_permission(self, request, obj=None):
        return False



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'ip_address', 'created_at']
    list_editable = ['status']


admin.site.register(Module)
