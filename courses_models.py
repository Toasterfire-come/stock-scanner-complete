# app/backend/education/models.py
"""
Educational Platform Models
Phase 7 Implementation - TradeScanPro
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Course(models.Model):
    """Main course categories"""
    
    CATEGORY_CHOICES = [
        ('fundamentals', 'Trading Fundamentals'),
        ('technical', 'Technical Analysis'),
        ('fundamental', 'Fundamental Analysis'),
        ('strategy', 'Strategy Development'),
        ('psychology', 'Psychology & Risk Management'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    thumbnail_url = models.URLField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.IntegerField(help_text="Total course duration in minutes")
    order = models.IntegerField(default=0, help_text="Display order")
    
    is_published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text="Requires Premium subscription")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def lesson_count(self):
        return self.lessons.count()
    
    @property
    def completion_rate(self):
        """Calculate average completion rate across all users"""
        total_users = UserProgress.objects.filter(lesson__course=self).values('user').distinct().count()
        if total_users == 0:
            return 0
        completed_users = UserProgress.objects.filter(
            lesson__course=self,
            completed=True
        ).values('user').distinct().count()
        return (completed_users / total_users) * 100


class Lesson(models.Model):
    """Individual lessons within a course"""
    
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video Tutorial'),
        ('text', 'Text Content'),
        ('interactive', 'Interactive Demo'),
        ('mixed', 'Mixed Content'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    
    # Content
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(help_text="Markdown formatted content")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo URL")
    
    # Interactive components (stored as JSON)
    interactive_demo = models.JSONField(
        blank=True,
        null=True,
        help_text="Chart examples, interactive widgets configuration"
    )
    
    # Quiz questions (stored as JSON)
    quiz_questions = models.JSONField(
        blank=True,
        null=True,
        help_text="""
        Format: [
            {
                "question": "What is RSI?",
                "options": ["A", "B", "C", "D"],
                "correct": 0,
                "explanation": "..."
            }
        ]
        """
    )
    
    # Metadata
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(help_text="Estimated completion time")
    
    # Key takeaways
    key_takeaways = models.JSONField(
        blank=True,
        null=True,
        help_text="List of 3-5 key points from lesson"
    )
    
    # Related resources
    related_terms = models.ManyToManyField('GlossaryTerm', blank=True)
    
    is_published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def completion_rate(self):
        """Calculate completion rate for this lesson"""
        total_started = UserProgress.objects.filter(lesson=self).count()
        if total_started == 0:
            return 0
        completed = UserProgress.objects.filter(lesson=self, completed=True).count()
        return (completed / total_started) * 100
    
    @property
    def average_quiz_score(self):
        """Calculate average quiz score for this lesson"""
        scores = UserProgress.objects.filter(
            lesson=self,
            quiz_score__isnull=False
        ).values_list('quiz_score', flat=True)
        
        if not scores:
            return None
        return sum(scores) / len(scores)


class UserProgress(models.Model):
    """Track user progress through lessons"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress tracking
    completed = models.BooleanField(default=False)
    quiz_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    time_spent_seconds = models.IntegerField(default=0, help_text="Time spent on lesson in seconds")
    
    # Quiz attempts
    quiz_attempts = models.IntegerField(default=0)
    quiz_answers = models.JSONField(blank=True, null=True, help_text="User's quiz answers")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress Records'
        ordering = ['-last_accessed']
    
    def __str__(self):
        status = "✓" if self.completed else "⏳"
        return f"{status} {self.user.username} - {self.lesson.title}"
    
    @property
    def progress_percentage(self):
        """Calculate progress based on time spent vs estimated duration"""
        if self.completed:
            return 100
        estimated_seconds = self.lesson.duration_minutes * 60
        if estimated_seconds == 0:
            return 0
        return min(100, int((self.time_spent_seconds / estimated_seconds) * 100))


class CourseCertificate(models.Model):
    """Certificates awarded upon course completion"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    
    certificate_id = models.CharField(max_length=100, unique=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Performance metrics
    completion_time_hours = models.DecimalField(max_digits=6, decimal_places=2)
    average_quiz_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} Certificate"
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            import uuid
            self.certificate_id = f"TSP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class GlossaryTerm(models.Model):
    """Trading terminology glossary"""
    
    CATEGORY_CHOICES = [
        ('technical', 'Technical Analysis'),
        ('fundamental', 'Fundamental Analysis'),
        ('order_types', 'Order Types'),
        ('market_structure', 'Market Structure'),
        ('risk_management', 'Risk Management'),
        ('psychology', 'Trading Psychology'),
        ('options', 'Options & Derivatives'),
        ('general', 'General Trading'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    term = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Content
    definition = models.TextField(help_text="Clear, concise definition")
    example = models.TextField(blank=True, help_text="Practical example or usage")
    
    # Metadata
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    related_terms = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    tooltip_hover_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['term']
        verbose_name = 'Glossary Term'
        verbose_name_plural = 'Glossary Terms'
    
    def __str__(self):
        return self.term
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.term)
        super().save(*args, **kwargs)


class UserLearningStreak(models.Model):
    """Track user learning streaks for gamification"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_streak')
    
    current_streak = models.IntegerField(default=0, help_text="Current consecutive days")
    longest_streak = models.IntegerField(default=0, help_text="Longest streak ever")
    last_activity_date = models.DateField(null=True, blank=True)
    
    total_lessons_completed = models.IntegerField(default=0)
    total_time_spent_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Learning Streak'
        verbose_name_plural = 'Learning Streaks'
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"
