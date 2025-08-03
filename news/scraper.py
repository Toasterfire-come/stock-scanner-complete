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
        """Extract stock tickers from text"""
        tickers = set()
        
        # Find ticker patterns
        matches = self.ticker_pattern.findall(text)
        for match in matches:
            ticker = match[0] or match[1]  # Handle both $AAPL and AAPL patterns
            if ticker and len(ticker) <= 5:
                tickers.add(ticker.upper())
        
        # Common stock words that might indicate tickers
        stock_words = ['stock', 'shares', 'trading', 'market', 'investor']
        words = text.upper().split()
        for word in words:
            if len(word) <= 5 and word.isalpha() and word not in stock_words:
                # Basic validation - could be enhanced
                tickers.add(word)
        
        return list(tickers)
    
    def analyze_sentiment(self, text: str) -> Optional[float]:
        """Basic sentiment analysis"""
        text_lower = text.lower()
        
        # Positive words
        positive_words = ['up', 'gain', 'rise', 'positive', 'bullish', 'growth', 'profit', 'earnings', 'beat', 'surge']
        # Negative words
        negative_words = ['down', 'loss', 'fall', 'negative', 'bearish', 'decline', 'miss', 'drop', 'crash']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return round(sentiment, 4)
    
    def get_sentiment_grade(self, text: str) -> str:
        """Get sentiment grade (A-F)"""
        sentiment = self.analyze_sentiment(text)
        
        if sentiment >= 0.6:
            return 'A'  # Very positive
        elif sentiment >= 0.2:
            return 'B'  # Positive
        elif sentiment >= -0.2:
            return 'C'  # Neutral
        elif sentiment >= -0.6:
            return 'D'  # Negative
        else:
            return 'F'  # Very negative
    
    def scrape_all_sources(self, limit_per_source: int = 50) -> List[Dict]:
        """Scrape news from all sources"""
        all_articles = []
        
        logger.info("Starting news scraping from all sources...")
        
        # Scrape from each source
        sources = [
            self.scrape_yahoo_finance,
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
                articles = source_func(limit_per_source)
                all_articles.extend(articles)
                logger.info(f"Scraped {len(articles)} articles from {source_func.__name__}")
                time.sleep(0.5)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error scraping {source_func.__name__}: {e}")
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles
    
    def save_to_database(self, articles: List[Dict]):
        """Save articles to Django database"""
        from django.utils import timezone
        from .models import NewsArticle, NewsSource
        
        saved_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                if NewsArticle.objects.filter(url=article_data['url']).exists():
                    continue
                
                # Get or create news source
                source, created = NewsSource.objects.get_or_create(
                    name=article_data['source'],
                    defaults={'url': 'https://example.com', 'is_active': True}
                )
                
                # Create article
                article = NewsArticle.objects.create(
                    title=article_data['title'][:500],  # Respect field limits
                    summary=article_data['summary'],
                    url=article_data['url'],
                    source=article_data['source'],
                    news_source=source,
                    published_date=article_data['published_date'],
                    published_at=article_data['published_date'],
                    sentiment_score=article_data['sentiment_score'],
                    sentiment_grade=article_data['sentiment_grade'],
                    mentioned_tickers=article_data['mentioned_tickers']
                )
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving article: {e}")
                continue
        
        logger.info(f"Saved {saved_count} new articles to database")
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
