from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    WordPressCategory, WordPressTag, WordPressPage, WordPressPost,
    WordPressMedia, WordPressImport, WordPressMenu
)

@admin.register(WordPressCategory)
class WordPressCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'wp_id', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(WordPressTag)
class WordPressTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'wp_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(WordPressPage)
class WordPressPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'menu_order', 'wp_created_date', 'view_link']
    list_filter = ['status', 'wp_created_date', 'created_at']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['wp_id', 'wp_created_date', 'wp_modified_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'status', 'menu_order', 'parent')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('WordPress Data', {
            'fields': ('wp_id', 'wp_created_date', 'wp_modified_date'),
            'classes': ('collapse',)
        })
    )
    
    def view_link(self, obj):
        if obj.pk:
            return format_html('<a href="{}" target="_blank">View Page</a>', obj.get_absolute_url())
        return '-'
    view_link.short_description = 'View'

@admin.register(WordPressPost)
class WordPressPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'is_stock_related', 'author_name', 'wp_created_date', 'view_link']
    list_filter = ['status', 'is_stock_related', 'categories', 'tags', 'wp_created_date']
    search_fields = ['title', 'slug', 'content', 'author_name', 'related_tickers']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['wp_id', 'wp_created_date', 'wp_modified_date']
    filter_horizontal = ['categories', 'tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'status', 'post_type')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Categorization', {
            'fields': ('categories', 'tags')
        }),
        ('Author', {
            'fields': ('author_name', 'author_email')
        }),
        ('Stock Integration', {
            'fields': ('is_stock_related', 'related_tickers'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('WordPress Data', {
            'fields': ('wp_id', 'wp_created_date', 'wp_modified_date'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['extract_tickers']
    
    def view_link(self, obj):
        if obj.pk:
            return format_html('<a href="{}" target="_blank">View Post</a>', obj.get_absolute_url())
        return '-'
    view_link.short_description = 'View'
    
    def extract_tickers(self, request, queryset):
        """Extract stock tickers from selected posts"""
        count = 0
        for post in queryset:
            tickers = post.extract_stock_tickers()
            if tickers:
                count += 1
        
        self.message_user(request, f"Extracted tickers from {count} posts.")
    extract_tickers.short_description = "Extract stock tickers from content"

@admin.register(WordPressMedia)
class WordPressMediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'filename', 'mime_type', 'file_size', 'wp_upload_date', 'media_link']
    list_filter = ['mime_type', 'wp_upload_date']
    search_fields = ['title', 'filename', 'alt_text']
    readonly_fields = ['wp_id', 'wp_upload_date']
    
    def media_link(self, obj):
        if obj.url:
            return format_html('<a href="{}" target="_blank">View Media</a>', obj.url)
        return '-'
    media_link.short_description = 'View'

@admin.register(WordPressImport)
class WordPressImportAdmin(admin.ModelAdmin):
    list_display = ['filename', 'import_date', 'status', 'posts_imported', 'pages_imported', 'import_summary']
    list_filter = ['status', 'import_date']
    search_fields = ['filename']
    readonly_fields = ['import_date', 'posts_imported', 'pages_imported', 'categories_imported', 'tags_imported', 'media_imported']
    
    def import_summary(self, obj):
        return f"Posts: {obj.posts_imported}, Pages: {obj.pages_imported}, Categories: {obj.categories_imported}"
    import_summary.short_description = 'Summary'

@admin.register(WordPressMenu)
class WordPressMenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'menu_name', 'menu_order', 'parent', 'is_active', 'menu_link']
    list_filter = ['menu_name', 'is_active']
    search_fields = ['title', 'url']
    list_editable = ['menu_order', 'is_active']
    
    def menu_link(self, obj):
        url = obj.get_url()
        if url:
            return format_html('<a href="{}" target="_blank">{}</a>', url, url[:50])
        return '-'
    menu_link.short_description = 'Link'