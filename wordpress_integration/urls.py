from django.urls import path
from . import views

app_name = 'wordpress_integration'

urlpatterns = [
    # WordPress home page
    path('wp/', views.wordpress_home, name='home'),
    
    # Blog and posts
    path('wp/blog/', views.wordpress_blog, name='blog'),
    path('wp/post/<slug:slug>/', views.wordpress_post_detail, name='post_detail'),
    path('wp/stocks/', views.stock_related_posts, name='stock_posts'),
    
    # Pages
    path('wp/page/<slug:slug>/', views.wordpress_page_detail, name='page_detail'),
    
    # Categories and tags
    path('wp/category/<slug:slug>/', views.wordpress_category, name='category'),
    path('wp/tag/<slug:slug>/', views.wordpress_tag, name='tag'),
    
    # Search
    path('wp/search/', views.wordpress_search, name='search'),
    
    # API endpoints
    path('api/wp-stock-integration/', views.wp_stock_integration_api, name='wp_stock_api'),
    
    # SEO and feeds
    path('wp/sitemap.xml', views.wordpress_sitemap, name='sitemap'),
    path('wp/feed/', views.wordpress_rss, name='rss'),
]