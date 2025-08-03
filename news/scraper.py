"""
Financial News Scraper
Pulls news from multiple sources including Yahoo Finance, Reuters, Bloomberg, and more
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional
import json
from urllib.parse import urljoin, urlparse
import yfinance as yf
from django.utils import timezone

logger = logging.getLogger(__name__)

class NewsScraper:
    """Main news scraper class"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # News sources with more feeds
        self.sources = {
            'yahoo_finance': {
                'name': 'Yahoo Finance',
                'url': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'type': 'rss'
            },
            'yahoo_finance_latest': {
                'name': 'Yahoo Finance Latest News',
                'url': 'https://finance.yahoo.com/topic/latest-news/',
                'type': 'web'
            },
            'yahoo_finance_earnings': {
                'name': 'Yahoo Finance Earnings',
                'url': 'https://finance.yahoo.com/topic/earnings/',
                'type': 'web'
            },
            'yahoo_finance_market': {
                'name': 'Yahoo Finance Market',
                'url': 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^DJI,^IXIC',
                'type': 'rss'
            },
            'reuters': {
                'name': 'Reuters',
                'url': 'https://feeds.reuters.com/reuters/businessNews',
                'type': 'rss'
            },
            'reuters_markets': {
                'name': 'Reuters Markets',
                'url': 'https://feeds.reuters.com/reuters/markets',
                'type': 'rss'
            },
            'marketwatch': {
                'name': 'MarketWatch',
                'url': 'https://feeds.marketwatch.com/marketwatch/marketpulse/',
                'type': 'rss'
            },
            'marketwatch_top': {
                'name': 'MarketWatch Top',
                'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
                'type': 'rss'
            },
            'cnbc': {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
                'type': 'rss'
            },
            'cnbc_markets': {
                'name': 'CNBC Markets',
                'url': 'https://www.cnbc.com/id/100006149/device/rss/rss.html',
                'type': 'rss'
            },
            'seeking_alpha': {
                'name': 'Seeking Alpha',
                'url': 'https://seekingalpha.com/feed.xml',
                'type': 'rss'
            },
            'investing': {
                'name': 'Investing.com',
                'url': 'https://www.investing.com/rss/news_301.rss',
                'type': 'rss'
            }
        }
        
        # Stock ticker patterns
        self.ticker_pattern = re.compile(r'\$([A-Z]{1,5})|([A-Z]{1,5})')
        
    def scrape_yahoo_finance(self, limit: int = 100) -> List[Dict]:
        """Scrape news from Yahoo Finance"""
        articles = []
        
        try:
            # Yahoo Finance RSS feed
            feed_url = "https://feeds.finance.yahoo.com/rss/2.0/headline"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    # Extract tickers from title and description
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Yahoo Finance',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Yahoo Finance article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance: {e}")
            
        return articles
    
    def scrape_yahoo_finance_latest(self, limit: int = 100) -> List[Dict]:
        """Scrape latest news from Yahoo Finance RSS feed"""
        articles = []
        
        try:
            # Use RSS feed instead of web scraping for reliability
            feed_url = "https://feeds.finance.yahoo.com/rss/2.0/headline"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    # Extract tickers from title and description
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Yahoo Finance Latest',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Yahoo Finance Latest article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance Latest: {e}")
            
        return articles
    
    def scrape_yahoo_finance_earnings(self, limit: int = 100) -> List[Dict]:
        """Scrape earnings news from Yahoo Finance RSS feed"""
        articles = []
        
        try:
            # Use earnings-focused RSS feed
            feed_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=earnings"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    # Extract tickers from title and description
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Yahoo Finance Earnings',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Yahoo Finance Earnings article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance Earnings: {e}")
            
        return articles
    
    def scrape_yahoo_finance_market(self, limit: int = 100) -> List[Dict]:
        """Scrape market news from Yahoo Finance"""
        articles = []
        
        try:
            feed_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^DJI,^IXIC"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Yahoo Finance Market',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Yahoo Finance Market article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance Market: {e}")
            
        return articles
    
    def scrape_reuters(self, limit: int = 100) -> List[Dict]:
        """Scrape news from Reuters"""
        articles = []
        
        try:
            feed_url = "https://feeds.reuters.com/reuters/businessNews"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Reuters',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Reuters article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Reuters: {e}")
            
        return articles
    
    def scrape_reuters_markets(self, limit: int = 100) -> List[Dict]:
        """Scrape market news from Reuters"""
        articles = []
        
        try:
            feed_url = "https://feeds.reuters.com/reuters/markets"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Reuters Markets',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Reuters Markets article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Reuters Markets: {e}")
            
        return articles
    
    def scrape_marketwatch(self, limit: int = 100) -> List[Dict]:
        """Scrape news from MarketWatch"""
        articles = []
        
        try:
            feed_url = "https://feeds.marketwatch.com/marketwatch/marketpulse/"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'MarketWatch',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing MarketWatch article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping MarketWatch: {e}")
            
        return articles
    
    def scrape_marketwatch_top(self, limit: int = 100) -> List[Dict]:
        """Scrape top stories from MarketWatch"""
        articles = []
        
        try:
            feed_url = "https://feeds.marketwatch.com/marketwatch/topstories/"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'MarketWatch Top',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing MarketWatch Top article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping MarketWatch Top: {e}")
            
        return articles
    
    def scrape_cnbc(self, limit: int = 100) -> List[Dict]:
        """Scrape news from CNBC"""
        articles = []
        
        try:
            feed_url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'CNBC',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing CNBC article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping CNBC: {e}")
            
        return articles
    
    def scrape_cnbc_markets(self, limit: int = 100) -> List[Dict]:
        """Scrape market news from CNBC"""
        articles = []
        
        try:
            feed_url = "https://www.cnbc.com/id/100006149/device/rss/rss.html"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'CNBC Markets',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing CNBC Markets article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping CNBC Markets: {e}")
            
        return articles
    
    def scrape_seeking_alpha(self, limit: int = 100) -> List[Dict]:
        """Scrape news from Seeking Alpha"""
        articles = []
        
        try:
            feed_url = "https://seekingalpha.com/feed.xml"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Seeking Alpha',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Seeking Alpha article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Seeking Alpha: {e}")
            
        return articles
    
    def scrape_investing(self, limit: int = 100) -> List[Dict]:
        """Scrape news from Investing.com"""
        articles = []
        
        try:
            feed_url = "https://www.investing.com/rss/news_301.rss"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                try:
                    text = f"{entry.title} {entry.description}"
                    tickers = self.extract_tickers(text)
                    
                    article = {
                        'title': entry.title,
                        'summary': entry.description,
                        'url': entry.link,
                        'source': 'Investing.com',
                        'published_date': timezone.now(),
                        'mentioned_tickers': ','.join(tickers) if tickers else '',
                        'sentiment_score': self.analyze_sentiment(entry.title + ' ' + entry.description),
                        'sentiment_grade': self.get_sentiment_grade(entry.title + ' ' + entry.description)
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing Investing.com article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Investing.com: {e}")
            
        return articles
    
    def scrape_yfinance_news(self, limit: int = 100) -> List[Dict]:
        """Scrape news using yfinance for major stocks"""
        articles = []
        
        # Major stock tickers to get news for
        major_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'XOM', 'PFE', 'ABT', 'KO']
        
        for ticker in major_tickers[:10]:  # Limit to first 10 to avoid too many requests
            try:
                stock = yf.Ticker(ticker)
                news = stock.news
                
                for item in news[:limit//len(major_tickers)]:
                    try:
                        text = f"{item.get('title', '')} {item.get('summary', '')}"
                        tickers = self.extract_tickers(text)
                        
                        article = {
                            'title': item.get('title', ''),
                            'summary': item.get('summary', ''),
                            'url': item.get('link', ''),
                            'source': f'YFinance {ticker}',
                            'published_date': timezone.now(),
                            'mentioned_tickers': ','.join(tickers) if tickers else ticker,
                            'sentiment_score': self.analyze_sentiment(text),
                            'sentiment_grade': self.get_sentiment_grade(text)
                        }
                        articles.append(article)
                        
                    except Exception as e:
                        logger.error(f"Error processing yfinance news for {ticker}: {e}")
                        continue
                        
                time.sleep(0.5)  # Be respectful to yfinance
                
            except Exception as e:
                logger.error(f"Error getting yfinance news for {ticker}: {e}")
                continue
                
        return articles
    
    def extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text with enhanced detection"""
        tickers = set()
        
        # Enhanced ticker patterns
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
                    # Filter out common words that aren't tickers
                    if ticker not in ['THE', 'AND', 'FOR', 'ARE', 'YOU', 'ALL', 'NEW', 'TOP', 'CEO', 'CFO', 'CTO']:
                        tickers.add(ticker.upper())
        
        # Major stock tickers to look for specifically
        major_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'JPM', 'JNJ',
            'V', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'XOM', 'PFE', 'ABT', 'KO', 'PEP', 'TMO',
            'COST', 'AVGO', 'MRK', 'WMT', 'ACN', 'DHR', 'NEE', 'LLY', 'UNP', 'RTX', 'HON',
            'QCOM', 'LMT', 'BMY', 'TXN', 'AMGN', 'PM', 'ORCL', 'ADBE', 'CRM', 'NFLX', 'PYPL'
        ]
        
        # Check for major tickers in text
        text_upper = text.upper()
        for ticker in major_tickers:
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
            'stock split', 'buyback', 'acquisition', 'merger', 'partnership'
        ]
        
        # Moderate positive indicators (B grade)
        moderate_positive = [
            'up', 'gain', 'rise', 'positive', 'growth', 'profit', 'earnings', 'revenue',
            'improve', 'better', 'strong', 'solid', 'stable', 'recovery', 'bounce',
            'optimistic', 'favorable', 'support', 'buy', 'hold', 'outperform'
        ]
        
        # Neutral indicators (C grade)
        neutral_words = [
            'maintain', 'stable', 'steady', 'unchanged', 'hold', 'neutral', 'mixed',
            'balance', 'maintain', 'consistent', 'flat', 'sideways'
        ]
        
        # Moderate negative indicators (D grade)
        moderate_negative = [
            'down', 'fall', 'decline', 'drop', 'negative', 'weak', 'lower', 'reduce',
            'decrease', 'loss', 'miss', 'disappoint', 'concern', 'risk', 'sell',
            'underperform', 'downgrade', 'cut', 'reduce'
        ]
        
        # Strong negative indicators (F grade)
        strong_negative = [
            'crash', 'plunge', 'collapse', 'bearish', 'breakdown', 'record low',
            'earnings miss', 'revenue miss', 'guidance cut', 'downgrade', 'sell rating',
            'negative outlook', 'weak growth', 'loss increase', 'dividend cut',
            'bankruptcy', 'delisting', 'fraud', 'scandal', 'investigation'
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
    
    def scrape_all_sources(self, limit_per_source: int = 50) -> List[Dict]:
        """Scrape news from all sources"""
        all_articles = []
        
        logger.info("Starting news scraping from all sources...")
        
        # Scrape from each source
        sources = [
            self.scrape_yahoo_finance,
            self.scrape_yahoo_finance_latest,
            self.scrape_yahoo_finance_earnings,
            self.scrape_yahoo_finance_market,
            self.scrape_reuters,
            self.scrape_reuters_markets,
            self.scrape_marketwatch,
            self.scrape_marketwatch_top,
            self.scrape_cnbc,
            self.scrape_cnbc_markets,
            self.scrape_seeking_alpha,
            self.scrape_investing,
            self.scrape_yfinance_news
        ]
        
        for source_func in sources:
            try:
                logger.info(f"Starting to scrape from {source_func.__name__}...")
                articles = source_func(limit_per_source)
                all_articles.extend(articles)
                logger.info(f"Successfully scraped {len(articles)} articles from {source_func.__name__}")
                time.sleep(0.5)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error scraping {source_func.__name__}: {e}")
                continue
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles
    
    def save_to_database(self, articles: List[Dict]):
        """Save articles to Django database"""
        from django.utils import timezone
        from .models import NewsArticle, NewsSource
        
        saved_count = 0
        skipped_count = 0
        error_count = 0
        
        logger.info(f"Attempting to save {len(articles)} articles to database...")
        
        for i, article_data in enumerate(articles):
            try:
                # Validate required fields
                if not article_data.get('title') or not article_data.get('url'):
                    logger.warning(f"Skipping article {i}: Missing title or URL")
                    skipped_count += 1
                    continue
                
                # Check if article already exists
                if NewsArticle.objects.filter(url=article_data['url']).exists():
                    skipped_count += 1
                    continue
                
                # Get or create news source
                source, created = NewsSource.objects.get_or_create(
                    name=article_data['source'],
                    defaults={'url': 'https://example.com', 'is_active': True}
                )
                
                # Ensure sentiment_score is a valid Decimal
                sentiment_score = article_data.get('sentiment_score')
                if sentiment_score is not None:
                    try:
                        from decimal import Decimal
                        sentiment_score = Decimal(str(sentiment_score))
                    except:
                        sentiment_score = None
                
                # Create article
                article = NewsArticle.objects.create(
                    title=article_data['title'][:500],  # Respect field limits
                    summary=article_data.get('summary', '')[:1000],  # Limit summary length
                    url=article_data['url'],
                    source=article_data['source'],
                    news_source=source,
                    published_date=article_data['published_date'],
                    published_at=article_data['published_date'],
                    sentiment_score=sentiment_score,
                    sentiment_grade=article_data.get('sentiment_grade', 'C'),
                    mentioned_tickers=article_data.get('mentioned_tickers', '')[:500]  # Limit ticker length
                )
                
                saved_count += 1
                if saved_count % 10 == 0:
                    logger.info(f"Saved {saved_count} articles so far...")
                
            except Exception as e:
                logger.error(f"Error saving article {i}: {e}")
                logger.error(f"Article data: {article_data}")
                error_count += 1
                continue
        
        logger.info(f"Database save complete: {saved_count} saved, {skipped_count} skipped, {error_count} errors")
        return saved_count

def run_news_scraper():
    """Main function to run the news scraper"""
    scraper = NewsScraper()
    
    # Scrape articles
    articles = scraper.scrape_all_sources(limit_per_source=50)
    
    # Save to database
    saved_count = scraper.save_to_database(articles)
    
    print(f"News scraping completed!")
    print(f"Articles scraped: {len(articles)}")
    print(f"Articles saved: {saved_count}")
    
    return saved_count

if __name__ == "__main__":
    run_news_scraper()
