#!/usr/bin/env python3
"""
Simple test for sentiment analysis
"""

import re
from typing import List, Optional

def extract_tickers(text: str) -> List[str]:
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

def analyze_sentiment(text: str) -> Optional[float]:
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

def get_sentiment_grade(text: str) -> str:
    """Get sentiment grade (A-F) based on stock price impact"""
    sentiment = analyze_sentiment(text)
    
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

def test_sentiment():
    """Test sentiment analysis"""
    test_texts = [
        "Apple beats earnings expectations with strong iPhone sales",
        "Tesla stock crashes after disappointing quarterly results",
        "Market remains stable with mixed economic data",
        "Microsoft reports record revenue growth",
        "Bankruptcy filing sends company stock plunging"
    ]
    
    for text in test_texts:
        sentiment = analyze_sentiment(text)
        grade = get_sentiment_grade(text)
        tickers = extract_tickers(text)
        print(f"Text: {text}")
        print(f"Sentiment: {sentiment}, Grade: {grade}, Tickers: {tickers}")
        print("---")

if __name__ == "__main__":
    test_sentiment()