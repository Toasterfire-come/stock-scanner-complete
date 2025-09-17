"""
News Personalization Service - Intelligent news curation based on user interests and holdings.
Handles automatic news categorization, stock ticker extraction, relevance scoring algorithm,
user preference management, and consumption analytics.
"""

import re
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Set
from django.db import transaction
from django.db.models import Q, Count, Avg, F
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import (
    Stock, UserInterests, PersonalizedNews, UserPortfolio, 
    UserWatchlist, StockAlert
)
from news.models import NewsArticle

logger = logging.getLogger(__name__)

class NewsPersonalizationService:
    """Intelligent news curation service"""
    
    # Stock ticker regex patterns
    TICKER_PATTERNS = [
        r'\b([A-Z]{1,5})\b',  # Basic ticker pattern
        r'\$([A-Z]{1,5})\b',  # Ticker with $ prefix
        r'\b([A-Z]{1,5})\.(?:NYSE|NASDAQ|AMEX)\b',  # Ticker with exchange
        r'NYSE:\s*([A-Z]{1,5})',  # NYSE: prefix
        r'NASDAQ:\s*([A-Z]{1,5})',  # NASDAQ: prefix
    ]
    
    # News category keywords
    CATEGORY_KEYWORDS = {
        'earnings': [
            'earnings', 'quarterly results', 'revenue', 'eps', 'guidance', 
            'profit', 'loss', 'beats estimates', 'misses estimates',
            'q1', 'q2', 'q3', 'q4', 'quarterly'
        ],
        'analyst': [
            'analyst', 'rating', 'upgrade', 'downgrade', 'price target',
            'buy rating', 'sell rating', 'hold rating', 'overweight',
            'underweight', 'outperform', 'underperform', 'neutral'
        ],
        'insider': [
            'insider trading', 'insider buying', 'insider selling',
            'director', 'ceo', 'cfo', 'executive', 'officer',
            'form 4', 'sec filing', 'stock purchase', 'stock sale'
        ],
        'merger': [
            'merger', 'acquisition', 'takeover', 'buyout', 'deal',
            'acquired', 'merging', 'combining', 'joint venture',
            'strategic partnership', 'consolidation'
        ],
        'ipo': [
            'ipo', 'initial public offering', 'going public', 'debut',
            'first trading day', 'public offering', 'listing'
        ],
        'dividend': [
            'dividend', 'dividend yield', 'ex-dividend', 'dividend cut',
            'dividend increase', 'dividend payment', 'special dividend',
            'quarterly dividend', 'annual dividend'
        ],
        'guidance': [
            'guidance', 'forecast', 'outlook', 'projection', 'expects',
            'anticipates', 'targets', 'revised guidance', 'full year'
        ],
        'partnership': [
            'partnership', 'collaboration', 'alliance', 'joint venture',
            'strategic partnership', 'cooperation', 'agreement'
        ],
        'regulation': [
            'regulation', 'regulatory', 'sec', 'fda approval', 'compliance',
            'investigation', 'lawsuit', 'legal', 'court', 'settlement'
        ]
    }
    
    # Common non-ticker words to exclude
    EXCLUDE_WORDS = {
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN',
        'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM',
        'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO',
        'BOY', 'DID', 'HIS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE',
        'WAY', 'WHY', 'ASK', 'BIG', 'EAR', 'END', 'FAR', 'FUN', 'GOT',
        'LAW', 'MAN', 'OWN', 'RUN', 'SUN', 'TOP', 'TRY', 'WIN', 'YES',
        'AGO', 'BAD', 'BAG', 'BED', 'BOX', 'BUY', 'CAR', 'CAT', 'CUP',
        'DOG', 'EAT', 'EGG', 'EYE', 'FEW', 'FLY', 'GUN', 'HAD', 'HAT',
        'JOB', 'LEG', 'LOT', 'MAP', 'RED', 'SEA', 'SIT', 'SIX', 'TEN',
        'USA', 'CEO', 'CFO', 'CTO', 'COO', 'API', 'APP', 'WEB', 'NET',
        'PAY', 'TAX', 'LAW', 'WAR', 'OIL', 'GAS', 'GDP', 'CPI', 'ETF'
    }
    
    @staticmethod
    def setup_user_interests(user: User, followed_stocks: List[str] = None,
                           followed_sectors: List[str] = None,
                           preferred_categories: List[str] = None,
                           news_frequency: str = 'daily') -> UserInterests:
        """
        Setup or update user interests for news personalization.
        
        Args:
            user: User to setup interests for
            followed_stocks: List of stock tickers to follow
            followed_sectors: List of sectors to follow  
            preferred_categories: List of preferred news categories
            news_frequency: Frequency of news delivery
            
        Returns:
            UserInterests: Created or updated interests instance
        """
        try:
            with transaction.atomic():
                interests, created = UserInterests.objects.get_or_create(
                    user=user,
                    defaults={
                        'followed_stocks': followed_stocks or [],
                        'followed_sectors': followed_sectors or [],
                        'preferred_categories': preferred_categories or [],
                        'news_frequency': news_frequency
                    }
                )
                
                if not created:
                    # Update existing interests
                    if followed_stocks is not None:
                        interests.followed_stocks = followed_stocks
                    if followed_sectors is not None:
                        interests.followed_sectors = followed_sectors
                    if preferred_categories is not None:
                        interests.preferred_categories = preferred_categories
                    if news_frequency:
                        interests.news_frequency = news_frequency
                    
                    interests.save()
                
                logger.info(f"Setup interests for user {user.username}")
                return interests
                
        except Exception as e:
            logger.error(f"Error setting up interests for {user.username}: {str(e)}")
            raise ValidationError(f"Failed to setup user interests: {str(e)}")
    
    @staticmethod
    def sync_portfolio_stocks(user: User) -> None:
        """
        Automatically sync stocks from user's portfolios and watchlists to interests.
        
        Args:
            user: User to sync stocks for
        """
        try:
            # Get user interests
            interests, created = UserInterests.objects.get_or_create(
                user=user,
                defaults={'followed_stocks': [], 'followed_sectors': [], 'preferred_categories': []}
            )
            
            # Collect stocks from portfolios
            portfolio_stocks = set()
            portfolios = UserPortfolio.objects.filter(user=user)
            
            for portfolio in portfolios:
                holdings = portfolio.holdings.select_related('stock').all()
                for holding in holdings:
                    portfolio_stocks.add(holding.stock.ticker)
            
            # Collect stocks from watchlists
            watchlist_stocks = set()
            watchlists = UserWatchlist.objects.filter(user=user)
            
            for watchlist in watchlists:
                items = watchlist.items.select_related('stock').all()
                for item in items:
                    watchlist_stocks.add(item.stock.ticker)
            
            # Combine and update followed stocks
            all_stocks = portfolio_stocks.union(watchlist_stocks)
            current_followed = set(interests.followed_stocks)
            
            # Add new stocks, keep manually added ones
            updated_stocks = current_followed.union(all_stocks)
            interests.followed_stocks = list(updated_stocks)
            interests.save()
            
            logger.info(f"Synced {len(all_stocks)} stocks to interests for user {user.username}")
            
        except Exception as e:
            logger.error(f"Error syncing portfolio stocks for {user.username}: {str(e)}")
    
    @staticmethod
    def categorize_news(title: str, content: str) -> str:
        """
        Automatically categorize news article based on content.
        
        Args:
            title: News article title
            content: News article content
            
        Returns:
            str: Detected category
        """
        try:
            # Combine title and content for analysis
            text = f"{title} {content}".lower()
            
            # Score each category
            category_scores = {}
            
            for category, keywords in NewsPersonalizationService.CATEGORY_KEYWORDS.items():
                score = 0
                for keyword in keywords:
                    # Weight title matches higher
                    if keyword in title.lower():
                        score += 3
                    if keyword in content.lower():
                        score += 1
                
                category_scores[category] = score
            
            # Return category with highest score, or 'general' if no matches
            if category_scores and max(category_scores.values()) > 0:
                return max(category_scores, key=category_scores.get)
            
            return 'general'
            
        except Exception as e:
            logger.error(f"Error categorizing news: {str(e)}")
            return 'general'
    
    @staticmethod
    def extract_stock_tickers(text: str) -> List[str]:
        """
        Extract stock tickers from news content.
        
        Args:
            text: Text to extract tickers from
            
        Returns:
            List[str]: List of detected stock tickers
        """
        try:
            tickers = set()
            
            for pattern in NewsPersonalizationService.TICKER_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    ticker = match.upper().strip()
                    
                    # Validate ticker format and exclude common words
                    if (len(ticker) >= 1 and len(ticker) <= 5 and 
                        ticker.isalpha() and 
                        ticker not in NewsPersonalizationService.EXCLUDE_WORDS):
                        
                        # Verify ticker exists in our database
                        if Stock.objects.filter(ticker=ticker).exists():
                            tickers.add(ticker)
            
            return list(tickers)
            
        except Exception as e:
            logger.error(f"Error extracting stock tickers: {str(e)}")
            return []
    
    @staticmethod
    def calculate_relevance_score(user: User, title: str, content: str, 
                                category: str, related_stocks: List[str]) -> Decimal:
        """
        Calculate relevance score for a news article based on user interests.
        
        Args:
            user: User to calculate relevance for
            title: News article title
            content: News article content
            category: News category
            related_stocks: List of related stock tickers
            
        Returns:
            Decimal: Relevance score (0-100)
        """
        try:
            score = Decimal('0')
            
            # Get user interests
            try:
                interests = UserInterests.objects.get(user=user)
            except UserInterests.DoesNotExist:
                # No interests setup, return low relevance
                return Decimal('10')
            
            # Stock relevance (40 points max)
            followed_stocks = set(interests.followed_stocks)
            related_stocks_set = set(related_stocks)
            
            if followed_stocks.intersection(related_stocks_set):
                # High relevance for followed stocks
                overlap = len(followed_stocks.intersection(related_stocks_set))
                score += min(Decimal('40'), Decimal(str(overlap * 15)))
            
            # Category relevance (30 points max)
            preferred_categories = interests.preferred_categories
            if category in preferred_categories:
                score += Decimal('30')
            elif category != 'general':
                score += Decimal('10')  # Some relevance for any categorized news
            
            # Portfolio holdings relevance (20 points max)
            portfolio_tickers = set()
            portfolios = UserPortfolio.objects.filter(user=user)
            for portfolio in portfolios:
                for holding in portfolio.holdings.select_related('stock'):
                    portfolio_tickers.add(holding.stock.ticker)
            
            if portfolio_tickers.intersection(related_stocks_set):
                overlap = len(portfolio_tickers.intersection(related_stocks_set))
                score += min(Decimal('20'), Decimal(str(overlap * 10)))
            
            # Watchlist relevance (10 points max)
            watchlist_tickers = set()
            watchlists = UserWatchlist.objects.filter(user=user)
            for watchlist in watchlists:
                for item in watchlist.items.select_related('stock'):
                    watchlist_tickers.add(item.stock.ticker)
            
            if watchlist_tickers.intersection(related_stocks_set):
                overlap = len(watchlist_tickers.intersection(related_stocks_set))
                score += min(Decimal('10'), Decimal(str(overlap * 5)))
            
            # Ensure score is within bounds
            score = max(Decimal('0'), min(Decimal('100'), score))
            
            return score.quantize(Decimal('0.01'))
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {str(e)}")
            return Decimal('10')  # Default low relevance
    
    @staticmethod
    def create_personalized_news(user: User, title: str, content: str, url: str,
                               source: str, published_at: datetime) -> Optional[PersonalizedNews]:
        """
        Create a personalized news entry for a user.
        
        Args:
            user: User to create news for
            title: News article title
            content: News article content
            url: Article URL
            source: News source
            published_at: When article was published
            
        Returns:
            PersonalizedNews: Created news instance or None if not relevant
        """
        try:
            # Extract information from content
            category = NewsPersonalizationService.categorize_news(title, content)
            related_stocks = NewsPersonalizationService.extract_stock_tickers(f"{title} {content}")
            relevance_score = NewsPersonalizationService.calculate_relevance_score(
                user, title, content, category, related_stocks
            )
            
            # Only create news if relevance score is above threshold
            if relevance_score < Decimal('15'):
                return None
            
            # Check if news already exists for this user
            existing = PersonalizedNews.objects.filter(
                user=user, url=url
            ).first()
            
            if existing:
                return existing
            
            # Create personalized news entry
            news = PersonalizedNews.objects.create(
                user=user,
                title=title,
                content=content,
                url=url,
                source=source,
                relevance_score=relevance_score,
                related_stocks=related_stocks,
                category=category,
                published_at=published_at
            )
            
            logger.info(f"Created personalized news for {user.username}: {title[:50]}...")
            return news
            
        except Exception as e:
            logger.error(f"Error creating personalized news for {user.username}: {str(e)}")
            return None
    
    @staticmethod
    def get_personalized_feed(user: User, limit: int = 20, 
                            category: str = None) -> List[Dict[str, Any]]:
        """
        Get personalized news feed for a user.
        
        Args:
            user: User to get feed for
            limit: Maximum number of articles
            category: Filter by category (optional)
            
        Returns:
            List of news article dictionaries
        """
        try:
            # Start with user's personalized news
            query = PersonalizedNews.objects.filter(user=user)
            
            # Filter by category if specified
            if category:
                query = query.filter(category=category)
            
            # Order by relevance score and recency
            news_items = query.order_by('-relevance_score', '-published_at')[:limit]
            
            result = []
            # Lazy import to avoid heavy initialization if not needed
            try:
                from news.scraper import YahooFinanceNewsScraper as _YFNS
                _analyzer = _YFNS()
            except Exception:
                _analyzer = None

            for item in news_items:
                # Derive sentiment from corresponding NewsArticle if available; otherwise compute ad-hoc
                sentiment_score = None
                sentiment_grade = None
                try:
                    linked = NewsArticle.objects.filter(url=item.url).first()
                    if linked:
                        if linked.sentiment_score is not None:
                            try:
                                sentiment_score = float(linked.sentiment_score)
                            except Exception:
                                sentiment_score = None
                        sentiment_grade = linked.sentiment_grade or None
                    elif _analyzer is not None:
                        text = f"{item.title} {item.content or ''}"
                        sentiment_score = _analyzer.analyze_sentiment(text)
                        sentiment_grade = _analyzer.get_sentiment_grade(text)
                except Exception:
                    pass

                # Provide tickers alias expected by some clients
                tickers = item.related_stocks or []

                result.append({
                    'id': item.id,
                    'title': item.title,
                    'content': item.content[:500] + '...' if len(item.content) > 500 else item.content,
                    'url': item.url,
                    'source': item.source,
                    'relevance_score': float(item.relevance_score),
                    'related_stocks': item.related_stocks,
                    'tickers': tickers,
                    'sentiment_score': sentiment_score,
                    'sentiment_grade': sentiment_grade,
                    'category': item.category,
                    'published_at': item.published_at.isoformat(),
                    'read_at': item.read_at.isoformat() if item.read_at else None,
                    'clicked': item.clicked
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting personalized feed for {user.username}: {str(e)}")
            return []
    
    @staticmethod
    def mark_news_read(user: User, news_id: int) -> bool:
        """
        Mark a news article as read by the user.
        
        Args:
            user: User who read the article
            news_id: ID of the news article
            
        Returns:
            bool: True if marked successfully
        """
        try:
            news = PersonalizedNews.objects.filter(id=news_id, user=user).first()
            if news and not news.read_at:
                news.read_at = timezone.now()
                news.save()
                
                logger.info(f"Marked news {news_id} as read for {user.username}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking news as read: {str(e)}")
            return False
    
    @staticmethod
    def mark_news_clicked(user: User, news_id: int) -> bool:
        """
        Mark a news article as clicked by the user.
        
        Args:
            user: User who clicked the article
            news_id: ID of the news article
            
        Returns:
            bool: True if marked successfully
        """
        try:
            news = PersonalizedNews.objects.filter(id=news_id, user=user).first()
            if news:
                news.clicked = True
                if not news.read_at:
                    news.read_at = timezone.now()
                news.save()
                
                logger.info(f"Marked news {news_id} as clicked for {user.username}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking news as clicked: {str(e)}")
            return False
    
    @staticmethod
    def bulk_create_news_for_users(news_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Create personalized news for multiple users from a single article.
        
        Args:
            news_data: Dictionary containing title, content, url, source, published_at
            
        Returns:
            Dict with creation statistics
        """
        try:
            title = news_data['title']
            content = news_data['content']
            url = news_data['url']
            source = news_data['source']
            published_at = news_data['published_at']
            
            # Extract stocks and category once
            related_stocks = NewsPersonalizationService.extract_stock_tickers(f"{title} {content}")
            category = NewsPersonalizationService.categorize_news(title, content)
            
            # Get users who might be interested
            interested_users = User.objects.filter(
                Q(interests__followed_stocks__overlap=related_stocks) |
                Q(interests__preferred_categories__contains=category) |
                Q(portfolios__holdings__stock__ticker__in=related_stocks) |
                Q(watchlists__items__stock__ticker__in=related_stocks)
            ).distinct()
            
            created_count = 0
            skipped_count = 0
            
            for user in interested_users:
                news = NewsPersonalizationService.create_personalized_news(
                    user, title, content, url, source, published_at
                )
                
                if news:
                    created_count += 1
                else:
                    skipped_count += 1
            
            logger.info(f"Bulk created news: {created_count} created, {skipped_count} skipped")
            
            return {
                'created': created_count,
                'skipped': skipped_count,
                'total_users': interested_users.count()
            }
            
        except Exception as e:
            logger.error(f"Error bulk creating news: {str(e)}")
            return {'created': 0, 'skipped': 0, 'total_users': 0}
    
    @staticmethod
    def should_send_news_to_user(user: User) -> bool:
        """
        Check if user should receive news based on their frequency preference.
        
        Args:
            user: User to check
            
        Returns:
            bool: True if user should receive news now
        """
        try:
            interests = UserInterests.objects.filter(user=user).first()
            if not interests:
                return False
            
            frequency = interests.news_frequency
            
            # Get last news created for user
            last_news = PersonalizedNews.objects.filter(user=user).order_by('-created_at').first()
            
            if not last_news:
                return True  # First time, send news
            
            now = timezone.now()
            time_since_last = now - last_news.created_at
            
            # Check frequency
            if frequency == 'realtime':
                return True
            elif frequency == 'hourly':
                return time_since_last >= timedelta(hours=1)
            elif frequency == 'daily':
                return time_since_last >= timedelta(days=1)
            elif frequency == 'weekly':
                return time_since_last >= timedelta(weeks=1)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking news frequency for {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def cleanup_old_news(days_to_keep: int = 30) -> int:
        """
        Clean up old personalized news articles.
        
        Args:
            days_to_keep: Number of days to keep news
            
        Returns:
            int: Number of articles deleted
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_to_keep)
            deleted_count = PersonalizedNews.objects.filter(
                created_at__lt=cutoff_date
            ).delete()[0]
            
            logger.info(f"Cleaned up {deleted_count} old news articles")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old news: {str(e)}")
            return 0
    
    @staticmethod
    def get_news_analytics(user: User) -> Dict[str, Any]:
        """
        Get news consumption analytics for a user.
        
        Args:
            user: User to get analytics for
            
        Returns:
            Dict with analytics data
        """
        try:
            # Total news stats
            total_news = PersonalizedNews.objects.filter(user=user).count()
            read_news = PersonalizedNews.objects.filter(user=user, read_at__isnull=False).count()
            clicked_news = PersonalizedNews.objects.filter(user=user, clicked=True).count()
            
            # Category breakdown
            category_stats = PersonalizedNews.objects.filter(user=user).values('category').annotate(
                count=Count('id'),
                avg_relevance=Avg('relevance_score')
            ).order_by('-count')
            
            # Recent activity (last 7 days)
            week_ago = timezone.now() - timedelta(days=7)
            recent_news = PersonalizedNews.objects.filter(
                user=user, created_at__gte=week_ago
            ).count()
            recent_read = PersonalizedNews.objects.filter(
                user=user, read_at__gte=week_ago
            ).count()
            
            # Top sources
            source_stats = PersonalizedNews.objects.filter(user=user).values('source').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            return {
                'total_news': total_news,
                'read_news': read_news,
                'clicked_news': clicked_news,
                'read_rate': (read_news / total_news * 100) if total_news > 0 else 0,
                'click_rate': (clicked_news / total_news * 100) if total_news > 0 else 0,
                'recent_news_count': recent_news,
                'recent_read_count': recent_read,
                'category_breakdown': list(category_stats),
                'top_sources': list(source_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting news analytics for {user.username}: {str(e)}")
            return {}