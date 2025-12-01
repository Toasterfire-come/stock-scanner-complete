# app/backend/education/serializers.py
"""
Educational Platform Serializers
Phase 7 Implementation - TradeScanPro
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Course, Lesson, UserProgress, CourseCertificate,
    GlossaryTerm, UserLearningStreak
)


class GlossaryTermSerializer(serializers.ModelSerializer):
    """Serializer for glossary terms"""
    
    related_term_names = serializers.SerializerMethodField()
    
    class Meta:
        model = GlossaryTerm
        fields = [
            'id', 'term', 'slug', 'category', 'definition',
            'example', 'difficulty', 'related_term_names',
            'view_count'
        ]
    
    def get_related_term_names(self, obj):
        return [term.term for term in obj.related_terms.all()[:5]]


class GlossaryTermDetailSerializer(GlossaryTermSerializer):
    """Detailed glossary term with full related terms"""
    
    related_terms = serializers.SerializerMethodField()
    
    class Meta(GlossaryTermSerializer.Meta):
        fields = GlossaryTermSerializer.Meta.fields + ['related_terms']
    
    def get_related_terms(self, obj):
        return GlossaryTermSerializer(obj.related_terms.all(), many=True).data


class LessonListSerializer(serializers.ModelSerializer):
    """Simplified lesson serializer for course listings"""
    
    is_completed = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content_type', 'order',
            'duration_minutes', 'is_premium', 'is_completed',
            'user_progress'
        ]
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=request.user, lesson=obj)
                return progress.completed
            except UserProgress.DoesNotExist:
                return False
        return False
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=request.user, lesson=obj)
                return {
                    'completed': progress.completed,
                    'quiz_score': progress.quiz_score,
                    'progress_percentage': progress.progress_percentage,
                    'time_spent_minutes': progress.time_spent_seconds // 60
                }
            except UserProgress.DoesNotExist:
                return None
        return None


class LessonDetailSerializer(serializers.ModelSerializer):
    """Full lesson details including content"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    related_terms = GlossaryTermSerializer(many=True, read_only=True)
    next_lesson = serializers.SerializerMethodField()
    previous_lesson = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'course_title', 'title', 'slug',
            'content_type', 'content', 'video_url', 'interactive_demo',
            'quiz_questions', 'key_takeaways', 'order', 'duration_minutes',
            'related_terms', 'next_lesson', 'previous_lesson',
            'user_progress', 'is_premium'
        ]
    
    def get_next_lesson(self, obj):
        try:
            next_lesson = Lesson.objects.filter(
                course=obj.course,
                order__gt=obj.order
            ).order_by('order').first()
            
            if next_lesson:
                return {
                    'id': next_lesson.id,
                    'title': next_lesson.title,
                    'slug': next_lesson.slug
                }
        except Lesson.DoesNotExist:
            pass
        return None
    
    def get_previous_lesson(self, obj):
        try:
            prev_lesson = Lesson.objects.filter(
                course=obj.course,
                order__lt=obj.order
            ).order_by('-order').first()
            
            if prev_lesson:
                return {
                    'id': prev_lesson.id,
                    'title': prev_lesson.title,
                    'slug': prev_lesson.slug
                }
        except Lesson.DoesNotExist:
            pass
        return None
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=request.user, lesson=obj)
                return {
                    'completed': progress.completed,
                    'quiz_score': progress.quiz_score,
                    'quiz_attempts': progress.quiz_attempts,
                    'time_spent_minutes': progress.time_spent_seconds // 60,
                    'progress_percentage': progress.progress_percentage,
                    'started_at': progress.started_at,
                    'completed_at': progress.completed_at
                }
            except UserProgress.DoesNotExist:
                return None
        return None


class CourseListSerializer(serializers.ModelSerializer):
    """Course list serializer with summary info"""
    
    lesson_count = serializers.IntegerField(read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'category', 'title', 'slug', 'description',
            'thumbnail_url', 'difficulty', 'duration_minutes',
            'lesson_count', 'completion_percentage', 'is_premium', 'order'
        ]
    
    def get_completion_percentage(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            total_lessons = obj.lessons.count()
            if total_lessons == 0:
                return 0
            
            completed_lessons = UserProgress.objects.filter(
                user=request.user,
                lesson__course=obj,
                completed=True
            ).count()
            
            return int((completed_lessons / total_lessons) * 100)
        return 0


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course details with lessons"""
    
    lessons = LessonListSerializer(many=True, read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    has_certificate = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'category', 'title', 'slug', 'description',
            'thumbnail_url', 'difficulty', 'duration_minutes',
            'lessons', 'completion_percentage', 'completed_lessons',
            'total_lessons', 'has_certificate', 'is_premium', 'order'
        ]
    
    def get_completion_percentage(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            total_lessons = obj.lessons.count()
            if total_lessons == 0:
                return 0
            
            completed_lessons = UserProgress.objects.filter(
                user=request.user,
                lesson__course=obj,
                completed=True
            ).count()
            
            return int((completed_lessons / total_lessons) * 100)
        return 0
    
    def get_completed_lessons(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserProgress.objects.filter(
                user=request.user,
                lesson__course=obj,
                completed=True
            ).count()
        return 0
    
    def get_total_lessons(self, obj):
        return obj.lessons.count()
    
    def get_has_certificate(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseCertificate.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False


class UserProgressSerializer(serializers.ModelSerializer):
    """User progress tracking serializer"""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'course_title',
            'completed', 'quiz_score', 'quiz_attempts',
            'time_spent_seconds', 'progress_percentage',
            'started_at', 'completed_at', 'last_accessed'
        ]
        read_only_fields = ['started_at', 'last_accessed']


class UserProgressUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user progress"""
    
    class Meta:
        model = UserProgress
        fields = [
            'completed', 'quiz_score', 'quiz_answers',
            'time_spent_seconds'
        ]
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        # If marking as completed, set completion timestamp
        if validated_data.get('completed') and not instance.completed:
            validated_data['completed_at'] = timezone.now()
        
        # Track quiz attempts if quiz_score is being updated
        if 'quiz_score' in validated_data and validated_data['quiz_score'] is not None:
            instance.quiz_attempts += 1
        
        return super().update(instance, validated_data)


class CourseCertificateSerializer(serializers.ModelSerializer):
    """Certificate serializer"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = CourseCertificate
        fields = [
            'id', 'certificate_id', 'course', 'course_title',
            'user_name', 'issued_at', 'completion_time_hours',
            'average_quiz_score'
        ]
        read_only_fields = ['certificate_id', 'issued_at']


class UserLearningStreakSerializer(serializers.ModelSerializer):
    """Learning streak serializer"""
    
    class Meta:
        model = UserLearningStreak
        fields = [
            'current_streak', 'longest_streak', 'last_activity_date',
            'total_lessons_completed', 'total_time_spent_hours'
        ]
        read_only_fields = fields


class UserLearningStatsSerializer(serializers.Serializer):
    """Combined user learning statistics"""
    
    total_courses_started = serializers.IntegerField()
    total_courses_completed = serializers.IntegerField()
    total_lessons_completed = serializers.IntegerField()
    total_time_spent_hours = serializers.FloatField()
    average_quiz_score = serializers.FloatField()
    certificates_earned = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    recent_activity = serializers.ListField()
