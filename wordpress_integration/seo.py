"""
SEO utilities for WordPress integration with stock-specific optimizations
"""
import re
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.conf import settings
from urllib.parse import urljoin

class SEOOptimizer:
    """SEO optimization utilities for stock-related content"""
    
    def __init__(self):
        self.stock_keywords = [
            'stock analysis', 'trading', 'investment', 'market research',
            'stock price', 'financial analysis', 'stock scanner', 'trading strategy',
            'market trends', 'stock alerts', 'portfolio', 'equity analysis'
        ]
        
    def generate_meta_description(self, content, title="", max_length=160):
        """Generate SEO-optimized meta description"""
        if not content:
            return ""
            
        # Clean content
        clean_content = strip_tags(content).replace('\n', ' ').replace('\r', '')
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Try to find a good excerpt that includes stock keywords
        sentences = clean_content.split('.')
        best_sentence = ""
        
        for sentence in sentences[:5]:  # Check first 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 50 and any(keyword in sentence.lower() for keyword in self.stock_keywords):
                best_sentence = sentence
                break
        
        if not best_sentence and sentences:
            best_sentence = sentences[0].strip()
        
        # Create description
        if best_sentence:
            description = best_sentence
            if len(description) > max_length:
                description = description[:max_length-3] + "..."
        else:
            description = clean_content[:max_length-3] + "..." if len(clean_content) > max_length else clean_content
        
        # Ensure it ends properly
        if not description.endswith(('.', '!', '?', '...')):
            description = description.rstrip() + "."
            
        return description
    
    def generate_keywords(self, title, content, tickers=None):
        """Generate SEO keywords from content"""
        keywords = set()
        
        # Add stock-related base keywords
        keywords.update(['stock analysis', 'trading', 'investment', 'market research'])
        
        # Add tickers if available
        if tickers:
            ticker_list = [t.strip() for t in tickers.split(',') if t.strip()]
            keywords.update(ticker_list)
            for ticker in ticker_list:
                keywords.add(f"{ticker} stock")
                keywords.add(f"{ticker} analysis")
        
        # Extract keywords from title
        title_words = re.findall(r'\b[A-Za-z]{3,}\b', title.lower())
        keywords.update(title_words[:5])
        
        # Extract keywords from content
        content_clean = strip_tags(content).lower()
        
        # Find stock tickers in content
        ticker_pattern = r'\b[A-Z]{2,5}\b'
        found_tickers = re.findall(ticker_pattern, content)
        for ticker in found_tickers:
            if len(ticker) >= 2 and ticker not in ['THE', 'AND', 'FOR', 'ARE']:
                keywords.add(ticker)
                keywords.add(f"{ticker} stock")
        
        # Find financial terms
        financial_terms = [
            'earnings', 'revenue', 'profit', 'dividend', 'market cap',
            'volume', 'volatility', 'bullish', 'bearish', 'resistance',
            'support', 'breakout', 'trend', 'analysis', 'forecast'
        ]
        
        for term in financial_terms:
            if term in content_clean:
                keywords.add(term)
        
        return ', '.join(sorted(list(keywords))[:20])  # Limit to 20 keywords
    
    def generate_structured_data(self, post, request):
        """Generate JSON-LD structured data for articles"""
        base_url = f"{request.scheme}://{request.get_host()}"
        
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.title,
            "description": post.excerpt or self.generate_meta_description(post.content, post.title),
            "url": urljoin(base_url, post.get_absolute_url()),
            "datePublished": post.wp_created_date.isoformat(),
            "dateModified": post.wp_modified_date.isoformat(),
            "author": {
                "@type": "Person",
                "name": post.author_name or "Retail Trade Scan Net"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Retail Trade Scan Net",
                "url": base_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": urljoin(base_url, "/static/logo.png")
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": urljoin(base_url, post.get_absolute_url())
            }
        }
        
        # Add stock-specific data if available
        if post.is_stock_related and post.related_tickers:
            tickers = [t.strip() for t in post.related_tickers.split(',')]
            structured_data["about"] = []
            
            for ticker in tickers:
                structured_data["about"].append({
                    "@type": "Corporation",
                    "name": ticker,
                    "tickerSymbol": ticker,
                    "exchange": "NASDAQ"  # Default, could be enhanced
                })
        
        # Add categories as keywords
        if hasattr(post, 'categories') and post.categories.exists():
            keywords = [cat.name for cat in post.categories.all()]
            structured_data["keywords"] = keywords
        
        return structured_data
    
    def generate_open_graph_data(self, post, request):
        """Generate Open Graph meta tags"""
        base_url = f"{request.scheme}://{request.get_host()}"
        
        og_data = {
            'og:type': 'article',
            'og:title': post.title,
            'og:description': post.excerpt or self.generate_meta_description(post.content, post.title),
            'og:url': urljoin(base_url, post.get_absolute_url()),
            'og:site_name': 'Retail Trade Scan Net',
            'article:published_time': post.wp_created_date.isoformat(),
            'article:modified_time': post.wp_modified_date.isoformat(),
            'article:author': post.author_name or 'Retail Trade Scan Net',
        }
        
        # Add categories as tags
        if hasattr(post, 'categories') and post.categories.exists():
            tags = [cat.name for cat in post.categories.all()]
            og_data['article:tag'] = tags
        
        return og_data
    
    def generate_twitter_card_data(self, post, request):
        """Generate Twitter Card meta tags"""
        base_url = f"{request.scheme}://{request.get_host()}"
        
        twitter_data = {
            'twitter:card': 'summary_large_image',
            'twitter:site': '@RetailTradeScan',  # Update with actual Twitter handle
            'twitter:title': post.title,
            'twitter:description': post.excerpt or self.generate_meta_description(post.content, post.title),
            'twitter:url': urljoin(base_url, post.get_absolute_url()),
        }
        
        return twitter_data

