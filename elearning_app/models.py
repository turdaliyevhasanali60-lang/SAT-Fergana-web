# media/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """Course categories (Web Design, Graphic Design, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    course_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        # Update course count after saving
        self.update_course_count()

    def update_course_count(self):
        """Update the course count for this category"""
        count = Course.objects.filter(category=self, is_published=True).count()
        # Use update() to avoid infinite recursion
        Category.objects.filter(id=self.id).update(course_count=count)
        # Update the instance as well
        self.course_count = count


# elearning_app/models.py
from django.db import models


class Instructor(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    experience = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='instructors/', blank=True, null=True)

    # Contact info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Social media links
    telegram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    # Display settings
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} - {self.designation}"


class Course(models.Model):
    """Course model"""
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all', 'All Levels'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name='courses')

    # Course details
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, help_text="Course duration in hours")
    max_students = models.IntegerField(default=30)
    enrolled_students = models.IntegerField(default=0)

    # Media
    thumbnail = models.ImageField(upload_to='courses/thumbnails/')
    featured_image = models.ImageField(upload_to='courses/featured/', blank=True, null=True)

    # Ratings
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    rating_count = models.IntegerField(default=0)

    # Metadata
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_date:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def is_discounted(self):
        return self.discount_price is not None

    @property
    def discount_percentage(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    def update_rating(self, new_rating):
        """Update course rating when new review is added"""
        total_rating = (self.rating * self.rating_count) + new_rating
        self.rating_count += 1
        self.rating = total_rating / self.rating_count
        self.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_category = None

        # Get old category if updating existing course
        if not is_new:
            try:
                old_course = Course.objects.get(pk=self.pk)
                old_category = old_course.category
            except Course.DoesNotExist:
                pass

        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_date:
            self.published_date = timezone.now()

        super().save(*args, **kwargs)

        # Update course counts for categories
        if self.category:
            self.category.update_course_count()

        # Update old category count if category changed
        if old_category and old_category != self.category:
            old_category.update_course_count()

    def delete(self, *args, **kwargs):
        category = self.category
        super().delete(*args, **kwargs)

        # Update category count after deletion
        if category:
            category.update_course_count()


class Module(models.Model):
    """Course modules/lessons"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=0)
    video_url = models.URLField(blank=True)
    attachment = models.FileField(upload_to='course_modules/', blank=True, null=True)
    is_free_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# elearning_app/models.py - Update Testimonial model
class Testimonial(models.Model):
    """Student testimonials"""
    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True, help_text="Company/School name")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    message = models.TextField()

    # Optional: Link to a course the student took
    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials'
    )

    # Rating (1-5 stars)
    rating = models.IntegerField(
        choices=[(i, '⭐' * i) for i in range(1, 6)],
        default=5,
        help_text="Student rating (1-5 stars)"
    )

    # Status and ordering
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    is_active = models.BooleanField(default=True)

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional fields for verification
    graduation_year = models.IntegerField(
        blank=True,
        null=True,
        help_text="Year student graduated"
    )
    verified = models.BooleanField(
        default=False,
        help_text="Verified testimonial"
    )

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Student Testimonial"
        verbose_name_plural = "Student Testimonials"

    def __str__(self):
        return f"{self.name} - {self.profession or 'Student'}"

    def star_rating(self):
        """Return star rating as HTML"""
        return '⭐' * self.rating

    def get_display_name(self):
        """Get formatted display name"""
        if self.profession and self.company:
            return f"{self.name}, {self.profession} at {self.company}"
        elif self.profession:
            return f"{self.name}, {self.profession}"
        else:
            return f"{self.name}, Student"


class Banner(models.Model):
    """Homepage banner/slider"""
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    description = models.TextField(blank=True)  # Add this line
    image = models.ImageField(upload_to='banners/')
    button_text = models.CharField(max_length=50, default='Learn More')
    button_url = models.CharField(max_length=200, default='#')
    secondary_button_text = models.CharField(max_length=50, blank=True)
    secondary_button_url = models.CharField(max_length=200, blank=True)

    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Service(models.Model):
    """Homepage services (Skilled Instructors, Online Classes, etc.)"""
    ICON_CHOICES = [
        ('fa-graduation-cap', 'Graduation Cap'),
        ('fa-globe', 'Globe'),
        ('fa-home', 'Home'),
        ('fa-book-open', 'Book Open'),
        ('fa-laptop', 'Laptop'),
        ('fa-certificate', 'Certificate'),
        ('fa-users', 'Users'),
        ('fa-chalkboard-teacher', 'Chalkboard Teacher'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fa-graduation-cap')
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title


class SiteSetting(models.Model):
    """Site-wide settings (singleton)"""
    site_name = models.CharField(max_length=100, default='eLEARNING')
    logo = models.ImageField(upload_to='site/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/favicon/', blank=True, null=True)

    # Contact Information
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    # Social Media Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    # Footer Text
    footer_copyright = models.CharField(max_length=200, default='© Your Site Name, All Right Reserved.')
    footer_design_credit = models.CharField(max_length=200, default='Designed By HTML Codex')
    footer_design_url = models.URLField(default='https://htmlcodex.com')

    # Newsletter
    newsletter_enabled = models.BooleanField(default=True)
    newsletter_text = models.TextField(default='Dolor amet sit justo amet elitr clita ipsum elitr est.')

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)

    # Site maintenance
    site_maintenance = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)


class Gallery(models.Model):
    """Footer gallery images"""
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Gallery"
        ordering = ['display_order']

    def __str__(self):
        return self.caption or f"Gallery Image {self.id}"


class ContactMessage(models.Model):
    """Contact form messages"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Student(models.Model):
    """Registered students (if you want user registration)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='students/', blank=True, null=True)
    bio = models.TextField(blank=True)
    enrolled_courses = models.ManyToManyField(Course, through='Enrollment', related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Enrollment(models.Model):
    """Track student course enrollments"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} - {self.course}"


class FAQ(models.Model):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=200)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question