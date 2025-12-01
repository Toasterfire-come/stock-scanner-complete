from django.contrib import admin
from .models import (
    Course, Lesson, UserProgress, CourseCertificate,
    GlossaryTerm, UserLearningStreak
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'is_published', 'lesson_count']
    list_filter = ['category', 'difficulty', 'is_published', 'is_premium']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'content_type', 'is_published']
    list_filter = ['course', 'content_type', 'is_published', 'is_premium']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['course', 'order']

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'quiz_score', 'last_accessed']
    list_filter = ['completed', 'lesson__course']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['started_at', 'completed_at', 'last_accessed']

@admin.register(CourseCertificate)
class CourseCertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'certificate_id', 'issued_at', 'average_quiz_score']
    list_filter = ['course', 'issued_at']
    search_fields = ['user__username', 'certificate_id']
    readonly_fields = ['certificate_id', 'issued_at']

@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'category', 'difficulty', 'view_count']
    list_filter = ['category', 'difficulty']
    search_fields = ['term', 'definition']
    prepopulated_fields = {'slug': ('term',)}

@admin.register(UserLearningStreak)
class UserLearningStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'total_lessons_completed']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
