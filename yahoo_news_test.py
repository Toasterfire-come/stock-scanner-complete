#!/usr/bin/env python3
"""
Standalone Yahoo Finance News Scraper Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news.scraper import YahooFinanceNewsScraper

def test_yahoo_news_scraper():
    """Test the Yahoo Finance news scraper"""
    print("=" * 60)
    print("YAHOO FINANCE NEWS SCRAPER TEST")
    print("=" * 60)
    
    scraper = YahooFinanceNewsScraper()
    
    # Test with a smaller limit for testing
    articles = scraper.scrape_all_yahoo_feeds(limit_per_feed=20)
    
    print(f"\nTotal Articles Scraped: {len(articles)}")
    
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
    
    # Show high impact articles
    high_impact = [a for a in articles if a.get('impact_score', 0) >= 8]
    print(f"\nHigh Impact Articles (Score 8+): {len(high_impact)}")
    
    # Show articles with major tickers
    major_ticker_articles = [a for a in articles if any(ticker in a.get('mentioned_tickers', '') for ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])]
    print(f"Articles mentioning major stocks: {len(major_ticker_articles)}")
    
    # Show sample articles
    print(f"\nSample Articles:")
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article['title']}")
        print(f"   Grade: {article['sentiment_grade']} | Impact: {article['impact_score']}")
        print(f"   Tickers: {article['mentioned_tickers']}")
        print(f"   URL: {article['url']}")
    
    # Show top positive articles
    positive_articles = [a for a in articles if a.get('sentiment_grade') in ['A', 'B']]
    print(f"\nTop Positive Articles (A/B Grade):")
    for i, article in enumerate(positive_articles[:3]):
        print(f"\n{i+1}. {article['title']}")
        print(f"   Grade: {article['sentiment_grade']} | Impact: {article['impact_score']}")
    
    # Show top negative articles
    negative_articles = [a for a in articles if a.get('sentiment_grade') in ['D', 'F']]
    print(f"\nTop Negative Articles (D/F Grade):")
    for i, article in enumerate(negative_articles[:3]):
        print(f"\n{i+1}. {article['title']}")
        print(f"   Grade: {article['sentiment_grade']} | Impact: {article['impact_score']}")
    
    return articles

if __name__ == "__main__":
    test_yahoo_news_scraper()