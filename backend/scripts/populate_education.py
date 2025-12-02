#!/usr/bin/env python
"""
Script to populate the education database with courses and glossary terms
from the JSON data files.
"""
import os
import sys
import json
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings_local_sqlite')
django.setup()

from education.models import Course, Lesson, GlossaryTerm


def load_courses(data_path):
    """Load courses and lessons from JSON file."""
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    courses_created = 0
    lessons_created = 0
    
    for course_data in data.get('courses', []):
        lessons = course_data.pop('lessons', [])
        
        # Create or update the course
        course, created = Course.objects.update_or_create(
            category=course_data['category'],
            defaults={
                'title': course_data['title'],
                'slug': course_data['slug'],
                'description': course_data['description'],
                'thumbnail_url': course_data.get('thumbnail_url', ''),
                'difficulty': course_data['difficulty'],
                'duration_minutes': course_data['duration_minutes'],
                'is_premium': course_data.get('is_premium', False),
                'is_published': True,
                'order': course_data.get('order', 0),
            }
        )
        
        if created:
            courses_created += 1
            print(f"  Created course: {course.title}")
        else:
            print(f"  Updated course: {course.title}")
        
        # Create lessons for this course
        for lesson_data in lessons:
            lesson, lesson_created = Lesson.objects.update_or_create(
                course=course,
                slug=lesson_data['slug'],
                defaults={
                    'title': lesson_data['title'],
                    'content_type': lesson_data['content_type'],
                    'content': lesson_data['content'],
                    'video_url': lesson_data.get('video_url', ''),
                    'order': lesson_data['order'],
                    'duration_minutes': lesson_data['duration_minutes'],
                    'key_takeaways': lesson_data.get('key_takeaways', []),
                    'quiz_questions': lesson_data.get('quiz_questions', []),
                    'is_premium': lesson_data.get('is_premium', False),
                    'is_published': True,
                }
            )
            
            if lesson_created:
                lessons_created += 1
    
    return courses_created, lessons_created


def load_glossary(data_path):
    """Load glossary terms from JSON file."""
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    terms_created = 0
    
    for term_data in data.get('glossary_terms', []):
        term, created = GlossaryTerm.objects.update_or_create(
            term=term_data['term'],
            defaults={
                'slug': term_data['slug'],
                'category': term_data['category'],
                'definition': term_data['definition'],
                'example': term_data.get('example', ''),
                'difficulty': term_data.get('difficulty', 'beginner'),
            }
        )
        
        if created:
            terms_created += 1
    
    return terms_created


def main():
    print("=" * 60)
    print("Populating Education Database")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Load courses
    course_path = os.path.join(base_path, 'data', 'course_content.json')
    if os.path.exists(course_path):
        print(f"\nLoading courses from: {course_path}")
        courses, lessons = load_courses(course_path)
        print(f"  Courses created: {courses}")
        print(f"  Lessons created: {lessons}")
        print(f"  Total courses: {Course.objects.count()}")
        print(f"  Total lessons: {Lesson.objects.count()}")
    else:
        print(f"Course file not found: {course_path}")
    
    # Load glossary terms
    glossary_path = os.path.join(base_path, 'data', 'glossary_terms.json')
    if os.path.exists(glossary_path):
        print(f"\nLoading glossary from: {glossary_path}")
        terms = load_glossary(glossary_path)
        print(f"  Terms created: {terms}")
        print(f"  Total terms: {GlossaryTerm.objects.count()}")
    else:
        print(f"Glossary file not found: {glossary_path}")
    
    print("\n" + "=" * 60)
    print("Education database population complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
