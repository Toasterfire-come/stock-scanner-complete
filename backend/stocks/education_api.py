"""
API endpoints for Educational Platform (Phase 7)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


# ============================================================================
# COURSE CATEGORIES AND CONTENT
# ============================================================================

COURSES = {
    'basics': {
        'id': 'basics',
        'title': 'Trading Basics',
        'description': 'Essential concepts for beginning traders',
        'icon': '📚',
        'lessons': [
            {
                'id': 'basics-1',
                'title': 'What is Stock Trading?',
                'duration': '10 min',
                'content': 'Learn the fundamentals of stock trading, market participants, and how exchanges work.',
                'topics': ['Stocks', 'Markets', 'Exchanges', 'Brokers']
            },
            {
                'id': 'basics-2',
                'title': 'Understanding Stock Prices',
                'duration': '12 min',
                'content': 'How stock prices are determined, bid/ask spread, and market orders.',
                'topics': ['Bid/Ask', 'Market Orders', 'Limit Orders', 'Supply & Demand']
            },
            {
                'id': 'basics-3',
                'title': 'Reading Stock Charts',
                'duration': '15 min',
                'content': 'Introduction to candlestick charts, volume, and basic chart patterns.',
                'topics': ['Candlesticks', 'Volume', 'Trends', 'Support & Resistance']
            },
            {
                'id': 'basics-4',
                'title': 'Risk Management',
                'duration': '18 min',
                'content': 'Essential risk management principles, position sizing, and stop losses.',
                'topics': ['Position Sizing', 'Stop Loss', 'Risk/Reward', 'Portfolio Diversification']
            }
        ]
    },
    'technical': {
        'id': 'technical',
        'title': 'Technical Analysis',
        'description': 'Chart patterns and technical indicators',
        'icon': '📊',
        'lessons': [
            {
                'id': 'technical-1',
                'title': 'Moving Averages',
                'duration': '20 min',
                'content': 'SMA, EMA, and how to use moving averages for trend identification.',
                'topics': ['SMA', 'EMA', 'Crossovers', 'Trend Following']
            },
            {
                'id': 'technical-2',
                'title': 'RSI & Momentum Indicators',
                'duration': '22 min',
                'content': 'Understanding RSI, MACD, and other momentum indicators.',
                'topics': ['RSI', 'MACD', 'Stochastic', 'Momentum']
            },
            {
                'id': 'technical-3',
                'title': 'Support & Resistance',
                'duration': '18 min',
                'content': 'Identifying key support and resistance levels for entry and exit.',
                'topics': ['Horizontal Levels', 'Trendlines', 'Fibonacci', 'Pivot Points']
            },
            {
                'id': 'technical-4',
                'title': 'Chart Patterns',
                'duration': '25 min',
                'content': 'Recognizing and trading common chart patterns.',
                'topics': ['Head & Shoulders', 'Triangles', 'Flags', 'Cup & Handle']
            },
            {
                'id': 'technical-5',
                'title': 'Volume Analysis',
                'duration': '16 min',
                'content': 'Using volume to confirm trends and identify reversals.',
                'topics': ['Volume Spikes', 'OBV', 'VWAP', 'Volume Patterns']
            }
        ]
    },
    'fundamental': {
        'id': 'fundamental',
        'title': 'Fundamental Analysis',
        'description': 'Company valuation and financial metrics',
        'icon': '💰',
        'lessons': [
            {
                'id': 'fundamental-1',
                'title': 'Financial Statements',
                'duration': '25 min',
                'content': 'Reading income statements, balance sheets, and cash flow statements.',
                'topics': ['Income Statement', 'Balance Sheet', 'Cash Flow', 'Financial Ratios']
            },
            {
                'id': 'fundamental-2',
                'title': 'Valuation Metrics',
                'duration': '22 min',
                'content': 'P/E ratio, P/B ratio, PEG, and other valuation metrics.',
                'topics': ['P/E Ratio', 'P/B Ratio', 'PEG', 'Price to Sales']
            },
            {
                'id': 'fundamental-3',
                'title': 'DCF Valuation',
                'duration': '30 min',
                'content': 'Discounted Cash Flow analysis for intrinsic value calculation.',
                'topics': ['DCF Model', 'WACC', 'Terminal Value', 'Intrinsic Value']
            },
            {
                'id': 'fundamental-4',
                'title': 'Earnings Analysis',
                'duration': '20 min',
                'content': 'Understanding earnings reports, EPS, and earnings seasons.',
                'topics': ['EPS', 'Earnings Reports', 'Guidance', 'Earnings Season']
            }
        ]
    },
    'strategies': {
        'id': 'strategies',
        'title': 'Trading Strategies',
        'description': 'Day trading, swing trading, and long-term strategies',
        'icon': '🎯',
        'lessons': [
            {
                'id': 'strategies-1',
                'title': 'Day Trading Strategies',
                'duration': '28 min',
                'content': 'Popular day trading strategies including scalping, momentum, and reversal.',
                'topics': ['Scalping', 'Momentum Trading', 'Gap Trading', 'Range Trading']
            },
            {
                'id': 'strategies-2',
                'title': 'Swing Trading Strategies',
                'duration': '26 min',
                'content': 'Multi-day strategies for capturing swings in stock prices.',
                'topics': ['Trend Following', 'Mean Reversion', 'Breakout Trading', 'Pattern Trading']
            },
            {
                'id': 'strategies-3',
                'title': 'Long-Term Investing',
                'duration': '24 min',
                'content': 'Value investing, growth investing, and dividend strategies.',
                'topics': ['Value Investing', 'Growth Investing', 'Dividend Investing', 'GARP']
            },
            {
                'id': 'strategies-4',
                'title': 'Backtesting Strategies',
                'duration': '22 min',
                'content': 'How to backtest trading strategies and interpret results.',
                'topics': ['Backtest Setup', 'Performance Metrics', 'Optimization', 'Walk-Forward Analysis']
            }
        ]
    },
    'psychology': {
        'id': 'psychology',
        'title': 'Trading Psychology',
        'description': 'Mental discipline and emotional control',
        'icon': '🧠',
        'lessons': [
            {
                'id': 'psychology-1',
                'title': 'Common Trading Biases',
                'duration': '20 min',
                'content': 'Recognizing and overcoming cognitive biases in trading.',
                'topics': ['Confirmation Bias', 'Loss Aversion', 'Recency Bias', 'Overconfidence']
            },
            {
                'id': 'psychology-2',
                'title': 'Emotional Discipline',
                'duration': '18 min',
                'content': 'Managing emotions like fear, greed, and FOMO in trading.',
                'topics': ['Fear', 'Greed', 'FOMO', 'Revenge Trading']
            },
            {
                'id': 'psychology-3',
                'title': 'Developing a Trading Plan',
                'duration': '25 min',
                'content': 'Creating and sticking to a structured trading plan.',
                'topics': ['Goals', 'Rules', 'Journal', 'Review Process']
            },
            {
                'id': 'psychology-4',
                'title': 'Building Mental Toughness',
                'duration': '22 min',
                'content': 'Techniques for staying disciplined during winning and losing streaks.',
                'topics': ['Discipline', 'Patience', 'Consistency', 'Mindfulness']
            }
        ]
    }
}


# ============================================================================
# TRADING GLOSSARY (200+ terms)
# ============================================================================

GLOSSARY = {
    # A
    'Ask': 'The lowest price a seller is willing to accept for a security',
    'ATR': 'Average True Range - measures market volatility',
    'Accumulation': 'Phase where investors are buying stocks, often before a price increase',
    'Alpha': 'Excess return of an investment relative to a benchmark',
    'Arbitrage': 'Simultaneous purchase and sale to profit from price differences',
    
    # B
    'Bid': 'The highest price a buyer is willing to pay for a security',
    'Bear Market': 'Market condition where prices are falling or expected to fall',
    'Bull Market': 'Market condition where prices are rising or expected to rise',
    'Breakout': 'When price moves above resistance or below support',
    'Beta': 'Measure of a stock\'s volatility relative to the market',
    'Bollinger Bands': 'Volatility indicator using standard deviations',
    'Blue Chip': 'Stock of a large, well-established, and financially sound company',
    
    # C
    'Candlestick': 'Chart representation showing open, high, low, and close prices',
    'Call Option': 'Contract giving the right to buy an asset at a specified price',
    'Consolidation': 'Period where price trades in a range after a significant move',
    'Crossover': 'When two moving averages cross each other',
    'Cup and Handle': 'Bullish continuation pattern resembling a tea cup',
    
    # D
    'Day Trading': 'Buying and selling securities within the same trading day',
    'Dividend': 'Payment made by a company to its shareholders',
    'Divergence': 'When price and indicator move in opposite directions',
    'Drawdown': 'Peak-to-trough decline in portfolio value',
    'DCF': 'Discounted Cash Flow - valuation method based on future cash flows',
    'Distribution': 'Phase where investors are selling stocks, often before a price decrease',
    
    # E
    'EMA': 'Exponential Moving Average - weighted average giving more importance to recent prices',
    'EPS': 'Earnings Per Share - company profit divided by outstanding shares',
    'Entry Point': 'Price level at which a trade is initiated',
    'Exit Point': 'Price level at which a trade is closed',
    'Ex-Dividend Date': 'Date on which a stock trades without the value of its next dividend',
    
    # F
    'FOMO': 'Fear Of Missing Out - emotional driver of impulsive trading',
    'Fibonacci Retracement': 'Technical tool using horizontal lines at key Fibonacci levels',
    'Float': 'Number of shares available for public trading',
    'Fundamental Analysis': 'Evaluation of a stock based on financial data',
    'Futures': 'Contract to buy or sell an asset at a predetermined future date',
    
    # G
    'Gap': 'Price discontinuity between one day\'s close and next day\'s open',
    'Graham Number': 'Intrinsic value formula created by Benjamin Graham',
    'Growth Stock': 'Stock expected to grow at an above-average rate',
    'GARP': 'Growth At a Reasonable Price investment strategy',
    
    # H
    'Head and Shoulders': 'Reversal pattern indicating potential trend change',
    'Hedge': 'Investment strategy to reduce risk',
    'High of Day (HOD)': 'Highest price reached during a trading session',
    'Heikin-Ashi': 'Modified candlestick chart type that filters market noise',
    
    # I
    'Indicator': 'Statistical calculation based on price and/or volume',
    'IPO': 'Initial Public Offering - first sale of stock by a company',
    'Intrinsic Value': 'Perceived fundamental value of a security',
    'Iron Condor': 'Options strategy combining bull put and bear call spreads',
    
    # L
    'Limit Order': 'Order to buy or sell at a specific price or better',
    'Liquidity': 'Ease with which an asset can be bought or sold',
    'Long Position': 'Buying a security with expectation of price increase',
    'Low of Day (LOD)': 'Lowest price reached during a trading session',
    
    # M
    'MACD': 'Moving Average Convergence Divergence - momentum indicator',
    'Market Order': 'Order to buy or sell immediately at current market price',
    'Market Cap': 'Total market value of a company\'s outstanding shares',
    'Margin': 'Borrowing money from broker to purchase securities',
    'Moving Average': 'Average price over a specific time period',
    'Momentum': 'Rate of price change, strength of price movement',
    
    # O
    'OHLC': 'Open, High, Low, Close - basic price data points',
    'Options': 'Derivative contracts giving the right to buy or sell an asset',
    'Overbought': 'Condition where price has risen too quickly',
    'Oversold': 'Condition where price has fallen too quickly',
    'OBV': 'On-Balance Volume - momentum indicator using volume flow',
    
    # P
    'P/E Ratio': 'Price-to-Earnings ratio - valuation metric',
    'Put Option': 'Contract giving the right to sell an asset at a specified price',
    'Pivot Point': 'Technical indicator for potential support/resistance',
    'Position Size': 'Amount of capital allocated to a single trade',
    'Pullback': 'Temporary reversal in the direction of a trend',
    'Pattern Day Trader': 'Trader who executes 4+ day trades within 5 business days',
    
    # R
    'RSI': 'Relative Strength Index - momentum oscillator (0-100)',
    'Resistance': 'Price level where selling pressure may overcome buying pressure',
    'Risk/Reward Ratio': 'Comparison of potential profit to potential loss',
    'Reversal': 'Change in price trend direction',
    'Retracement': 'Temporary price movement against the prevailing trend',
    
    # S
    'SMA': 'Simple Moving Average - arithmetic mean of prices over a period',
    'Scalping': 'Very short-term trading strategy for small profits',
    'Short Selling': 'Selling borrowed stock expecting to buy back at lower price',
    'Stop Loss': 'Order to sell when price reaches a specified level',
    'Support': 'Price level where buying pressure may overcome selling pressure',
    'Swing Trading': 'Holding positions for several days to weeks',
    'Sharpe Ratio': 'Risk-adjusted return measure',
    'Spread': 'Difference between bid and ask price',
    
    # T
    'Technical Analysis': 'Evaluation of stocks using price charts and patterns',
    'Trend': 'General direction in which a stock price is moving',
    'Trendline': 'Line connecting price highs or lows to show trend direction',
    'Take Profit': 'Order to close position when target price is reached',
    'Timeframe': 'Period of time represented by each candlestick or bar',
    
    # V
    'Volume': 'Number of shares traded during a given period',
    'VWAP': 'Volume-Weighted Average Price - intraday benchmark',
    'Volatility': 'Degree of variation in trading prices',
    'Value Stock': 'Stock trading below its intrinsic value',
    
    # W
    'Watchlist': 'List of stocks monitored for potential trades',
    'Whipsaw': 'Rapid price movement in one direction followed by sharp reversal',
    'Window': 'Alternative term for a gap in Japanese candlestick analysis',
    
    # Y
    'Yield': 'Income return on an investment',
    'YTD': 'Year-To-Date - performance since beginning of current year',
}


# ============================================================================
# API ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_all_courses(request):
    """Get list of all available courses"""
    try:
        courses_list = [
            {
                'id': course['id'],
                'title': course['title'],
                'description': course['description'],
                'icon': course['icon'],
                'lesson_count': len(course['lessons']),
                'total_duration': sum(
                    int(lesson['duration'].split()[0]) 
                    for lesson in course['lessons']
                )
            }
            for course in COURSES.values()
        ]
        
        return JsonResponse({
            'success': True,
            'courses': courses_list
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_course(request, course_id):
    """Get detailed information about a specific course"""
    try:
        if course_id not in COURSES:
            return JsonResponse({
                'success': False,
                'error': 'Course not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'course': COURSES[course_id]
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_lesson(request, course_id, lesson_id):
    """Get detailed information about a specific lesson"""
    try:
        if course_id not in COURSES:
            return JsonResponse({
                'success': False,
                'error': 'Course not found'
            }, status=404)
        
        course = COURSES[course_id]
        lesson = next((l for l in course['lessons'] if l['id'] == lesson_id), None)
        
        if not lesson:
            return JsonResponse({
                'success': False,
                'error': 'Lesson not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'lesson': lesson,
            'course_title': course['title']
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_glossary(request):
    """
    Get trading glossary
    
    Query params:
    - search: search term (optional)
    - letter: filter by starting letter (optional)
    """
    try:
        search = request.GET.get('search', '').lower()
        letter = request.GET.get('letter', '').upper()
        
        # Filter glossary
        filtered_glossary = {}
        for term, definition in GLOSSARY.items():
            # Apply letter filter
            if letter and not term.upper().startswith(letter):
                continue
            
            # Apply search filter
            if search and search not in term.lower() and search not in definition.lower():
                continue
            
            filtered_glossary[term] = definition
        
        # Convert to list format
        glossary_list = [
            {'term': term, 'definition': definition}
            for term, definition in sorted(filtered_glossary.items())
        ]
        
        return JsonResponse({
            'success': True,
            'glossary': glossary_list,
            'total': len(glossary_list)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_glossary_term(request, term):
    """Get definition of a specific glossary term"""
    try:
        # Case-insensitive search
        term_key = next((k for k in GLOSSARY.keys() if k.lower() == term.lower()), None)
        
        if not term_key:
            return JsonResponse({
                'success': False,
                'error': 'Term not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'term': term_key,
            'definition': GLOSSARY[term_key]
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_interactive_tooltips(request):
    """Get commonly used terms for interactive tooltips"""
    try:
        # Select most commonly used terms
        common_terms = [
            'RSI', 'MACD', 'SMA', 'EMA', 'Support', 'Resistance', 
            'Volume', 'VWAP', 'Bollinger Bands', 'Candlestick',
            'Breakout', 'Pullback', 'Trend', 'Stop Loss', 'Take Profit'
        ]
        
        tooltips = {
            term: GLOSSARY[term]
            for term in common_terms
            if term in GLOSSARY
        }
        
        return JsonResponse({
            'success': True,
            'tooltips': tooltips
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
