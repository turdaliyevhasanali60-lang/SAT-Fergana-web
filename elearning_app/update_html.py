# update_html.py
import os
import re


def update_static_references(file_path):
    """Update static file references in HTML files"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Add {% load static %} after DOCTYPE
    if '{% load static %}' not in content:
        content = content.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n{% load static %}')

    # Update CSS links
    content = re.sub(r'href="css/([^"]+)"', r'href="{% static \'css/\1\' %}"', content)
    content = re.sub(r'href="lib/([^"]+)"', r'href="{% static \'lib/\1\' %}"', content)

    # Update image sources
    content = re.sub(r'src="img/([^"]+)"', r'src="{% static \'img/\1\' %}"', content)

    # Update JavaScript sources
    content = re.sub(r'src="js/([^"]+)"', r'src="{% static \'js/\1\' %}"', content)
    content = re.sub(r'src="lib/([^"]+)"', r'src="{% static \'lib/\1\' %}"', content)

    # Update URLs
    content = content.replace('href="index.html"', 'href="{% url \'home\' %}"')
    content = content.replace('href="about.html"', 'href="{% url \'about\' %}"')
    content = content.replace('href="courses.html"', 'href="{% url \'courses\' %}"')
    content = content.replace('href="team.html"', 'href="{% url \'team\' %}"')
    content = content.replace('href="testimonial.html"', 'href="{% url \'testimonials\' %}"')
    content = content.replace('href="contact.html"', 'href="{% url \'contact\' %}"')

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"Updated: {file_path}")


# Directory containing HTML files
template_dir = 'elearning_app/templates/elearning_app/'

# List of HTML files
html_files = [
    'index.html',
    'about.html',
    'courses.html',
    'team.html',
    'testimonial.html',
    'contact.html',
]

# Update each file
for html_file in html_files:
    file_path = os.path.join(template_dir, html_file)
    if os.path.exists(file_path):
        update_static_references(file_path)
    else:
        print(f"File not found: {file_path}")