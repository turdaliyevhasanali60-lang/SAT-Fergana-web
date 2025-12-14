# media/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.views.generic import ListView, DetailView, TemplateView
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import (
    Category, Course, Instructor, Testimonial,
    Banner, Service, SiteSetting, Gallery,
    ContactMessage, FAQ, Student, Enrollment
)
from .forms import ContactForm


# ========== Home Page View ==========
# views.py
from django.shortcuts import render
from .models import Category, Course, Instructor, Testimonial


# Update the home function in views.py
def home(request):
    """Home page view"""
    # Get active banners ordered by display_order
    banners = Banner.objects.filter(is_active=True).order_by('display_order')

    # Get some sample data
    categories = Category.objects.filter(is_active=True)[:4]
    courses = Course.objects.filter(is_published=True, is_featured=True)[:3]
    instructors = Instructor.objects.filter(is_featured=True)[:4]
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)[:4]

    # Get statistics
    total_students = Student.objects.count() or 2000
    total_courses = Course.objects.filter(is_published=True).count()
    total_instructors = Instructor.objects.count()

    context = {
        'banners': banners,
        'categories': categories,
        'featured_courses': courses,
        'featured_instructors': instructors,
        'featured_testimonials': testimonials,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
    }
    return render(request, 'index.html', context)


def courses(request):
    """Courses page with filtering"""
    # Get all published courses
    courses_list = Course.objects.filter(is_published=True).order_by('-created_at')


    # Get all active categories
    categories = Category.objects.filter(is_active=True)

    # Get filter parameters from request
    category_filter = request.GET.get('category')
    level_filter = request.GET.get('level')
    search_query = request.GET.get('search')

    # Apply filters
    if category_filter:
        courses_list = courses_list.filter(category__slug=category_filter)

    if level_filter:
        courses_list = courses_list.filter(level=level_filter)

    if search_query:
        courses_list = courses_list.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(full_description__icontains=search_query) |
            Q(instructor__name__icontains=search_query)
        )

    # Get course statistics
    course_stats = {
        'total': Course.objects.filter(is_published=True).count(),
        'beginner': Course.objects.filter(level='beginner', is_published=True).count(),
        'intermediate': Course.objects.filter(level='intermediate', is_published=True).count(),
        'advanced': Course.objects.filter(level='advanced', is_published=True).count(),
    }

    # Get featured courses for sidebar (optional)
    featured_courses = Course.objects.filter(
        is_featured=True,
        is_published=True
    ).order_by('-created_at')[:4]

    total_students = sum(course.enrolled_students for course in courses_list)

    avg_rating = courses_list.aggregate(avg=Avg('rating'))['avg'] or 0

    context = {
        'courses': courses_list,
        'categories': categories,
        'course_stats': course_stats,
        'featured_courses': featured_courses,
        'selected_category': category_filter,
        'selected_level': level_filter,
        'search_query': search_query or '',
        'title': 'Courses - SAT Fergana',
        'total_students': total_students,
        'avg_rating': avg_rating,
    }
    return render(request, 'courses.html', context)


def team(request):
    """Team/Instructors page"""
    # Get all active instructors, ordered by display order
    instructors = Instructor.objects.all().order_by('display_order')
    total_courses = sum(len(instructor.courses.all()) for instructor in instructors)
    context = {
        'instructors': instructors,
        'title': 'Our Team - SAT Fergana',
        'total_courses': total_courses,
    }
    return render(request, 'team.html', context)


def testimonials(request):
    """Testimonials page"""
    # Get active testimonials, ordered by display order
    testimonials_list = Testimonial.objects.filter(is_active=True).order_by('display_order', '-created_at')

    # Get featured testimonials for sidebar/widget
    featured_testimonials = Testimonial.objects.filter(
        is_featured=True,
        is_active=True
    ).order_by('display_order')[:4]

    # Calculate statistics
    total_testimonials = testimonials_list.count()

    # Calculate average rating
    if total_testimonials > 0:
        average_rating = testimonials_list.aggregate(Avg('rating'))['rating__avg']
        average_rating = round(average_rating, 1)
    else:
        average_rating = 0

    # Calculate satisfaction rate (example: percentage of 4-5 star ratings)
    high_rating_count = testimonials_list.filter(rating__gte=4).count()
    satisfaction_rate = round((high_rating_count / total_testimonials * 100) if total_testimonials > 0 else 0)

    context = {
        'testimonials': testimonials_list,
        'featured_testimonials': featured_testimonials,
        'total_testimonials': total_testimonials,
        'average_rating': average_rating,
        'satisfaction_rate': satisfaction_rate,
        'active_students': total_testimonials,  # You can change this if you have actual student count
        'title': 'Testimonials - SAT Fergana',
    }
    return render(request, 'testimonial.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.ip_address = request.META.get('REMOTE_ADDR')
            contact_message.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


# Update the about function in views.py
def about(request):
    """About page"""
    # Get all active instructors, ordered by display order
    instructors = Instructor.objects.all().order_by('display_order')

    # Get some statistics
    total_instructors = instructors.count()
    total_courses = Course.objects.filter(is_published=True).count()
    total_students = Student.objects.count() or 1500  # Default if no students

    context = {
        'instructors': instructors,
        'total_instructors': total_instructors,
        'total_courses': total_courses,
        'total_students': total_students,
        'title': 'About Us - SAT Fergana',
    }
    return render(request, 'about.html', context)


