"""
Education & Context API
Endpoints for learning paths, tooltips, walkthroughs, and knowledge base.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from stocks.models import (
    LearningPath, Lesson, UserLessonProgress,
    IndicatorExplanation, FeatureWalkthrough,
    UserWalkthroughProgress, KnowledgeBaseArticle
)
from stocks.services.education_service import (
    EducationService, IndicatorService,
    WalkthroughService, KnowledgeBaseService
)


# ==================== LEARNING PATHS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_learning_paths(request):
    """
    Get all published learning paths with filtering.

    Query params:
        - category: Filter by category
        - difficulty: Filter by difficulty level
        - required_tier: Filter by tier requirement
    """
    paths = LearningPath.objects.filter(is_published=True)

    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    required_tier = request.GET.get('required_tier')

    if category:
        paths = paths.filter(category=category)
    if difficulty:
        paths = paths.filter(difficulty=difficulty)
    if required_tier:
        paths = paths.filter(required_tier=required_tier)

    paths_data = []
    for path in paths:
        completion_rate = 0
        if request.user.is_authenticated:
            completion_rate = path.get_completion_rate(request.user)

        paths_data.append({
            'id': path.id,
            'title': path.title,
            'slug': path.slug,
            'description': path.description,
            'category': path.category,
            'difficulty': path.difficulty,
            'estimated_duration_minutes': path.estimated_duration_minutes,
            'lesson_count': path.lessons.filter(is_published=True).count(),
            'completion_rate': completion_rate,
            'is_required_for_onboarding': path.is_required_for_onboarding,
            'cover_image_url': path.cover_image_url
        })

    return Response({
        'success': True,
        'paths': paths_data,
        'total': len(paths_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommended_paths(request):
    """
    Get personalized learning path recommendations for the user.
    """
    result = EducationService.get_recommended_paths(request.user)

    paths_data = []
    for path in result['paths']:
        completion_rate = path.get_completion_rate(request.user)

        paths_data.append({
            'id': path.id,
            'title': path.title,
            'slug': path.slug,
            'description': path.description,
            'category': path.category,
            'difficulty': path.difficulty,
            'estimated_duration_minutes': path.estimated_duration_minutes,
            'lesson_count': path.lessons.filter(is_published=True).count(),
            'completion_rate': completion_rate
        })

    return Response({
        'success': True,
        'skill_level': result['skill_level'],
        'recommended_paths': paths_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_learning_path_detail(request, path_id):
    """
    Get detailed information about a learning path including all lessons.
    """
    try:
        path = LearningPath.objects.get(id=path_id, is_published=True)
    except LearningPath.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Learning path not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Get progress if authenticated
    completion_rate = 0
    lessons_data = []

    lessons = path.lessons.filter(is_published=True).order_by('order')

    for lesson in lessons:
        lesson_data = {
            'id': lesson.id,
            'title': lesson.title,
            'slug': lesson.slug,
            'description': lesson.description,
            'content_type': lesson.content_type,
            'order': lesson.order,
            'estimated_duration_minutes': lesson.estimated_duration_minutes,
            'difficulty': lesson.difficulty
        }

        if request.user.is_authenticated:
            try:
                progress = UserLessonProgress.objects.get(user=request.user, lesson=lesson)
                lesson_data['progress'] = {
                    'is_completed': progress.is_completed,
                    'completion_percentage': progress.completion_percentage,
                    'time_spent_seconds': progress.time_spent_seconds,
                    'quiz_score': float(progress.quiz_score) if progress.quiz_score else None
                }
            except UserLessonProgress.DoesNotExist:
                lesson_data['progress'] = None

        lessons_data.append(lesson_data)

    if request.user.is_authenticated:
        completion_rate = path.get_completion_rate(request.user)

    return Response({
        'success': True,
        'path': {
            'id': path.id,
            'title': path.title,
            'slug': path.slug,
            'description': path.description,
            'category': path.category,
            'difficulty': path.difficulty,
            'estimated_duration_minutes': path.estimated_duration_minutes,
            'is_required_for_onboarding': path.is_required_for_onboarding,
            'cover_image_url': path.cover_image_url,
            'completion_rate': completion_rate
        },
        'lessons': lessons_data
    })


# ==================== LESSONS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_lesson_detail(request, lesson_id):
    """
    Get detailed lesson content.
    """
    try:
        lesson = Lesson.objects.select_related('learning_path').get(id=lesson_id, is_published=True)
    except Lesson.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)

    lesson_data = {
        'id': lesson.id,
        'title': lesson.title,
        'slug': lesson.slug,
        'description': lesson.description,
        'content': lesson.content,
        'content_type': lesson.content_type,
        'video_url': lesson.video_url,
        'example_code': lesson.example_code,
        'interactive_demo_url': lesson.interactive_demo_url,
        'estimated_duration_minutes': lesson.estimated_duration_minutes,
        'difficulty': lesson.difficulty,
        'learning_path': {
            'id': lesson.learning_path.id,
            'title': lesson.learning_path.title,
            'slug': lesson.learning_path.slug
        }
    }

    # Include quiz questions if quiz type
    if lesson.content_type == 'quiz' and lesson.quiz_questions:
        # Don't include correct answers in the response
        quiz_questions = []
        for q in lesson.quiz_questions:
            quiz_questions.append({
                'id': q.get('id'),
                'question': q.get('question'),
                'options': q.get('options'),
                'type': q.get('type', 'multiple_choice')
            })
        lesson_data['quiz_questions'] = quiz_questions

    # Include exercise instructions if exercise type
    if lesson.content_type == 'exercise':
        lesson_data['exercise_instructions'] = lesson.exercise_instructions

    # Get user progress if authenticated
    if request.user.is_authenticated:
        progress_result = EducationService.start_lesson(request.user, lesson_id)
        if progress_result['success']:
            progress = progress_result['progress']
            lesson_data['progress'] = {
                'is_completed': progress.is_completed,
                'completion_percentage': progress.completion_percentage,
                'time_spent_seconds': progress.time_spent_seconds,
                'quiz_score': float(progress.quiz_score) if progress.quiz_score else None,
                'quiz_attempts': progress.quiz_attempts
            }

    return Response({
        'success': True,
        'lesson': lesson_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_lesson_progress(request, lesson_id):
    """
    Update user's progress on a lesson.

    Body:
        {
            "completion_percentage": 50,
            "time_spent_seconds": 120
        }
    """
    completion_percentage = request.data.get('completion_percentage', 0)
    time_spent_seconds = request.data.get('time_spent_seconds', 0)

    result = EducationService.update_lesson_progress(
        request.user,
        lesson_id,
        completion_percentage,
        time_spent_seconds
    )

    if result['success']:
        progress = result['progress']
        return Response({
            'success': True,
            'progress': {
                'is_completed': progress.is_completed,
                'completion_percentage': progress.completion_percentage,
                'time_spent_seconds': progress.time_spent_seconds,
                'completed_at': progress.completed_at
            },
            'is_completed': result['is_completed']
        })
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, lesson_id):
    """
    Submit quiz answers for grading.

    Body:
        {
            "answers": {
                "1": "option_a",
                "2": "option_c",
                ...
            }
        }
    """
    answers = request.data.get('answers', {})

    result = EducationService.submit_quiz(request.user, lesson_id, answers)

    if result['success']:
        return Response({
            'success': True,
            'score': result['score'],
            'passed': result['passed'],
            'correct_count': result['correct_count'],
            'total_questions': result['total_questions'],
            'passing_score': result['passing_score'],
            'correct_answers': result['correct_answers']
        })
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# ==================== INDICATOR EXPLANATIONS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_indicator_tooltip(request, indicator_name):
    """
    Get tooltip/short explanation for an indicator.
    """
    result = IndicatorService.get_indicator_tooltip(indicator_name)

    if result['success']:
        indicator = result['indicator']
        return Response({
            'success': True,
            'indicator_name': indicator.indicator_name,
            'full_name': indicator.full_name,
            'tooltip': result['tooltip'],
            'category': indicator.category
        })
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_indicator_explanation(request, indicator_name):
    """
    Get full explanation for an indicator.
    """
    try:
        indicator = IndicatorExplanation.objects.get(
            Q(indicator_name__iexact=indicator_name) |
            Q(full_name__iexact=indicator_name)
        )
    except IndicatorExplanation.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Indicator not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Get related indicators
    related = indicator.related_indicators.all()[:5]

    return Response({
        'success': True,
        'indicator': {
            'indicator_name': indicator.indicator_name,
            'full_name': indicator.full_name,
            'category': indicator.category,
            'short_description': indicator.short_description,
            'detailed_explanation': indicator.detailed_explanation,
            'how_to_use': indicator.how_to_use,
            'common_mistakes': indicator.common_mistakes,
            'formula': indicator.formula,
            'calculation_example': indicator.calculation_example,
            'default_parameters': indicator.default_parameters,
            'parameter_explanations': indicator.parameter_explanations,
            'example_chart_url': indicator.example_chart_url,
            'video_tutorial_url': indicator.video_tutorial_url
        },
        'related_indicators': [
            {
                'indicator_name': r.indicator_name,
                'full_name': r.full_name,
                'short_description': r.short_description
            }
            for r in related
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_indicators(request):
    """
    List all available indicator explanations.

    Query params:
        - category: Filter by category
    """
    indicators = IndicatorExplanation.objects.all()

    category = request.GET.get('category')
    if category:
        indicators = indicators.filter(category=category)

    indicators_data = [
        {
            'indicator_name': ind.indicator_name,
            'full_name': ind.full_name,
            'category': ind.category,
            'short_description': ind.short_description
        }
        for ind in indicators
    ]

    return Response({
        'success': True,
        'indicators': indicators_data,
        'total': len(indicators_data)
    })


# ==================== FEATURE WALKTHROUGHS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_walkthroughs(request):
    """
    Get active walkthroughs for the current page.

    Query params:
        - url_path: Current URL path
    """
    url_path = request.GET.get('url_path', '/')

    result = WalkthroughService.get_active_walkthroughs(request.user, url_path)

    walkthroughs_data = []
    for wt in result['walkthroughs']:
        walkthroughs_data.append({
            'id': wt.id,
            'feature_name': wt.feature_name,
            'title': wt.title,
            'description': wt.description,
            'steps': wt.steps,
            'trigger_type': wt.trigger_type,
            'priority': wt.priority
        })

    return Response({
        'success': True,
        'walkthroughs': walkthroughs_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_walkthrough(request, walkthrough_id):
    """
    Start a walkthrough for the user.
    """
    result = WalkthroughService.start_walkthrough(request.user, walkthrough_id)

    if result['success']:
        progress = result['progress']
        return Response({
            'success': True,
            'progress': {
                'current_step': progress.current_step,
                'is_completed': progress.is_completed,
                'started_at': progress.started_at
            },
            'created': result['created']
        })
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_walkthrough_step(request, walkthrough_id):
    """
    Update current step in a walkthrough.

    Body:
        {
            "step_number": 2
        }
    """
    step_number = request.data.get('step_number', 0)

    result = WalkthroughService.update_walkthrough_step(request.user, walkthrough_id, step_number)

    if result['success']:
        progress = result['progress']
        return Response({
            'success': True,
            'progress': {
                'current_step': progress.current_step,
                'is_completed': progress.is_completed,
                'completed_at': progress.completed_at
            },
            'is_completed': result['is_completed']
        })
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dismiss_walkthrough(request, walkthrough_id):
    """
    Dismiss a walkthrough without completing it.
    """
    result = WalkthroughService.dismiss_walkthrough(request.user, walkthrough_id)

    if result['success']:
        return Response({
            'success': True,
            'message': 'Walkthrough dismissed'
        })
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# ==================== KNOWLEDGE BASE ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def search_knowledge_base(request):
    """
    Search knowledge base articles.

    Query params:
        - q: Search query
        - category: Filter by category
        - type: Filter by article type
        - limit: Results limit (default 20)
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category')
    article_type = request.GET.get('type')
    limit = int(request.GET.get('limit', 20))

    result = KnowledgeBaseService.search_articles(query, category, article_type, limit)

    articles_data = []
    for article in result['articles']:
        articles_data.append({
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'article_type': article.article_type,
            'summary': article.summary,
            'category': article.category,
            'tags': article.tags,
            'view_count': article.view_count,
            'helpful_count': article.helpful_count,
            'is_featured': article.is_featured,
            'created_at': article.created_at
        })

    return Response({
        'success': True,
        'articles': articles_data,
        'count': result['count'],
        'query': result['query']
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_kb_article(request, slug):
    """
    Get a knowledge base article by slug.
    """
    try:
        article = KnowledgeBaseArticle.objects.get(slug=slug, is_published=True)
    except KnowledgeBaseArticle.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Article not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Record view
    KnowledgeBaseService.record_article_view(article.id)

    # Get related articles
    related = article.related_articles.filter(is_published=True)[:5]

    # Get user feedback if authenticated
    user_feedback = None
    if request.user.is_authenticated:
        try:
            from stocks.models import UserKBFeedback
            feedback = UserKBFeedback.objects.get(user=request.user, article=article)
            user_feedback = {
                'was_helpful': feedback.was_helpful,
                'comment': feedback.comment,
                'created_at': feedback.created_at
            }
        except UserKBFeedback.DoesNotExist:
            pass

    return Response({
        'success': True,
        'article': {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'article_type': article.article_type,
            'summary': article.summary,
            'content': article.content,
            'category': article.category,
            'tags': article.tags,
            'view_count': article.view_count,
            'helpful_count': article.helpful_count,
            'not_helpful_count': article.not_helpful_count,
            'is_featured': article.is_featured,
            'created_at': article.created_at,
            'updated_at': article.updated_at
        },
        'related_articles': [
            {
                'id': r.id,
                'title': r.title,
                'slug': r.slug,
                'summary': r.summary
            }
            for r in related
        ],
        'user_feedback': user_feedback
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_kb_feedback(request, article_id):
    """
    Submit feedback on a knowledge base article.

    Body:
        {
            "was_helpful": true,
            "comment": "Very helpful article!" (optional)
        }
    """
    was_helpful = request.data.get('was_helpful')
    comment = request.data.get('comment', '')

    if was_helpful is None:
        return Response({
            'success': False,
            'message': 'was_helpful field is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    result = KnowledgeBaseService.submit_feedback(request.user, article_id, was_helpful, comment)

    if result['success']:
        return Response({
            'success': True,
            'message': 'Feedback submitted',
            'created': result['created']
        })
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_popular_kb_articles(request):
    """
    Get most popular knowledge base articles.
    """
    limit = int(request.GET.get('limit', 10))
    result = KnowledgeBaseService.get_popular_articles(limit)

    articles_data = []
    for article in result['articles']:
        articles_data.append({
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'category': article.category,
            'view_count': article.view_count,
            'is_featured': article.is_featured
        })

    return Response({
        'success': True,
        'articles': articles_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_helpful_kb_articles(request):
    """
    Get most helpful knowledge base articles.
    """
    limit = int(request.GET.get('limit', 10))
    result = KnowledgeBaseService.get_helpful_articles(limit)

    articles_data = []
    for article in result['articles']:
        articles_data.append({
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'category': article.category,
            'helpful_count': article.helpful_count,
            'view_count': article.view_count
        })

    return Response({
        'success': True,
        'articles': articles_data
    })
