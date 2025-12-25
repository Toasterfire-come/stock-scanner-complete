"""
Education Service
Handles learning path management, progress tracking, and content delivery.
"""

from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from stocks.models import (
    LearningPath, Lesson, UserLessonProgress,
    IndicatorExplanation, FeatureWalkthrough,
    UserWalkthroughProgress, KnowledgeBaseArticle, UserKBFeedback
)


class EducationService:
    """Service for managing learning paths and educational content."""

    @staticmethod
    def get_recommended_paths(user):
        """
        Get recommended learning paths for a user based on their progress and skill level.

        Returns:
            dict: {'success': bool, 'paths': list}
        """
        # Get user's completed lessons
        completed_lessons = UserLessonProgress.objects.filter(
            user=user,
            is_completed=True
        ).values_list('lesson__learning_path__difficulty', flat=True)

        # Determine user's skill level
        if not completed_lessons:
            skill_level = 'beginner'
        else:
            # Check difficulty distribution
            difficulty_counts = {}
            for diff in completed_lessons:
                difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

            if difficulty_counts.get('expert', 0) > 3:
                skill_level = 'expert'
            elif difficulty_counts.get('advanced', 0) > 3:
                skill_level = 'advanced'
            elif difficulty_counts.get('intermediate', 0) > 3:
                skill_level = 'intermediate'
            else:
                skill_level = 'beginner'

        # Get paths appropriate for skill level
        difficulty_order = ['beginner', 'intermediate', 'advanced', 'expert']
        current_index = difficulty_order.index(skill_level)
        target_difficulties = difficulty_order[current_index:current_index + 2]

        recommended = LearningPath.objects.filter(
            is_published=True,
            difficulty__in=target_difficulties
        ).exclude(
            lessons__user_progress__user=user,
            lessons__user_progress__is_completed=True
        ).distinct()[:5]

        return {
            'success': True,
            'skill_level': skill_level,
            'paths': recommended
        }

    @staticmethod
    def start_lesson(user, lesson_id):
        """
        Start or resume a lesson for a user.

        Returns:
            dict: {'success': bool, 'progress': UserLessonProgress}
        """
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return {'success': False, 'message': 'Lesson not found'}

        # Get or create progress
        progress, created = UserLessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson
        )

        if created:
            progress.started_at = timezone.now()
            progress.save()

        return {
            'success': True,
            'progress': progress,
            'created': created
        }

    @staticmethod
    def update_lesson_progress(user, lesson_id, completion_percentage, time_spent_seconds=0):
        """
        Update user's progress on a lesson.

        Returns:
            dict: {'success': bool, 'progress': UserLessonProgress, 'is_completed': bool}
        """
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            progress = UserLessonProgress.objects.get(user=user, lesson=lesson)
        except (Lesson.DoesNotExist, UserLessonProgress.DoesNotExist):
            return {'success': False, 'message': 'Lesson or progress not found'}

        # Update progress
        progress.completion_percentage = min(100, max(0, completion_percentage))
        progress.time_spent_seconds += time_spent_seconds
        progress.last_accessed_at = timezone.now()

        # Mark as completed if 100%
        if progress.completion_percentage >= 100 and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()

        progress.save()

        return {
            'success': True,
            'progress': progress,
            'is_completed': progress.is_completed
        }

    @staticmethod
    def submit_quiz(user, lesson_id, answers):
        """
        Submit quiz answers and calculate score.

        Args:
            user: User object
            lesson_id: Lesson ID
            answers: dict of {question_id: answer}

        Returns:
            dict: {'success': bool, 'score': float, 'passed': bool, 'correct_answers': dict}
        """
        try:
            lesson = Lesson.objects.get(id=lesson_id, content_type='quiz')
            progress = UserLessonProgress.objects.get(user=user, lesson=lesson)
        except (Lesson.DoesNotExist, UserLessonProgress.DoesNotExist):
            return {'success': False, 'message': 'Quiz lesson or progress not found'}

        if not lesson.quiz_questions:
            return {'success': False, 'message': 'No quiz questions available'}

        # Calculate score
        total_questions = len(lesson.quiz_questions)
        correct_count = 0
        correct_answers = {}

        for question in lesson.quiz_questions:
            question_id = question.get('id')
            correct_answer = question.get('correct_answer')
            user_answer = answers.get(str(question_id))

            is_correct = str(user_answer) == str(correct_answer)
            if is_correct:
                correct_count += 1

            correct_answers[question_id] = {
                'correct': correct_answer,
                'user_answer': user_answer,
                'is_correct': is_correct
            }

        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        passing_score = 70.0  # 70% to pass

        # Update progress
        progress.quiz_score = score
        progress.quiz_attempts += 1
        progress.quiz_answers = answers

        # Mark as completed if passed
        if score >= passing_score:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.completion_percentage = 100

        progress.save()

        return {
            'success': True,
            'score': score,
            'passed': score >= passing_score,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'passing_score': passing_score
        }

    @staticmethod
    def get_path_progress(user, path_id):
        """
        Get user's progress through a learning path.

        Returns:
            dict: {'success': bool, 'path': LearningPath, 'completion_rate': float, 'lessons': list}
        """
        try:
            path = LearningPath.objects.get(id=path_id)
        except LearningPath.DoesNotExist:
            return {'success': False, 'message': 'Learning path not found'}

        # Get all lessons in path
        lessons = path.lessons.filter(is_published=True).order_by('order')

        # Get user's progress for each lesson
        lesson_data = []
        for lesson in lessons:
            try:
                progress = UserLessonProgress.objects.get(user=user, lesson=lesson)
                lesson_data.append({
                    'lesson': lesson,
                    'progress': progress,
                    'is_completed': progress.is_completed,
                    'completion_percentage': progress.completion_percentage
                })
            except UserLessonProgress.DoesNotExist:
                lesson_data.append({
                    'lesson': lesson,
                    'progress': None,
                    'is_completed': False,
                    'completion_percentage': 0
                })

        # Calculate overall completion rate
        completion_rate = path.get_completion_rate(user)

        return {
            'success': True,
            'path': path,
            'completion_rate': completion_rate,
            'lessons': lesson_data,
            'total_lessons': lessons.count()
        }


