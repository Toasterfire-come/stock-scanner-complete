#!/usr/bin/env python3
"""
Test script to debug news scraper issues
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from news.scraper import NewsScraper

def test_scraper():
    """Test the news scraper"""
    print("Testing news scraper...")
    
    scraper = NewsScraper()
    
    # Test sentiment analysis
    print("\nTesting sentiment analysis...")
    test_texts = [
        "Apple beats earnings expectations with strong iPhone sales",
        "Tesla stock crashes after disappointing quarterly results",
        "Market remains stable with mixed economic data"
    ]
    
    for text in test_texts:
        sentiment = scraper.analyze_sentiment(text)
        grade = scraper.get_sentiment_grade(text)
        tickers = scraper.extract_tickers(text)
        print(f"Text: {text}")
        print(f"Sentiment: {sentiment}, Grade: {grade}, Tickers: {tickers}")
        print("---")
    
    # Test single source
    print("\nTesting single source...")
    try:
        articles = scraper.scrape_yahoo_finance(limit=5)
        print(f"Scraped {len(articles)} articles from Yahoo Finance")
        if articles:
            print(f"First article: {articles[0]}")
    except Exception as e:
        print(f"Error scraping Yahoo Finance: {e}")
    
    # Test database save
    print("\nTesting database save...")
    try:
        test_articles = [
            {
                'title': 'Test Article 1',
                'summary': 'This is a test article about AAPL',
                'url': 'https://example.com/test1',
                'source': 'Test Source',
                'published_date': django.utils.timezone.now(),
                'mentioned_tickers': 'AAPL',
                'sentiment_score': 0.5,
                'sentiment_grade': 'B'
            }
        ]
        
        saved_count = scraper.save_to_database(test_articles)
        print(f"Saved {saved_count} test articles")
        
    except Exception as e:
        print(f"Error saving to database: {e}")

if __name__ == "__main__":
    test_scraper()