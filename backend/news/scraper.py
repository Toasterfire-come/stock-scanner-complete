"""
Multi-source Finance News Scraper
Sources: Yahoo Finance, Reuters, CNBC, MarketWatch, Financial Times
Ensures: >=200 unique articles, tickers extracted, link included, de-duplicated
"""

import requests
import feedparser
import time
import logging
import re
import decimal
from typing import List, Dict, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFinanceNewsScraper:
    """Multi-source news scraper (still named for compatibility)"""
    
    def __init__(self):
        """Initialize the scraper with headers and session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Yahoo Finance RSS feeds
        self.yahoo_feeds = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^DJI',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^IXIC',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^VIX',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^TNX',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=GC=F',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=CL=F',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=DX-Y.NYB',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^FTSE',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^N225',
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GDAXI',
        ]

        # Additional finance news RSS feeds
        self.extra_feeds = [
            # Reuters business & markets
            'https://feeds.reuters.com/reuters/businessNews',
            'https://feeds.reuters.com/reuters/USstockNews',
            'https://feeds.reuters.com/reuters/worldNews',
            # CNBC top news and markets
            'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'https://www.cnbc.com/id/15839135/device/rss/rss.html',
            # MarketWatch top stories
            'https://www.marketwatch.com/feeds/topstories',
            # Financial Times markets
            'https://www.ft.com/markets?format=rss',
        ]
        
        # Major stock tickers for detection
        self.major_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'JPM', 'JNJ',
            'V', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'XOM', 'PFE', 'ABT', 'KO', 'PEP', 'TMO',
            'COST', 'AVGO', 'MRK', 'WMT', 'ACN', 'DHR', 'NEE', 'LLY', 'UNP', 'RTX', 'HON',
            'QCOM', 'LMT', 'BMY', 'TXN', 'AMGN', 'PM', 'ORCL', 'ADBE', 'CRM', 'PYPL', 'INTC',
            'CSCO', 'VZ', 'CMCSA', 'T', 'PFE', 'ABBV', 'CVX', 'KO', 'PEP', 'TMO', 'COST',
            'AVGO', 'MRK', 'WMT', 'ACN', 'DHR', 'NEE', 'LLY', 'UNP', 'RTX', 'HON', 'QCOM',
            'LMT', 'BMY', 'TXN', 'AMGN', 'PM', 'ORCL', 'ADBE', 'CRM', 'PYPL', 'INTC', 'CSCO'
        ]
    
    def extract_tickers(self, text: str) -> List[str]:
        """Enhanced ticker extraction with major stock focus"""
        tickers = set()
        
        # Enhanced patterns
        patterns = [
            r'\$([A-Z]{1,5})',  # $AAPL
            r'\b([A-Z]{1,5})\b',  # AAPL
            r'\b([A-Z]{1,5})\.(?:TO|V|N|O|PK)\b',  # Canadian/International
            r'\b([A-Z]{1,5})\.(?:NASDAQ|NYSE|AMEX)\b',  # Exchange specific
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            for match in matches:
                ticker = match if isinstance(match, str) else match[0]
                if ticker and len(ticker) <= 5 and ticker.isalpha():
                    # Filter out common words
                    if ticker not in ['THE', 'AND', 'FOR', 'ARE', 'YOU', 'ALL', 'NEW', 'TOP', 'CEO', 'CFO', 'CTO', 'USA', 'FED', 'GDP']:
                        tickers.add(ticker.upper())
        
        # Check for major tickers specifically
        text_upper = text.upper()
        for ticker in self.major_tickers:
            if ticker in text_upper:
                tickers.add(ticker)
        
        return list(tickers)
    
    def analyze_sentiment(self, text: str) -> Optional[float]:
        """Enhanced sentiment analysis for stock price impact"""
        text_lower = text.lower()
        
        # Strong positive indicators (A grade)
        strong_positive = [
            'beat', 'surge', 'soar', 'jump', 'rally', 'bullish', 'breakout', 'record high',
            'earnings beat', 'revenue beat', 'guidance raise', 'upgrade', 'buy rating',
            'positive outlook', 'strong growth', 'profit increase', 'dividend increase',
            'stock split', 'buyback', 'acquisition', 'merger', 'partnership', 'positive',
            'strong', 'solid', 'recovery', 'bounce', 'optimistic', 'favorable', 'support'
        ]
        
        # Moderate positive indicators (B grade)
        moderate_positive = [
            'up', 'gain', 'rise', 'growth', 'profit', 'earnings', 'revenue',
            'improve', 'better', 'stable', 'recovery', 'bounce', 'buy', 'hold', 'outperform',
            'positive', 'strong', 'solid', 'stable', 'recovery', 'bounce', 'optimistic'
        ]
        
        # Neutral indicators (C grade)
        neutral_words = [
            'maintain', 'stable', 'steady', 'unchanged', 'hold', 'neutral', 'mixed',
            'balance', 'consistent', 'flat', 'sideways', 'maintain', 'report', 'announce'
        ]
        
        # Moderate negative indicators (D grade)
        moderate_negative = [
            'down', 'fall', 'decline', 'drop', 'negative', 'weak', 'lower', 'reduce',
            'decrease', 'loss', 'miss', 'disappoint', 'concern', 'risk', 'sell',
            'underperform', 'downgrade', 'cut', 'reduce', 'negative', 'weak', 'lower'
        ]
        
        # Strong negative indicators (F grade)
        strong_negative = [
            'crash', 'plunge', 'collapse', 'bearish', 'breakdown', 'record low',
            'earnings miss', 'revenue miss', 'guidance cut', 'downgrade', 'sell rating',
            'negative outlook', 'weak growth', 'loss increase', 'dividend cut',
            'bankruptcy', 'delisting', 'fraud', 'scandal', 'investigation', 'crash',
            'plunge', 'collapse', 'bearish', 'breakdown', 'record low'
        ]
        
        # Count occurrences
        strong_pos_count = sum(1 for word in strong_positive if word in text_lower)
        moderate_pos_count = sum(1 for word in moderate_positive if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        moderate_neg_count = sum(1 for word in moderate_negative if word in text_lower)
        strong_neg_count = sum(1 for word in strong_negative if word in text_lower)
        
        # Weighted scoring
        total_score = (strong_pos_count * 2) + moderate_pos_count - moderate_neg_count - (strong_neg_count * 2)
        total_words = strong_pos_count + moderate_pos_count + neutral_count + moderate_neg_count + strong_neg_count
        
        if total_words == 0:
            return 0.0
        
        # Normalize to -1 to 1 range
        sentiment = total_score / (total_words * 2)
        return round(max(-1.0, min(1.0, sentiment)), 4)
    
    def get_sentiment_grade(self, text: str) -> str:
        """Get sentiment grade (A-F) based on stock price impact"""
        sentiment = self.analyze_sentiment(text)
        
        if sentiment >= 0.4:
            return 'A'  # Strong positive - likely to boost stock price
        elif sentiment >= 0.1:
            return 'B'  # Moderate positive - good for stock price
        elif sentiment >= -0.1:
            return 'C'  # Neutral - minimal impact on stock price
        elif sentiment >= -0.4:
            return 'D'  # Moderate negative - bad for stock price
        else:
            return 'F'  # Strong negative - likely to hurt stock price
    
    def get_impact_score(self, text: str) -> int:
        """Get impact score (1-10) based on urgency and importance"""
        text_lower = text.lower()
        
        # High impact indicators
        high_impact = [
            'breaking', 'urgent', 'exclusive', 'just in', 'live', 'developing',
            'earnings', 'revenue', 'guidance', 'upgrade', 'downgrade', 'buy', 'sell',
            'merger', 'acquisition', 'bankruptcy', 'fraud', 'investigation', 'lawsuit',
            'federal', 'sec', 'regulatory', 'government', 'president', 'fed', 'federal reserve'
        ]
        
        # Medium impact indicators
        medium_impact = [
            'report', 'announce', 'release', 'update', 'change', 'plan', 'strategy',
            'expansion', 'restructuring', 'layoff', 'hire', 'appointment', 'resignation',
            'partnership', 'deal', 'agreement', 'contract', 'launch', 'product', 'service'
        ]
        
        # Count high impact words
        high_count = sum(1 for word in high_impact if word in text_lower)
        medium_count = sum(1 for word in medium_impact if word in text_lower)
        
        # Calculate impact score (1-10)
        if high_count >= 3:
            return 10
        elif high_count >= 2:
            return 9
        elif high_count >= 1:
            return 8
        elif medium_count >= 3:
            return 7
        elif medium_count >= 2:
            return 6
        elif medium_count >= 1:
            return 5
        else:
            return 4
    
    def scrape_generic_rss(self, feed_url: str, source_label: str, limit: int = 50) -> List[Dict]:
        """Scrape a generic RSS feed and extract articles with tickers and sentiment."""
        articles = []
        
        try:
            logger.info(f"Scraping RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            for i, entry in enumerate(feed.entries[:limit]):
                try:
                    # Extract basic info
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '').strip()
                    summary = (entry.get('summary') or entry.get('description') or '').strip()
                    
                    # Parse date
                    published_date = datetime.now(timezone.utc)
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    
                    # Skip if missing essential info
                    if not title or not url:
                        continue
                    
                    # Analyze sentiment and extract tickers
                    full_text = f"{title} {summary}"
                    sentiment_score = self.analyze_sentiment(full_text)
                    sentiment_grade = self.get_sentiment_grade(full_text)
                    mentioned_tickers = self.extract_tickers(full_text)
                    impact_score = self.get_impact_score(full_text)
                    
                    article = {
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'source': source_label,
                        'published_date': published_date,
                        'mentioned_tickers': ', '.join(mentioned_tickers),
                        'sentiment_score': sentiment_score,
                        'sentiment_grade': sentiment_grade,
                        'impact_score': impact_score,
                        'feed_url': feed_url
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Yahoo Finance RSS entry {i}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} articles from feed: {feed_url}")
            
        except Exception as e:
            logger.error(f"Error scraping RSS feed {feed_url}: {e}")
        
        return articles
    
    def scrape_all_yahoo_feeds(self, limit_per_feed: int = 50) -> List[Dict]:
        """Scrape Yahoo Finance RSS feeds"""
        all_articles = []
        
        logger.info(f"Starting Yahoo Finance news scraping from {len(self.yahoo_feeds)} feeds...")
        
        for feed_url in self.yahoo_feeds:
            try:
                articles = self.scrape_generic_rss(feed_url, 'Yahoo Finance', limit_per_feed)
                all_articles.extend(articles)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error scraping Yahoo Finance feed {feed_url}: {e}")
                continue
        
        # Remove duplicates based on URL
        unique_articles = []
        seen_urls = set()
        
        for article in all_articles:
            if article['url'] not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article['url'])
        
        logger.info(f"Total unique Yahoo Finance articles scraped: {len(unique_articles)}")
        return unique_articles

    def scrape_all_sources(self, limit_per_feed: int = 50, min_total: int = 200) -> List[Dict]:
        """Scrape multiple sources and return at least min_total unique articles if available."""
        combined: List[Dict] = []
        # Yahoo first
        combined.extend(self.scrape_all_yahoo_feeds(limit_per_feed))
        # Then extra feeds
        for feed_url in self.extra_feeds:
            try:
                combined.extend(self.scrape_generic_rss(feed_url, 'Reuters' if 'reuters' in feed_url else (
                    'CNBC' if 'cnbc' in feed_url else ('MarketWatch' if 'marketwatch' in feed_url else ('Financial Times' if 'ft.com' in feed_url else 'News'))
                ), limit_per_feed))
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error scraping extra feed {feed_url}: {e}")
                continue
        # Dedupe by URL
        seen = set()
        unique_articles: List[Dict] = []
        for a in combined:
            u = a.get('url')
            if not u or u in seen:
                continue
            seen.add(u)
            unique_articles.append(a)
        logger.info(f"Combined unique articles: {len(unique_articles)}")
        # Trim if massive
        if len(unique_articles) > min_total:
            return unique_articles[:max(min_total, 500)]
        return unique_articles
    
    def save_to_database(self, articles: List[Dict]) -> int:
        """Save articles to Django database"""
        from django.utils import timezone
        from .models import NewsArticle, NewsSource
        
        saved_count = 0
        skipped_count = 0
        error_count = 0
        
        logger.info(f"Attempting to save {len(articles)} Yahoo Finance articles to database...")
        
        for i, article_data in enumerate(articles):
            try:
                # Validate required fields
                if not article_data.get('title') or not article_data.get('url'):
                    logger.warning(f"Skipping Yahoo Finance article {i}: Missing title or URL")
                    skipped_count += 1
                    continue
                
                # Check if article already exists
                if NewsArticle.objects.filter(url=article_data['url']).exists():
                    skipped_count += 1
                    continue
                
                # Get or create news source
                source, created = NewsSource.objects.get_or_create(
                    name=article_data['source'],
                    defaults={'url': 'https://finance.yahoo.com', 'is_active': True}
                )
                
                # Ensure sentiment_score is a valid Decimal
                sentiment_score = article_data.get('sentiment_score')
                if sentiment_score is not None:
                    try:
                        from decimal import Decimal
                        sentiment_score = Decimal(str(sentiment_score))
                    except (ValueError, TypeError, decimal.InvalidOperation) as e:
                        logger.debug(f"Failed to convert sentiment score to Decimal: {e}")
                        sentiment_score = None
                
                # Create article
                article = NewsArticle.objects.create(
                    title=article_data['title'][:500],
                    summary=article_data.get('summary', '')[:1000],
                    url=article_data['url'],
                    source=article_data['source'],
                    news_source=source,
                    published_date=article_data['published_date'],
                    published_at=article_data['published_date'],
                    sentiment_score=sentiment_score,
                    sentiment_grade=article_data.get('sentiment_grade', 'C'),
                    mentioned_tickers=article_data.get('mentioned_tickers', '')[:500]
                )
                
                saved_count += 1
                if saved_count % 10 == 0:
                    logger.info(f"Saved {saved_count} Yahoo Finance articles so far...")
                
            except Exception as e:
                logger.error(f"Error saving Yahoo Finance article {i}: {e}")
                error_count += 1
                continue
        
        logger.info(f"Database save complete: {saved_count} saved, {skipped_count} skipped, {error_count} errors")
        return saved_count

def run_yahoo_news_scraper():
    """Run multi-source scraper and return results (kept function name for compatibility)."""
    scraper = YahooFinanceNewsScraper()
    
    # Scrape articles
    articles = scraper.scrape_all_sources(limit_per_feed=50, min_total=200)
    
    # Print results
    print(f"\n{'='*60}")
    print("YAHOO FINANCE NEWS SCRAPER RESULTS")
    print(f"{'='*60}")
    print(f"Articles scraped: {len(articles)}")
    
    # Show sentiment distribution
    grade_counts = {}
    for article in articles:
        grade = article.get('sentiment_grade', 'C')
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    print(f"\nSentiment Distribution:")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = grade_counts.get(grade, 0)
        percentage = (count / len(articles) * 100) if articles else 0
        print(f"Grade {grade}: {count} articles ({percentage:.1f}%)")
    
    # Show top articles by impact
    high_impact = [a for a in articles if a.get('impact_score', 0) >= 8]
    print(f"\nHigh Impact Articles (Score 8+): {len(high_impact)}")
    
    # Show articles with major tickers
    major_ticker_articles = [a for a in articles if any(ticker in a.get('mentioned_tickers', '') for ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])]
    print(f"Articles mentioning major stocks: {len(major_ticker_articles)}")
    
    return articles

if __name__ == "__main__":
    run_yahoo_news_scraper()