class IndicatorService:
    """Service for managing indicator explanations and tooltips."""

    @staticmethod
    def get_indicator_tooltip(indicator_name):
        """
        Get short tooltip text for an indicator.

        Returns:
            dict: {'success': bool, 'tooltip': str, 'indicator': IndicatorExplanation}
        """
        try:
            indicator = IndicatorExplanation.objects.get(
                Q(indicator_name__iexact=indicator_name) |
                Q(full_name__iexact=indicator_name)
            )
            return {
                'success': True,
                'tooltip': indicator.short_description,
                'indicator': indicator
            }
        except IndicatorExplanation.DoesNotExist:
            return {
                'success': False,
                'message': f'No explanation found for {indicator_name}'
            }

    @staticmethod
    def get_related_indicators(indicator_name):
        """
        Get indicators related to a given indicator.

        Returns:
            dict: {'success': bool, 'related': list}
        """
        try:
            indicator = IndicatorExplanation.objects.get(indicator_name__iexact=indicator_name)
            related = indicator.related_indicators.all()
            return {
                'success': True,
                'indicator': indicator,
                'related': related
            }
        except IndicatorExplanation.DoesNotExist:
            return {'success': False, 'message': 'Indicator not found'}


class WalkthroughService:
    """Service for managing feature walkthroughs."""

    @staticmethod
    def get_active_walkthroughs(user, url_path):
        """
        Get active walkthroughs for a user on a specific page.

        Returns:
            dict: {'success': bool, 'walkthroughs': list}
        """
        # Get all active walkthroughs matching the URL
        walkthroughs = FeatureWalkthrough.objects.filter(
            is_active=True,
            target_url__icontains=url_path
        ).order_by('-priority')

        # Filter based on user tier (placeholder - would integrate with billing)
        # For now, show all walkthroughs

        # Check which ones the user has already completed/dismissed
        completed_ids = UserWalkthroughProgress.objects.filter(
            user=user,
            is_completed=True
        ).values_list('walkthrough_id', flat=True)

        dismissed_ids = UserWalkthroughProgress.objects.filter(
            user=user,
            is_dismissed=True
        ).values_list('walkthrough_id', flat=True)

        # Filter out completed/dismissed for 'on_first_visit' type
        active_for_user = []
        for wt in walkthroughs:
            if wt.trigger_type == 'on_first_visit':
                if wt.id not in completed_ids and wt.id not in dismissed_ids:
                    active_for_user.append(wt)
            else:
                active_for_user.append(wt)

        return {
            'success': True,
            'walkthroughs': active_for_user
        }

    @staticmethod
    def start_walkthrough(user, walkthrough_id):
        """
        Start a walkthrough for a user.

        Returns:
            dict: {'success': bool, 'progress': UserWalkthroughProgress}
        """
        try:
            walkthrough = FeatureWalkthrough.objects.get(id=walkthrough_id, is_active=True)
        except FeatureWalkthrough.DoesNotExist:
            return {'success': False, 'message': 'Walkthrough not found'}

        # Get or create progress
        progress, created = UserWalkthroughProgress.objects.get_or_create(
            user=user,
            walkthrough=walkthrough,
            defaults={'current_step': 0}
        )

        return {
            'success': True,
            'progress': progress,
            'created': created
        }

    @staticmethod
    def update_walkthrough_step(user, walkthrough_id, step_number):
        """
        Update user's current step in a walkthrough.

        Returns:
            dict: {'success': bool, 'progress': UserWalkthroughProgress, 'is_completed': bool}
        """
        try:
            walkthrough = FeatureWalkthrough.objects.get(id=walkthrough_id)
            progress = UserWalkthroughProgress.objects.get(user=user, walkthrough=walkthrough)
        except (FeatureWalkthrough.DoesNotExist, UserWalkthroughProgress.DoesNotExist):
            return {'success': False, 'message': 'Walkthrough or progress not found'}

        progress.current_step = step_number

        # Check if completed (reached last step)
        total_steps = len(walkthrough.steps)
        if step_number >= total_steps - 1:
            progress.is_completed = True
            progress.completed_at = timezone.now()

        progress.save()

        return {
            'success': True,
            'progress': progress,
            'is_completed': progress.is_completed
        }

    @staticmethod
    def dismiss_walkthrough(user, walkthrough_id):
        """
        Mark a walkthrough as dismissed by the user.

        Returns:
            dict: {'success': bool, 'progress': UserWalkthroughProgress}
        """
        try:
            walkthrough = FeatureWalkthrough.objects.get(id=walkthrough_id)
            progress = UserWalkthroughProgress.objects.get(user=user, walkthrough=walkthrough)
        except (FeatureWalkthrough.DoesNotExist, UserWalkthroughProgress.DoesNotExist):
            return {'success': False, 'message': 'Walkthrough or progress not found'}

        progress.is_dismissed = True
        progress.dismissed_at = timezone.now()
        progress.save()

        return {
            'success': True,
            'progress': progress
        }


