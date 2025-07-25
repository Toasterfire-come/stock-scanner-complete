import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(base_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import re
import logging
from urllib.parse import urljoin, urlparse
from django.utils import timezone

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    # Download required NLTK data
    nltk.download('vader_lexicon', quiet=True)
    SENTIMENT_AVAILABLE = True
except ImportError:
    logger.warning("NLTK not available. Sentiment analysis will be disabled.")
    SENTIMENT_AVAILABLE = False


def assign_grade(text):
    """Analyze sentiment and assign grade and score"""
    if not text or not SENTIMENT_AVAILABLE:
        return "N/A", 0, 0.0
    
    try:
        # Clean text
        text = text.encode('utf-8', 'ignore').decode('utf-8')
        
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(text)
        compound_score = sentiment['compound']
        
        # Assign grade based on compound score
        if compound_score >= 0.6:
            grade, score = 'A', int((compound_score + 1) * 55)
        elif 0.3 <= compound_score < 0.6:
            grade, score = 'B', int((compound_score + 1) * 50)
        elif 0.1 <= compound_score < 0.3:
            grade, score = 'C', int((compound_score + 1) * 45)
        elif -0.1 <= compound_score < 0.1:
            grade, score = 'D', int((compound_score + 1) * 40)
        else:
            grade, score = 'F', int((compound_score + 1) * 35)
        
        return grade, score, compound_score
        
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return "N/A", 0, 0.0


def extract_tickers(text):
    """Extract stock tickers from text"""
    if not text:
        return []
    
    # Pattern to match stock tickers (1-5 uppercase letters)
    ticker_pattern = r'\b[A-Z]{1,5}\b'
    potential_tickers = re.findall(ticker_pattern, text)
    
    # Filter out common words that aren't tickers
    common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'BY', 'UP', 'DO', 'NO', 'IF', 'TO', 'MY', 'IS', 'AT', 'AS', 'WE', 'OR', 'AN', 'BE', 'HE', 'IN', 'ON', 'IT', 'OF', 'SO', 'US', 'AM', 'GO', 'GET', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
    
    tickers = [ticker for ticker in potential_tickers if ticker not in common_words]
    return list(set(tickers))  # Remove duplicates


def fetch_yahoo_finance_news():
    """Fetch news from Yahoo Finance"""
    urls = [
        "https://finance.yahoo.com/topic/stock-market-news/",
        "https://finance.yahoo.com/topic/latest-news/",
        "https://finance.yahoo.com/topic/earnings/",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    articles = []
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch from {url}. Status: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try different selectors for Yahoo Finance articles
            article_selectors = [
                "li.stream-item",
                "div[data-module='stream-item']",
                "article",
                "div.js-stream-content li"
            ]
            
            found_articles = []
            for selector in article_selectors:
                found_articles = soup.select(selector)
                if found_articles:
                    break
            
            logger.info(f"Found {len(found_articles)} articles from {url}")
            
            for article in found_articles:
                try:
                    # Extract headline
                    headline_selectors = ["h3", "h2", "h1", ".headline", ".title"]
                    headline = None
                    for sel in headline_selectors:
                        headline_tag = article.select_one(sel)
                        if headline_tag:
                            headline = headline_tag.get_text(strip=True)
                            break
                    
                    # Extract link
                    link_tag = article.select_one("a")
                    link = None
                    if link_tag and link_tag.get('href'):
                        link = urljoin(url, link_tag['href'])
                    
                    # Extract content/summary
                    content_selectors = ["p", ".summary", ".excerpt", ".description"]
                    content = None
                    for sel in content_selectors:
                        content_tag = article.select_one(sel)
                        if content_tag:
                            content = content_tag.get_text(strip=True)
                            break
                    
                    if headline and link:
                        articles.append({
                            'headline': headline,
                            'url': link,
                            'content': content or headline,
                            'source': 'Yahoo Finance'
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching from {url}: {e}")
            continue
    
    return articles


def save_articles_to_db(articles):
    """Save articles to Django database"""
    from .models import NewsArticle
    
    saved_count = 0
    updated_count = 0
    
    for article_data in articles:
        try:
            # Check if article already exists
            existing = NewsArticle.objects.filter(url=article_data['url']).first()
            
            if existing:
                # Update existing article
                existing.headline = article_data['headline']
                existing.content = article_data['content']
                existing.source = article_data['source']
                
                # Re-analyze sentiment
                grade, score, compound = assign_grade(article_data['content'])
                existing.sentiment_grade = grade
                existing.sentiment_score = score
                existing.sentiment_compound = compound
                
                # Extract tickers
                text_to_analyze = f"{article_data['headline']} {article_data['content']}"
                existing.mentioned_tickers = extract_tickers(text_to_analyze)
                
                existing.save()
                updated_count += 1
            else:
                # Create new article
                grade, score, compound = assign_grade(article_data['content'])
                text_to_analyze = f"{article_data['headline']} {article_data['content']}"
                tickers = extract_tickers(text_to_analyze)
                
                NewsArticle.objects.create(
                    headline=article_data['headline'],
                    url=article_data['url'],
                    content=article_data['content'],
                    source=article_data['source'],
                    sentiment_grade=grade,
                    sentiment_score=score,
                    sentiment_compound=compound,
                    mentioned_tickers=tickers,
                    is_market_relevant=len(tickers) > 0 or any(keyword in article_data['headline'].lower() for keyword in ['stock', 'market', 'trading', 'earnings', 'nasdaq', 'dow', 's&p'])
                )
                saved_count += 1
                
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            continue
    
    return saved_count, updated_count


def update_news_data():
    """Main function to update news data"""
    logger.info("🚀 Starting news data update...")
    
    try:
        # Fetch articles from Yahoo Finance
        articles = fetch_yahoo_finance_news()
        logger.info(f"📰 Fetched {len(articles)} articles")
        
        if articles:
            # Save to database
            saved, updated = save_articles_to_db(articles)
            logger.info(f"✅ Saved {saved} new articles, updated {updated} existing articles")
            
            # Clean up old articles (older than 30 days)
            from .models import NewsArticle
            cutoff_date = timezone.now() - timedelta(days=30)
            deleted_count = NewsArticle.objects.filter(published_date__lt=cutoff_date).count()
            NewsArticle.objects.filter(published_date__lt=cutoff_date).delete()
            logger.info(f"🗑️ Cleaned up {deleted_count} old articles")
            
            return True
        else:
            logger.warning("❌ No articles fetched")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error updating news data: {e}")
        return False


def main():
    """Command line interface"""
    success = update_news_data()
    if success:
        print("✅ News update completed successfully")
    else:
        print("❌ News update failed")


if __name__ == "__main__":
    main()