def generate_sitemap_data():
    """Generate sitemap data for all content"""
    from .models import WordPressPost, WordPressPage, WordPressCategory
    from django.urls import reverse
    
    urls = []
    
    # Add WordPress posts
    posts = WordPressPost.objects.filter(status='publish')
    for post in posts:
        urls.append({
            'location': post.get_absolute_url(),
            'lastmod': post.wp_modified_date,
            'changefreq': 'weekly',
            'priority': '0.8' if post.is_stock_related else '0.6'
        })
    
    # Add WordPress pages
    pages = WordPressPage.objects.filter(status='publish')
    for page in pages:
        urls.append({
            'location': page.get_absolute_url(),
            'lastmod': page.wp_modified_date,
            'changefreq': 'monthly',
            'priority': '0.7'
        })
    
    # Add category pages
    categories = WordPressCategory.objects.all()
    for category in categories:
        urls.append({
            'location': reverse('wordpress_integration:category', kwargs={'slug': category.slug}),
            'lastmod': None,
            'changefreq': 'weekly',
            'priority': '0.5'
        })
    
    # Add main WordPress pages
    main_pages = [
        ('wordpress_integration:home', '1.0', 'daily'),
        ('wordpress_integration:blog', '0.9', 'daily'),
        ('wordpress_integration:stock_posts', '0.9', 'daily'),
    ]
    
    for url_name, priority, changefreq in main_pages:
        urls.append({
            'location': reverse(url_name),
            'lastmod': None,
            'changefreq': changefreq,
            'priority': priority
        })
    
    return urls

def generate_robots_txt():
    """Generate robots.txt content"""
    robots_content = """User-agent: *
Allow: /

# Sitemaps
Sitemap: /wp/sitemap.xml
Sitemap: /sitemap.xml

# Allow crawling of stock data
Allow: /filter/
Allow: /search/
Allow: /wp/

# Disallow admin areas
Disallow: /admin/
Disallow: /api/admin/

# Allow RSS feeds
Allow: /wp/feed/

# Crawl delay (be nice to the server)
Crawl-delay: 1
"""
    return robots_content.strip()

class StockSEOEnhancer:
    """Enhance SEO specifically for stock-related content"""
    
    @staticmethod
    def enhance_stock_post_seo(post):
        """Enhance SEO for stock-related posts"""
        if not post.is_stock_related:
            return
        
        seo = SEOOptimizer()
        
        # Update meta description to include stock focus
        if not post.meta_description:
            content_with_stock_focus = f"Stock analysis and trading insights. {post.content[:200]}"
            post.meta_description = seo.generate_meta_description(content_with_stock_focus, post.title)
        
        # Update keywords to include stock-specific terms
        if not post.meta_keywords:
            post.meta_keywords = seo.generate_keywords(post.title, post.content, post.related_tickers)
        
        # Ensure title is SEO-optimized for stocks
        if post.related_tickers and not any(ticker in post.title for ticker in post.related_tickers.split(',')):
            primary_ticker = post.related_tickers.split(',')[0].strip()
            if primary_ticker and primary_ticker not in post.title:
                post.title = f"{post.title} - {primary_ticker} Stock Analysis"
        
        post.save()
    
    @staticmethod
    def generate_stock_rich_snippets(post, stock_data=None):
        """Generate rich snippets for stock-related posts"""
        if not post.is_stock_related:
            return None
        
        rich_snippet = {
            "@context": "https://schema.org",
            "@type": "FinancialProduct",
            "name": f"{post.title}",
            "description": post.excerpt or post.meta_description,
            "provider": {
                "@type": "Organization",
                "name": "Retail Trade Scan Net"
            }
        }
        
        if stock_data:
            rich_snippet.update({
                "price": {
                    "@type": "MonetaryAmount",
                    "value": str(stock_data.current_price),
                    "currency": "USD"
                },
                "offers": {
                    "@type": "Offer",
                    "price": str(stock_data.current_price),
                    "priceCurrency": "USD"
                }
            })
        
        return rich_snippet