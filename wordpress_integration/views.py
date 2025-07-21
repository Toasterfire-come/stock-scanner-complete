from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import WordPressPost, WordPressPage, WordPressCategory, WordPressTag, WordPressMenu
from stocks.models import StockAlert
import json

def wordpress_home(request):
    """WordPress homepage with recent posts and stock integration"""
    recent_posts = WordPressPost.objects.filter(status='publish').order_by('-wp_created_date')[:6]
    stock_related_posts = WordPressPost.objects.filter(
        status='publish', 
        is_stock_related=True
    ).order_by('-wp_created_date')[:3]
    
    # Get recent stock alerts for sidebar
    recent_stocks = StockAlert.objects.order_by('-last_update')[:5]
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'recent_posts': recent_posts,
        'stock_related_posts': stock_related_posts,
        'recent_stocks': recent_stocks,
        'main_menu': main_menu,
        'page_title': 'Retail Trade Scan Net - Stock Analysis & WordPress Content'
    }
    
    return render(request, 'wordpress_integration/home.html', context)

def wordpress_post_detail(request, slug):
    """Display individual WordPress post with stock integration"""
    post = get_object_or_404(WordPressPost, slug=slug, status='publish')
    
    # Get related stocks if this post mentions tickers
    related_stocks = []
    if post.related_tickers:
        ticker_list = [t.strip() for t in post.related_tickers.split(',')]
        related_stocks = StockAlert.objects.filter(
            ticker__in=ticker_list
        ).order_by('-last_update')[:5]
    
    # Get related posts by categories
    related_posts = WordPressPost.objects.filter(
        categories__in=post.categories.all(),
        status='publish'
    ).exclude(id=post.id).distinct()[:3]
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'post': post,
        'related_stocks': related_stocks,
        'related_posts': related_posts,
        'main_menu': main_menu,
        'page_title': post.title
    }
    
    return render(request, 'wordpress_integration/post_detail.html', context)

def wordpress_page_detail(request, slug):
    """Display individual WordPress page"""
    page = get_object_or_404(WordPressPage, slug=slug, status='publish')
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'page': page,
        'main_menu': main_menu,
        'page_title': page.title
    }
    
    return render(request, 'wordpress_integration/page_detail.html', context)

def wordpress_category(request, slug):
    """Display posts in a specific category"""
    category = get_object_or_404(WordPressCategory, slug=slug)
    posts_list = WordPressPost.objects.filter(
        categories=category,
        status='publish'
    ).order_by('-wp_created_date')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'category': category,
        'posts': posts,
        'main_menu': main_menu,
        'page_title': f"Category: {category.name}"
    }
    
    return render(request, 'wordpress_integration/category.html', context)

def wordpress_tag(request, slug):
    """Display posts with a specific tag"""
    tag = get_object_or_404(WordPressTag, slug=slug)
    posts_list = WordPressPost.objects.filter(
        tags=tag,
        status='publish'
    ).order_by('-wp_created_date')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'tag': tag,
        'posts': posts,
        'main_menu': main_menu,
        'page_title': f"Tag: {tag.name}"
    }
    
    return render(request, 'wordpress_integration/tag.html', context)

def wordpress_search(request):
    """Search WordPress content"""
    query = request.GET.get('q', '')
    posts = []
    pages = []
    
    if query:
        # Search posts
        posts = WordPressPost.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            status='publish'
        ).order_by('-wp_created_date')[:20]
        
        # Search pages
        pages = WordPressPage.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            status='publish'
        ).order_by('-wp_created_date')[:10]
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'query': query,
        'posts': posts,
        'pages': pages,
        'main_menu': main_menu,
        'page_title': f"Search: {query}" if query else "Search"
    }
    
    return render(request, 'wordpress_integration/search.html', context)

def wordpress_blog(request):
    """Blog listing page"""
    posts_list = WordPressPost.objects.filter(status='publish').order_by('-wp_created_date')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = WordPressCategory.objects.filter(
        wordpresspost__status='publish'
    ).distinct().order_by('name')
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'posts': posts,
        'categories': categories,
        'main_menu': main_menu,
        'page_title': 'Blog'
    }
    
    return render(request, 'wordpress_integration/blog.html', context)

def stock_related_posts(request):
    """Display posts related to stocks"""
    posts_list = WordPressPost.objects.filter(
        is_stock_related=True,
        status='publish'
    ).order_by('-wp_created_date')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get recent stock data for context
    recent_stocks = StockAlert.objects.order_by('-last_update')[:10]
    
    # Get main menu
    main_menu = WordPressMenu.objects.filter(
        menu_name='main', 
        is_active=True
    ).order_by('menu_order')
    
    context = {
        'posts': posts,
        'recent_stocks': recent_stocks,
        'main_menu': main_menu,
        'page_title': 'Stock-Related Content'
    }
    
    return render(request, 'wordpress_integration/stock_posts.html', context)

def wp_stock_integration_api(request):
    """API endpoint for WordPress-Stock integration"""
    if request.method == 'GET':
        ticker = request.GET.get('ticker', '').upper()
        
        if not ticker:
            return JsonResponse({'error': 'Ticker parameter required'}, status=400)
        
        # Get stock data
        try:
            stock = StockAlert.objects.get(ticker=ticker)
            stock_data = {
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': float(stock.current_price),
                'price_change_today': float(stock.price_change_today),
                'volume_today': int(stock.volume_today),
                'last_update': stock.last_update.isoformat() if stock.last_update else None
            }
        except StockAlert.DoesNotExist:
            stock_data = None
        
        # Get related WordPress posts
        related_posts = WordPressPost.objects.filter(
            related_tickers__icontains=ticker,
            status='publish'
        ).order_by('-wp_created_date')[:5]
        
        posts_data = [{
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt[:200] + '...' if len(post.excerpt) > 200 else post.excerpt,
            'url': post.get_absolute_url(),
            'date': post.wp_created_date.isoformat()
        } for post in related_posts]
        
        return JsonResponse({
            'ticker': ticker,
            'stock_data': stock_data,
            'related_posts': posts_data,
            'status': 'success'
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def wordpress_sitemap(request):
    """Generate a simple sitemap for WordPress content"""
    posts = WordPressPost.objects.filter(status='publish').order_by('-wp_modified_date')
    pages = WordPressPage.objects.filter(status='publish').order_by('-wp_modified_date')
    categories = WordPressCategory.objects.all().order_by('name')
    
    context = {
        'posts': posts,
        'pages': pages,
        'categories': categories,
    }
    
    return render(request, 'wordpress_integration/sitemap.xml', context, content_type='application/xml')

def wordpress_rss(request):
    """Generate RSS feed for WordPress posts"""
    posts = WordPressPost.objects.filter(status='publish').order_by('-wp_created_date')[:20]
    
    context = {
        'posts': posts,
        'site_title': 'Retail Trade Scan Net',
        'site_description': 'Stock analysis and trading insights',
        'site_url': request.build_absolute_uri('/'),
    }
    
    return render(request, 'wordpress_integration/rss.xml', context, content_type='application/rss+xml')