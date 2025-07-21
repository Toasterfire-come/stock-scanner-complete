from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import re

class WordPressCategory(models.Model):
    """Model for WordPress categories"""
    wp_id = models.IntegerField(unique=True, help_text="Original WordPress category ID")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "WordPress Categories"

    def __str__(self):
        return self.name

class WordPressTag(models.Model):
    """Model for WordPress tags"""
    wp_id = models.IntegerField(unique=True, help_text="Original WordPress tag ID")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "WordPress Tags"

    def __str__(self):
        return self.name

class WordPressPage(models.Model):
    """Model for WordPress pages"""
    wp_id = models.IntegerField(unique=True, help_text="Original WordPress page ID")
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='publish')
    menu_order = models.IntegerField(default=0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    # SEO fields
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    wp_created_date = models.DateTimeField()
    wp_modified_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['menu_order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('wordpress_page', kwargs={'slug': self.slug})

    def get_clean_content(self):
        """Return content with basic HTML cleanup"""
        content = self.content
        # Remove WordPress shortcodes
        content = re.sub(r'\[.*?\]', '', content)
        # Clean up common WordPress artifacts
        content = content.replace('&nbsp;', ' ')
        return content

class WordPressPost(models.Model):
    """Model for WordPress blog posts"""
    wp_id = models.IntegerField(unique=True, help_text="Original WordPress post ID")
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='publish')
    post_type = models.CharField(max_length=50, default='post')
    
    # Relationships
    categories = models.ManyToManyField(WordPressCategory, blank=True)
    tags = models.ManyToManyField(WordPressTag, blank=True)
    
    # Author info
    author_name = models.CharField(max_length=200, blank=True)
    author_email = models.EmailField(blank=True)
    
    # SEO fields
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    wp_created_date = models.DateTimeField()
    wp_modified_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Stock integration
    related_tickers = models.CharField(max_length=500, blank=True, 
                                     help_text="Comma-separated list of stock tickers mentioned")
    is_stock_related = models.BooleanField(default=False)

    class Meta:
        ordering = ['-wp_created_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('wordpress_post', kwargs={'slug': self.slug})

    def get_clean_content(self):
        """Return content with basic HTML cleanup"""
        content = self.content
        # Remove WordPress shortcodes
        content = re.sub(r'\[.*?\]', '', content)
        # Clean up common WordPress artifacts
        content = content.replace('&nbsp;', ' ')
        return content

    def extract_stock_tickers(self):
        """Extract stock tickers from content using regex"""
        content = self.title + ' ' + self.content + ' ' + self.excerpt
        # Look for stock ticker patterns (3-5 uppercase letters)
        ticker_pattern = r'\b[A-Z]{2,5}\b'
        potential_tickers = re.findall(ticker_pattern, content)
        
        # Filter out common words that might match the pattern
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'DID', 'GET', 'MAY', 'HIM', 'OLD', 'SEE', 'NOW', 'WAY', 'WHO', 'BOY', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
        tickers = [ticker for ticker in potential_tickers if ticker not in common_words]
        
        if tickers:
            self.related_tickers = ','.join(set(tickers))
            self.is_stock_related = True
            self.save()
        
        return tickers

class WordPressMedia(models.Model):
    """Model for WordPress media attachments"""
    wp_id = models.IntegerField(unique=True, help_text="Original WordPress attachment ID")
    title = models.CharField(max_length=500)
    filename = models.CharField(max_length=255)
    url = models.URLField()
    mime_type = models.CharField(max_length=100)
    file_size = models.IntegerField(null=True, blank=True)
    
    # Image specific fields
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    alt_text = models.CharField(max_length=300, blank=True)
    
    # Relationships
    attached_to_post = models.ForeignKey(WordPressPost, on_delete=models.SET_NULL, null=True, blank=True)
    attached_to_page = models.ForeignKey(WordPressPage, on_delete=models.SET_NULL, null=True, blank=True)
    
    wp_upload_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.filename

class WordPressImport(models.Model):
    """Model to track WordPress imports"""
    filename = models.CharField(max_length=255)
    import_date = models.DateTimeField(auto_now_add=True)
    posts_imported = models.IntegerField(default=0)
    pages_imported = models.IntegerField(default=0)
    categories_imported = models.IntegerField(default=0)
    tags_imported = models.IntegerField(default=0)
    media_imported = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed')
    ])
    error_log = models.TextField(blank=True)
    
    def __str__(self):
        return f"Import {self.filename} - {self.import_date.strftime('%Y-%m-%d %H:%M')}"

class WordPressMenu(models.Model):
    """Model for WordPress menu items"""
    wp_id = models.IntegerField(unique=True, help_text="Original WordPress menu item ID")
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    menu_order = models.IntegerField(default=0)
    menu_name = models.CharField(max_length=100, default='main')
    
    # Link to internal content
    linked_page = models.ForeignKey(WordPressPage, on_delete=models.CASCADE, null=True, blank=True)
    linked_post = models.ForeignKey(WordPressPost, on_delete=models.CASCADE, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['menu_order', 'title']

    def __str__(self):
        return f"{self.menu_name}: {self.title}"

    def get_url(self):
        """Get the appropriate URL for this menu item"""
        if self.linked_page:
            return self.linked_page.get_absolute_url()
        elif self.linked_post:
            return self.linked_post.get_absolute_url()
        else:
            return self.url