class KnowledgeBaseService:
    """Service for managing knowledge base articles and search."""

    @staticmethod
    def search_articles(query, category=None, article_type=None, limit=20):
        """
        Search knowledge base articles.

        Returns:
            dict: {'success': bool, 'articles': list, 'count': int}
        """
        articles = KnowledgeBaseArticle.objects.filter(is_published=True)

        # Apply filters
        if category:
            articles = articles.filter(category=category)

        if article_type:
            articles = articles.filter(article_type=article_type)

        # Search in title, summary, content, keywords
        if query:
            articles = articles.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(content__icontains=query) |
                Q(search_keywords__icontains=query) |
                Q(tags__contains=[query])
            )

        # Order by relevance (featured first, then view count)
        articles = articles.order_by('-is_featured', '-view_count')[:limit]

        return {
            'success': True,
            'articles': articles,
            'count': articles.count(),
            'query': query
        }

    @staticmethod
    def get_popular_articles(limit=10):
        """
        Get most popular/viewed articles.

        Returns:
            dict: {'success': bool, 'articles': list}
        """
        articles = KnowledgeBaseArticle.objects.filter(
            is_published=True
        ).order_by('-view_count')[:limit]

        return {
            'success': True,
            'articles': articles
        }

    @staticmethod
    def get_helpful_articles(limit=10):
        """
        Get most helpful articles based on user feedback.

        Returns:
            dict: {'success': bool, 'articles': list}
        """
        # Calculate helpfulness score
        articles = KnowledgeBaseArticle.objects.filter(
            is_published=True
        ).annotate(
            total_feedback=Count('feedback')
        ).filter(
            total_feedback__gt=0
        )

        # Sort by helpfulness ratio
        article_scores = []
        for article in articles:
            if article.helpful_count + article.not_helpful_count > 0:
                ratio = article.helpful_count / (article.helpful_count + article.not_helpful_count)
                article_scores.append((article, ratio))

        # Sort by ratio
        article_scores.sort(key=lambda x: x[1], reverse=True)
        top_articles = [a[0] for a in article_scores[:limit]]

        return {
            'success': True,
            'articles': top_articles
        }

    @staticmethod
    def record_article_view(article_id):
        """
        Increment view count for an article.

        Returns:
            dict: {'success': bool}
        """
        try:
            article = KnowledgeBaseArticle.objects.get(id=article_id)
            article.view_count += 1
            article.save(update_fields=['view_count'])
            return {'success': True}
        except KnowledgeBaseArticle.DoesNotExist:
            return {'success': False, 'message': 'Article not found'}

    @staticmethod
    def submit_feedback(user, article_id, was_helpful, comment=''):
        """
        Submit user feedback on an article.

        Returns:
            dict: {'success': bool, 'feedback': UserKBFeedback}
        """
        try:
            article = KnowledgeBaseArticle.objects.get(id=article_id)
        except KnowledgeBaseArticle.DoesNotExist:
            return {'success': False, 'message': 'Article not found'}

        # Create or update feedback
        feedback, created = UserKBFeedback.objects.update_or_create(
            user=user,
            article=article,
            defaults={
                'was_helpful': was_helpful,
                'comment': comment
            }
        )

        # Update article counts
        if created:
            if was_helpful:
                article.helpful_count += 1
            else:
                article.not_helpful_count += 1
        else:
            # Feedback was updated, adjust counts
            old_feedback = UserKBFeedback.objects.get(id=feedback.id)
            if old_feedback.was_helpful and not was_helpful:
                article.helpful_count -= 1
                article.not_helpful_count += 1
            elif not old_feedback.was_helpful and was_helpful:
                article.not_helpful_count -= 1
                article.helpful_count += 1

        article.save(update_fields=['helpful_count', 'not_helpful_count'])

        return {
            'success': True,
            'feedback': feedback,
            'created': created
        }
