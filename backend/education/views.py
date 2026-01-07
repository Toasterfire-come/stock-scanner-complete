# app/backend/education/views.py
"""
Educational Platform API Views
Phase 7 Implementation - TradeScanPro
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import (
    Course, Lesson, UserProgress, CourseCertificate,
    GlossaryTerm, UserLearningStreak
)
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    LessonListSerializer, LessonDetailSerializer,
    UserProgressSerializer, UserProgressUpdateSerializer,
    CourseCertificateSerializer, GlossaryTermSerializer,
    GlossaryTermDetailSerializer, UserLearningStreakSerializer,
    UserLearningStatsSerializer
)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for courses
    
    Endpoints:
    - GET /api/courses/ - List all courses
    - GET /api/courses/{id}/ - Get course details
    - POST /api/courses/{id}/enroll/ - Enroll in course
    - GET /api/courses/my-courses/ - Get user's enrolled courses
    """
    
    queryset = Course.objects.filter(is_published=True).prefetch_related('lessons')
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Premium filter
        premium = self.request.query_params.get('premium', None)
        if premium is not None:
            is_premium = premium.lower() == 'true'
            queryset = queryset.filter(is_premium=is_premium)
        
        # Ensure deterministic ordering for pagination.
        return queryset.annotate(lesson_count=Count('lessons')).order_by('order', 'title')
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        """Get courses user has started"""
        user = request.user
        
        # Get courses with at least one lesson started
        started_courses = Course.objects.filter(
            lessons__user_progress__user=user
        ).distinct()
        
        serializer = self.get_serializer(started_courses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, slug=None):
        """Enroll user in course (creates progress for first lesson)"""
        course = self.get_object()
        user = request.user
        
        # Check if premium and user has access
        if course.is_premium and not self._has_premium_access(user):
            return Response(
                {'detail': 'Premium subscription required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get first lesson
        first_lesson = course.lessons.order_by('order').first()
        if not first_lesson:
            return Response(
                {'detail': 'Course has no lessons'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or get progress for first lesson
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=first_lesson
        )
        
        return Response({
            'message': 'Enrolled successfully' if created else 'Already enrolled',
            'first_lesson_slug': first_lesson.slug
        })
    
    def _has_premium_access(self, user):
        """Check if user has premium subscription"""
        try:
            from stocks.models import UserProfile
            profile = UserProfile.objects.get(user=user)
            return profile.subscription_tier == 'premium'
        except:
            return False


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for lessons
    
    Endpoints:
    - GET /api/lessons/ - List lessons
    - GET /api/lessons/{id}/ - Get lesson details
    - POST /api/lessons/{id}/start/ - Start lesson
    - POST /api/lessons/{id}/complete/ - Mark lesson complete
    - POST /api/lessons/{id}/submit-quiz/ - Submit quiz
    - PATCH /api/lessons/{id}/update-progress/ - Update time spent
    """
    
    queryset = Lesson.objects.filter(is_published=True).select_related('course')
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by course
        course_slug = self.request.query_params.get('course', None)
        if course_slug:
            queryset = queryset.filter(course__slug=course_slug)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start(self, request, slug=None):
        """Start a lesson (create progress record)"""
        lesson = self.get_object()
        user = request.user
        
        # Check premium access
        if lesson.is_premium and not self._has_premium_access(user):
            return Response(
                {'detail': 'Premium subscription required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create or get progress
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=lesson
        )
        
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, slug=None):
        """Mark lesson as completed"""
        lesson = self.get_object()
        user = request.user
        
        try:
            progress = UserProgress.objects.get(user=user, lesson=lesson)
        except UserProgress.DoesNotExist:
            return Response(
                {'detail': 'Lesson not started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
            
            # Update learning streak
            self._update_learning_streak(user)
            
            # Check if course is complete for certificate
            self._check_course_completion(user, lesson.course)
        
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_quiz(self, request, slug=None):
        """Submit quiz answers and calculate score"""
        lesson = self.get_object()
        user = request.user
        answers = request.data.get('answers', [])
        
        try:
            progress = UserProgress.objects.get(user=user, lesson=lesson)
        except UserProgress.DoesNotExist:
            return Response(
                {'detail': 'Lesson not started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate score
        quiz_questions = lesson.quiz_questions or []
        if not quiz_questions:
            return Response(
                {'detail': 'No quiz available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        correct = 0
        for i, question in enumerate(quiz_questions):
            if i < len(answers) and answers[i] == question['correct']:
                correct += 1
        
        score = int((correct / len(quiz_questions)) * 100)
        
        # Update progress
        progress.quiz_score = score
        progress.quiz_attempts += 1
        progress.quiz_answers = answers
        progress.save()
        
        return Response({
            'score': score,
            'correct': correct,
            'total': len(quiz_questions),
            'passed': score >= 70
        })
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_progress(self, request, slug=None):
        """Update time spent on lesson"""
        lesson = self.get_object()
        user = request.user
        
        try:
            progress = UserProgress.objects.get(user=user, lesson=lesson)
        except UserProgress.DoesNotExist:
            return Response(
                {'detail': 'Lesson not started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserProgressUpdateSerializer(
            progress,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(UserProgressSerializer(progress).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _has_premium_access(self, user):
        """Check if user has premium subscription"""
        try:
            from stocks.models import UserProfile
            profile = UserProfile.objects.get(user=user)
            return profile.subscription_tier == 'premium'
        except:
            return False
    
    def _update_learning_streak(self, user):
        """Update user's learning streak"""
        streak, created = UserLearningStreak.objects.get_or_create(user=user)
        
        today = timezone.now().date()
        
        if created or streak.last_activity_date is None:
            streak.current_streak = 1
            streak.longest_streak = 1
        elif streak.last_activity_date == today:
            # Already logged today, no change
            pass
        elif streak.last_activity_date == today - timedelta(days=1):
            # Consecutive day
            streak.current_streak += 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        else:
            # Streak broken
            streak.current_streak = 1
        
        streak.last_activity_date = today
        streak.total_lessons_completed += 1
        streak.save()
    
    def _check_course_completion(self, user, course):
        """Check if user completed all lessons and issue certificate"""
        total_lessons = course.lessons.count()
        completed_lessons = UserProgress.objects.filter(
            user=user,
            lesson__course=course,
            completed=True
        ).count()
        
        if total_lessons > 0 and total_lessons == completed_lessons:
            # All lessons completed, issue certificate if not already issued
            if not CourseCertificate.objects.filter(user=user, course=course).exists():
                # Calculate stats
                progress_records = UserProgress.objects.filter(
                    user=user,
                    lesson__course=course
                )
                
                total_time = progress_records.aggregate(
                    total=Sum('time_spent_seconds')
                )['total'] or 0
                
                avg_score = progress_records.filter(
                    quiz_score__isnull=False
                ).aggregate(
                    avg=Avg('quiz_score')
                )['avg'] or 0
                
                CourseCertificate.objects.create(
                    user=user,
                    course=course,
                    completion_time_hours=total_time / 3600,
                    average_quiz_score=int(avg_score)
                )


class GlossaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for glossary terms
    
    Endpoints:
    - GET /api/glossary/ - List all terms
    - GET /api/glossary/{slug}/ - Get term details
    - GET /api/glossary/search/ - Search terms
    - GET /api/glossary/by-category/ - Group by category
    - POST /api/glossary/{slug}/track-view/ - Track term view
    """
    
    queryset = GlossaryTerm.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['term', 'definition']
    ordering_fields = ['term', 'view_count', 'created_at']
    ordering = ['term']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GlossaryTermDetailSerializer
        return GlossaryTermSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by first letter
        letter = self.request.query_params.get('letter', None)
        if letter and len(letter) == 1:
            queryset = queryset.filter(term__istartswith=letter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get terms grouped by category"""
        categories = {}
        
        for choice in GlossaryTerm.CATEGORY_CHOICES:
            category_key = choice[0]
            category_name = choice[1]
            
            terms = self.get_queryset().filter(category=category_key)
            categories[category_key] = {
                'name': category_name,
                'terms': GlossaryTermSerializer(terms, many=True).data
            }
        
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def track_view(self, request, slug=None):
        """Track when a term is viewed"""
        term = self.get_object()
        term.view_count += 1
        term.save(update_fields=['view_count'])
        return Response({'view_count': term.view_count})
    
    @action(detail=True, methods=['post'])
    def track_tooltip(self, request, slug=None):
        """Track when a term tooltip is hovered"""
        term = self.get_object()
        term.tooltip_hover_count += 1
        term.save(update_fields=['tooltip_hover_count'])
        return Response({'tooltip_hover_count': term.tooltip_hover_count})


class UserStatsViewSet(viewsets.ViewSet):
    """
    ViewSet for user learning statistics
    
    Endpoints:
    - GET /api/user-stats/overview/ - Get overall stats
    - GET /api/user-stats/streak/ - Get learning streak
    - GET /api/user-stats/certificates/ - Get earned certificates
    - GET /api/user-stats/progress/ - Get all progress records
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get comprehensive user learning statistics"""
        user = request.user
        
        # Courses
        courses_started = Course.objects.filter(
            lessons__user_progress__user=user
        ).distinct().count()
        
        courses_completed = CourseCertificate.objects.filter(user=user).count()
        
        # Lessons
        lessons_completed = UserProgress.objects.filter(
            user=user,
            completed=True
        ).count()
        
        # Time spent
        total_time_seconds = UserProgress.objects.filter(
            user=user
        ).aggregate(total=Sum('time_spent_seconds'))['total'] or 0
        
        # Quiz performance
        avg_quiz_score = UserProgress.objects.filter(
            user=user,
            quiz_score__isnull=False
        ).aggregate(avg=Avg('quiz_score'))['avg'] or 0
        
        # Streak
        try:
            streak = UserLearningStreak.objects.get(user=user)
            current_streak = streak.current_streak
            longest_streak = streak.longest_streak
        except UserLearningStreak.DoesNotExist:
            current_streak = 0
            longest_streak = 0
        
        # Recent activity
        recent_progress = UserProgress.objects.filter(
            user=user
        ).order_by('-last_accessed')[:5]
        
        recent_activity = []
        for progress in recent_progress:
            recent_activity.append({
                'lesson_title': progress.lesson.title,
                'course_title': progress.lesson.course.title,
                'completed': progress.completed,
                'last_accessed': progress.last_accessed
            })
        
        data = {
            'total_courses_started': courses_started,
            'total_courses_completed': courses_completed,
            'total_lessons_completed': lessons_completed,
            'total_time_spent_hours': round(total_time_seconds / 3600, 2),
            'average_quiz_score': round(avg_quiz_score, 1),
            'certificates_earned': courses_completed,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'recent_activity': recent_activity
        }
        
        serializer = UserLearningStatsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def streak(self, request):
        """Get user's learning streak"""
        user = request.user
        
        try:
            streak = UserLearningStreak.objects.get(user=user)
            serializer = UserLearningStreakSerializer(streak)
            return Response(serializer.data)
        except UserLearningStreak.DoesNotExist:
            return Response({
                'current_streak': 0,
                'longest_streak': 0,
                'last_activity_date': None,
                'total_lessons_completed': 0,
                'total_time_spent_hours': 0
            })
    
    @action(detail=False, methods=['get'])
    def certificates(self, request):
        """Get user's earned certificates"""
        user = request.user
        certificates = CourseCertificate.objects.filter(user=user)
        serializer = CourseCertificateSerializer(certificates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """Get all user progress records"""
        user = request.user
        progress = UserProgress.objects.filter(user=user).order_by('-last_accessed')
        serializer = UserProgressSerializer(progress, many=True)
        return Response(serializer.data)
