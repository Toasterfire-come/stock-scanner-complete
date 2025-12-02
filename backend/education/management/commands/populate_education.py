"""
Management command to populate education database from JSON files
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from education.models import Course, Lesson, GlossaryTerm


class Command(BaseCommand):
    help = 'Populate education database from course_content.json and glossary_terms.json'

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        # Load course content
        course_file = base_dir / 'course_content.json'
        if course_file.exists():
            with open(course_file, 'r') as f:
                data = json.load(f)
            
            for course_data in data.get('courses', []):
                lessons = course_data.pop('lessons', [])
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
                    }
                )
                action = 'Created' if created else 'Updated'
                self.stdout.write(f'{action} course: {course.title}')
                
                for lesson_data in lessons:
                    lesson, lesson_created = Lesson.objects.update_or_create(
                        course=course,
                        slug=lesson_data['slug'],
                        defaults={
                            'title': lesson_data['title'],
                            'content_type': lesson_data['content_type'],
                            'order': lesson_data['order'],
                            'duration_minutes': lesson_data['duration_minutes'],
                            'content': lesson_data['content'],
                            'video_url': lesson_data.get('video_url', ''),
                            'key_takeaways': lesson_data.get('key_takeaways', []),
                            'quiz_questions': lesson_data.get('quiz_questions', []),
                            'is_published': True,
                        }
                    )
                    action = 'Created' if lesson_created else 'Updated'
                    self.stdout.write(f'  {action} lesson: {lesson.title}')
        
        # Load glossary terms
        glossary_file = base_dir / 'glossary_terms.json'
        if glossary_file.exists():
            with open(glossary_file, 'r') as f:
                terms_data = json.load(f)
            
            for term_data in terms_data.get('terms', []):
                term, created = GlossaryTerm.objects.update_or_create(
                    term=term_data['term'],
                    defaults={
                        'definition': term_data['definition'],
                        'category': term_data.get('category', 'general'),
                        'related_terms': term_data.get('related_terms', []),
                        'example': term_data.get('example', ''),
                    }
                )
                action = 'Created' if created else 'Updated'
                self.stdout.write(f'{action} term: {term.term}')
        
        self.stdout.write(self.style.SUCCESS('Education data populated successfully!'))
