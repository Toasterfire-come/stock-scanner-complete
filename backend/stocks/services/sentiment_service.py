"""
Sentiment Analysis Service
NLP-based sentiment analysis with multiple engines.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from stocks.models import NewsArticle, SentimentAnalysis, Stock, SentimentTimeseries


class SentimentAnalysisService:
    """
    Performs sentiment analysis on news articles using various NLP engines.
    Supports VADER, TextBlob, and financial-specific models.
    """

    @staticmethod
    def analyze_article(article_id, engine='vader', stock_id=None):
        """
        Analyze sentiment of a news article.

        Args:
            article_id: NewsArticle ID
            engine: Analysis engine ('vader', 'textblob', 'finbert')
            stock_id: Optional stock ID for stock-specific sentiment

        Returns:
            dict: {'success': bool, 'sentiment_id': int, 'sentiment_label': str, 'score': float}
        """
        try:
            article = NewsArticle.objects.get(id=article_id)
        except NewsArticle.DoesNotExist:
            return {'success': False, 'message': 'Article not found'}

        stock = None
        if stock_id:
            try:
                stock = Stock.objects.get(id=stock_id)
            except Stock.DoesNotExist:
                return {'success': False, 'message': 'Stock not found'}

        # Check if already analyzed
        existing = SentimentAnalysis.objects.filter(
            article=article,
            stock=stock,
            analysis_engine=engine
        ).first()

        if existing:
            return {
                'success': True,
                'sentiment_id': existing.id,
                'sentiment_label': existing.sentiment_label,
                'score': float(existing.sentiment_score),
                'cached': True
            }

        # Perform analysis based on engine
        if engine == 'vader':
            result = SentimentAnalysisService._analyze_vader(article, stock)
        elif engine == 'textblob':
            result = SentimentAnalysisService._analyze_textblob(article, stock)
        elif engine == 'finbert':
            result = SentimentAnalysisService._analyze_finbert(article, stock)
        else:
            return {'success': False, 'message': 'Unsupported engine'}

        if not result['success']:
            return result

        # Create sentiment analysis record
        with transaction.atomic():
            sentiment = SentimentAnalysis.objects.create(
                article=article,
                stock=stock,
                sentiment_label=result['label'],
                sentiment_score=Decimal(str(result['score'])),
                confidence=Decimal(str(result.get('confidence', 1.0))),
                positive_score=Decimal(str(result.get('positive', 0))) if result.get('positive') is not None else None,
                negative_score=Decimal(str(result.get('negative', 0))) if result.get('negative') is not None else None,
                neutral_score=Decimal(str(result.get('neutral', 0))) if result.get('neutral') is not None else None,
                analysis_engine=engine,
                engine_version=result.get('version', ''),
                key_phrases=result.get('key_phrases', []),
                entities_mentioned=result.get('entities', []),
                aspect_sentiments=result.get('aspects', {}),
            )

            # Mark article as processed
            if not article.is_processed:
                article.is_processed = True
                article.save()

        return {
            'success': True,
            'sentiment_id': sentiment.id,
            'sentiment_label': sentiment.sentiment_label,
            'score': float(sentiment.sentiment_score),
            'cached': False
        }

    @staticmethod
    def _analyze_vader(article, stock):
        """
        Analyze using VADER (Valence Aware Dictionary and sEntiment Reasoner).
        Best for social media and general text.
        """
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            import nltk

            # Ensure VADER lexicon is downloaded
            try:
                nltk.data.find('sentiment/vader_lexicon.zip')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)

            sia = SentimentIntensityAnalyzer()

            # Analyze title and summary
            text = f"{article.title} {article.summary}"
            scores = sia.polarity_scores(text)

            # Compound score: -1 (negative) to +1 (positive)
            compound = scores['compound']

            # Determine label
            if compound >= 0.5:
                label = 'very_positive'
            elif compound >= 0.05:
                label = 'positive'
            elif compound <= -0.5:
                label = 'very_negative'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'

            return {
                'success': True,
                'score': compound,
                'label': label,
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'confidence': abs(compound),  # Use absolute value as confidence
                'version': 'nltk-vader-3.8'
            }

        except ImportError:
            return {'success': False, 'message': 'NLTK not installed (pip install nltk)'}
        except Exception as e:
            return {'success': False, 'message': f'VADER error: {str(e)}'}

    @staticmethod
    def _analyze_textblob(article, stock):
        """
        Analyze using TextBlob.
        Simple pattern-based sentiment analysis.
        """
        try:
            from textblob import TextBlob

            text = f"{article.title} {article.summary}"
            blob = TextBlob(text)

            # Polarity: -1 (negative) to +1 (positive)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Determine label
            if polarity >= 0.5:
                label = 'very_positive'
            elif polarity >= 0.1:
                label = 'positive'
            elif polarity <= -0.5:
                label = 'very_negative'
            elif polarity <= -0.1:
                label = 'negative'
            else:
                label = 'neutral'

            return {
                'success': True,
                'score': polarity,
                'label': label,
                'confidence': subjectivity,  # Higher subjectivity = more opinionated
                'version': 'textblob-0.17'
            }

        except ImportError:
            return {'success': False, 'message': 'TextBlob not installed (pip install textblob)'}
        except Exception as e:
            return {'success': False, 'message': f'TextBlob error: {str(e)}'}

    @staticmethod
    def _analyze_finbert(article, stock):
        """
        Analyze using FinBERT (Financial BERT).
        Specialized for financial news sentiment.
        """
        # Placeholder for FinBERT integration
        # Requires transformers library and FinBERT model
        # This would be a heavy dependency, so it's optional
        return {'success': False, 'message': 'FinBERT not implemented (requires transformers)'}

    @staticmethod
    def analyze_unprocessed_articles(engine='vader', limit=100):
        """
        Batch analyze unprocessed articles.

        Returns:
            dict: {'success': bool, 'processed': int, 'errors': int}
        """
        unprocessed = NewsArticle.objects.filter(is_processed=False)[:limit]

        processed = 0
        errors = 0

        for article in unprocessed:
            # Analyze for each stock mentioned
            if article.stocks.exists():
                for stock in article.stocks.all():
                    result = SentimentAnalysisService.analyze_article(article.id, engine, stock.id)
                    if result['success']:
                        processed += 1
                    else:
                        errors += 1
            else:
                # Analyze without stock-specific sentiment
                result = SentimentAnalysisService.analyze_article(article.id, engine)
                if result['success']:
                    processed += 1
                else:
                    errors += 1

        return {
            'success': True,
            'processed': processed,
            'errors': errors,
            'message': f'Processed {processed} articles with {errors} errors'
        }

    @staticmethod
    def get_stock_sentiment_summary(ticker, days_back=7):
        """
        Get aggregated sentiment summary for a stock.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to aggregate

        Returns:
            dict: Sentiment summary with scores and distribution
        """
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return {'success': False, 'message': 'Stock not found'}

        cutoff = timezone.now() - timedelta(days=days_back)

        sentiments = SentimentAnalysis.objects.filter(
            stock=stock,
            analyzed_at__gte=cutoff
        )

        if not sentiments.exists():
            return {
                'success': True,
                'ticker': ticker,
                'no_data': True,
                'message': 'No sentiment data available'
            }

        # Calculate aggregates
        total = sentiments.count()
        avg_score = sentiments.aggregate(models.Avg('sentiment_score'))['sentiment_score__avg']

        # Distribution
        very_positive = sentiments.filter(sentiment_label='very_positive').count()
        positive = sentiments.filter(sentiment_label='positive').count()
        neutral = sentiments.filter(sentiment_label='neutral').count()
        negative = sentiments.filter(sentiment_label='negative').count()
        very_negative = sentiments.filter(sentiment_label='very_negative').count()

        # Trend (last 24h vs previous period)
        yesterday = timezone.now() - timedelta(days=1)
        recent_avg = sentiments.filter(analyzed_at__gte=yesterday).aggregate(
            models.Avg('sentiment_score')
        )['sentiment_score__avg']

        older_avg = sentiments.filter(analyzed_at__lt=yesterday).aggregate(
            models.Avg('sentiment_score')
        )['sentiment_score__avg']

        trend = None
        if recent_avg and older_avg:
            trend = float(recent_avg) - float(older_avg)

        return {
            'success': True,
            'ticker': ticker,
            'period_days': days_back,
            'total_articles': total,
            'avg_sentiment_score': float(avg_score) if avg_score else 0,
            'distribution': {
                'very_positive': very_positive,
                'positive': positive,
                'neutral': neutral,
                'negative': negative,
                'very_negative': very_negative,
            },
            'sentiment_trend': trend,
            'overall_sentiment': SentimentAnalysisService._score_to_label(float(avg_score) if avg_score else 0),
        }

    @staticmethod
    def _score_to_label(score):
        """Convert numeric score to label"""
        if score >= 0.5:
            return 'very_positive'
        elif score >= 0.1:
            return 'positive'
        elif score <= -0.5:
            return 'very_negative'
        elif score <= -0.1:
            return 'negative'
        else:
            return 'neutral'

    @staticmethod
    def calculate_sentiment_timeseries(ticker, interval='1d', days_back=30):
        """
        Calculate and store sentiment timeseries data.

        Args:
            ticker: Stock ticker symbol
            interval: '1h', '4h', '1d', '1w'
            days_back: Number of days to calculate

        Returns:
            dict: {'success': bool, 'periods_created': int}
        """
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return {'success': False, 'message': 'Stock not found'}

        # Determine interval duration
        interval_hours = {
            '1h': 1,
            '4h': 4,
            '1d': 24,
            '1w': 168,
        }.get(interval, 24)

        periods_created = 0
        current_time = timezone.now()
        end_time = current_time - timedelta(days=days_back)

        while current_time > end_time:
            period_end = current_time
            period_start = current_time - timedelta(hours=interval_hours)

            # Get sentiments in this period
            sentiments = SentimentAnalysis.objects.filter(
                stock=stock,
                analyzed_at__gte=period_start,
                analyzed_at__lt=period_end
            )

            if sentiments.exists():
                # Calculate aggregates
                total = sentiments.count()
                avg_score = sentiments.aggregate(models.Avg('sentiment_score'))['sentiment_score__avg']

                # Count by label
                positive_count = sentiments.filter(sentiment_label__in=['positive', 'very_positive']).count()
                negative_count = sentiments.filter(sentiment_label__in=['negative', 'very_negative']).count()
                neutral_count = sentiments.filter(sentiment_label='neutral').count()

                # Create or update timeseries record
                SentimentTimeseries.objects.update_or_create(
                    stock=stock,
                    interval=interval,
                    period_start=period_start,
                    defaults={
                        'period_end': period_end,
                        'avg_sentiment_score': Decimal(str(avg_score)),
                        'weighted_sentiment': Decimal(str(avg_score)),  # TODO: Weight by source reliability
                        'total_articles': total,
                        'positive_articles': positive_count,
                        'negative_articles': negative_count,
                        'neutral_articles': neutral_count,
                    }
                )
                periods_created += 1

            current_time = period_start

        return {
            'success': True,
            'periods_created': periods_created,
            'message': f'Created {periods_created} timeseries periods for {ticker}'
        }


# Import Django models for aggregation
from django.db import models
