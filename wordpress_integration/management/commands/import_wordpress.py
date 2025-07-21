import os
import xml.etree.ElementTree as ET
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.db import transaction
from wordpress_integration.models import (
    WordPressCategory, WordPressTag, WordPressPage, WordPressPost,
    WordPressMedia, WordPressImport, WordPressMenu
)
import re
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import WordPress content from XML export file'

    def add_arguments(self, parser):
        parser.add_argument(
            'xml_file',
            type=str,
            help='Path to WordPress XML export file'
        )
        parser.add_argument(
            '--auto-detect',
            action='store_true',
            help='Auto-detect and import Retailtradescannet.Wordpress.2025-07-21.xml'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing content with same WordPress ID'
        )
        parser.add_argument(
            '--extract-tickers',
            action='store_true',
            help='Automatically extract stock tickers from imported content'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )

    def handle(self, *args, **options):
        xml_file = options['xml_file']
        
        # Auto-detect the WordPress file
        if options['auto_detect']:
            possible_locations = [
                'Retailtradescannet.Wordpress.2025-07-21.xml',
                '../Retailtradescannet.Wordpress.2025-07-21.xml',
                '../../Retailtradescannet.Wordpress.2025-07-21.xml',
                os.path.join(os.path.dirname(__file__), '../../../Retailtradescannet.Wordpress.2025-07-21.xml')
            ]
            
            for location in possible_locations:
                if os.path.exists(location):
                    xml_file = location
                    self.stdout.write(f"📁 Found WordPress file: {xml_file}")
                    break
            else:
                raise CommandError("❌ Could not auto-detect Retailtradescannet.Wordpress.2025-07-21.xml file")

        if not os.path.exists(xml_file):
            raise CommandError(f"❌ File not found: {xml_file}")

        self.stdout.write(f"🚀 Starting WordPress import from: {xml_file}")
        
        try:
            with transaction.atomic():
                result = self.import_wordpress_xml(
                    xml_file,
                    options['overwrite'],
                    options['extract_tickers'],
                    options['dry_run']
                )
                
                if not options['dry_run']:
                    # Create import record
                    WordPressImport.objects.create(
                        filename=os.path.basename(xml_file),
                        posts_imported=result['posts'],
                        pages_imported=result['pages'],
                        categories_imported=result['categories'],
                        tags_imported=result['tags'],
                        media_imported=result['media'],
                        status='success'
                    )
                
                self.stdout.write(self.style.SUCCESS("✅ WordPress import completed successfully!"))
                self.display_import_summary(result)
                
        except Exception as e:
            logger.error(f"WordPress import failed: {e}")
            self.stdout.write(self.style.ERROR(f"❌ Import failed: {e}"))
            
            if not options['dry_run']:
                WordPressImport.objects.create(
                    filename=os.path.basename(xml_file),
                    status='failed',
                    error_log=str(e)
                )
            raise

    def import_wordpress_xml(self, xml_file, overwrite=False, extract_tickers=False, dry_run=False):
        """Parse and import WordPress XML content"""
        
        self.stdout.write("📖 Parsing XML file...")
        
        # Parse XML with namespace handling
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # WordPress XML namespaces
        namespaces = {
            'wp': 'http://wordpress.org/export/1.2/',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        result = {
            'posts': 0,
            'pages': 0,
            'categories': 0,
            'tags': 0,
            'media': 0,
            'menus': 0
        }
        
        # Import categories first
        self.stdout.write("📂 Importing categories...")
        result['categories'] = self.import_categories(root, namespaces, overwrite, dry_run)
        
        # Import tags
        self.stdout.write("🏷️  Importing tags...")
        result['tags'] = self.import_tags(root, namespaces, overwrite, dry_run)
        
        # Import posts and pages
        self.stdout.write("📝 Importing posts and pages...")
        posts_result = self.import_posts_and_pages(
            root, namespaces, overwrite, extract_tickers, dry_run
        )
        result['posts'] = posts_result['posts']
        result['pages'] = posts_result['pages']
        result['media'] = posts_result['media']
        
        return result

    def import_categories(self, root, namespaces, overwrite, dry_run):
        """Import WordPress categories"""
        categories = root.findall('.//wp:category', namespaces)
        count = 0
        
        for cat_elem in categories:
            wp_id = int(cat_elem.find('wp:term_id', namespaces).text)
            name = cat_elem.find('wp:cat_name', namespaces).text
            slug = cat_elem.find('wp:category_nicename', namespaces).text
            parent_elem = cat_elem.find('wp:category_parent', namespaces)
            description_elem = cat_elem.find('wp:category_description', namespaces)
            
            parent = None
            if parent_elem is not None and parent_elem.text:
                # Find parent category by slug
                try:
                    parent = WordPressCategory.objects.get(slug=parent_elem.text)
                except WordPressCategory.DoesNotExist:
                    pass
            
            description = description_elem.text if description_elem is not None else ""
            
            if dry_run:
                self.stdout.write(f"  Would import category: {name} (ID: {wp_id})")
                count += 1
                continue
            
            # Check if category exists
            try:
                category = WordPressCategory.objects.get(wp_id=wp_id)
                if overwrite:
                    category.name = name
                    category.slug = slug
                    category.description = description
                    category.parent = parent
                    category.save()
                    self.stdout.write(f"  ✅ Updated category: {name}")
                else:
                    self.stdout.write(f"  ⏭️  Skipped existing category: {name}")
            except WordPressCategory.DoesNotExist:
                WordPressCategory.objects.create(
                    wp_id=wp_id,
                    name=name,
                    slug=slug,
                    description=description,
                    parent=parent
                )
                self.stdout.write(f"  ✅ Created category: {name}")
                count += 1
        
        return count

    def import_tags(self, root, namespaces, overwrite, dry_run):
        """Import WordPress tags"""
        tags = root.findall('.//wp:tag', namespaces)
        count = 0
        
        for tag_elem in tags:
            wp_id = int(tag_elem.find('wp:term_id', namespaces).text)
            name = tag_elem.find('wp:tag_name', namespaces).text
            slug = tag_elem.find('wp:tag_slug', namespaces).text
            description_elem = tag_elem.find('wp:tag_description', namespaces)
            
            description = description_elem.text if description_elem is not None else ""
            
            if dry_run:
                self.stdout.write(f"  Would import tag: {name} (ID: {wp_id})")
                count += 1
                continue
            
            # Check if tag exists
            try:
                tag = WordPressTag.objects.get(wp_id=wp_id)
                if overwrite:
                    tag.name = name
                    tag.slug = slug
                    tag.description = description
                    tag.save()
                    self.stdout.write(f"  ✅ Updated tag: {name}")
                else:
                    self.stdout.write(f"  ⏭️  Skipped existing tag: {name}")
            except WordPressTag.DoesNotExist:
                WordPressTag.objects.create(
                    wp_id=wp_id,
                    name=name,
                    slug=slug,
                    description=description
                )
                self.stdout.write(f"  ✅ Created tag: {name}")
                count += 1
        
        return count

    def import_posts_and_pages(self, root, namespaces, overwrite, extract_tickers, dry_run):
        """Import WordPress posts and pages"""
        items = root.findall('.//item')
        result = {'posts': 0, 'pages': 0, 'media': 0}
        
        for item in items:
            # Get basic item info
            wp_id_elem = item.find('wp:post_id', namespaces)
            if wp_id_elem is None:
                continue
                
            wp_id = int(wp_id_elem.text)
            title = item.find('title').text or ""
            content_elem = item.find('content:encoded', namespaces)
            content = content_elem.text if content_elem is not None else ""
            excerpt_elem = item.find('excerpt:encoded', namespaces)
            excerpt = excerpt_elem.text if excerpt_elem is not None else ""
            
            post_type_elem = item.find('wp:post_type', namespaces)
            post_type = post_type_elem.text if post_type_elem is not None else 'post'
            
            status_elem = item.find('wp:status', namespaces)
            status = status_elem.text if status_elem is not None else 'publish'
            
            # Skip certain post types
            if post_type in ['nav_menu_item', 'revision', 'attachment']:
                if post_type == 'attachment':
                    result['media'] += self.process_attachment(item, namespaces, overwrite, dry_run)
                continue
            
            # Get dates
            pub_date_elem = item.find('wp:post_date', namespaces)
            mod_date_elem = item.find('wp:post_modified', namespaces)
            
            try:
                wp_created_date = parse_datetime(pub_date_elem.text) if pub_date_elem is not None else datetime.now()
                wp_modified_date = parse_datetime(mod_date_elem.text) if mod_date_elem is not None else wp_created_date
            except:
                wp_created_date = datetime.now()
                wp_modified_date = wp_created_date
            
            # Generate slug
            slug_elem = item.find('wp:post_name', namespaces)
            slug = slug_elem.text if slug_elem is not None and slug_elem.text else slugify(title)
            
            # Ensure unique slug
            if not dry_run:
                original_slug = slug
                counter = 1
                while True:
                    if post_type == 'page':
                        exists = WordPressPage.objects.filter(slug=slug).exclude(wp_id=wp_id).exists()
                    else:
                        exists = WordPressPost.objects.filter(slug=slug).exclude(wp_id=wp_id).exists()
                    
                    if not exists:
                        break
                    
                    slug = f"{original_slug}-{counter}"
                    counter += 1
            
            # Get author info
            author_elem = item.find('dc:creator', namespaces)
            author_name = author_elem.text if author_elem is not None else ""
            
            if post_type == 'page':
                result['pages'] += self.process_page(
                    wp_id, title, slug, content, excerpt, status,
                    wp_created_date, wp_modified_date, overwrite, dry_run
                )
            else:
                result['posts'] += self.process_post(
                    item, namespaces, wp_id, title, slug, content, excerpt, status,
                    wp_created_date, wp_modified_date, author_name,
                    overwrite, extract_tickers, dry_run
                )
        
        return result

    def process_page(self, wp_id, title, slug, content, excerpt, status, 
                    wp_created_date, wp_modified_date, overwrite, dry_run):
        """Process a WordPress page"""
        
        if dry_run:
            self.stdout.write(f"  Would import page: {title} (ID: {wp_id})")
            return 1
        
        try:
            page = WordPressPage.objects.get(wp_id=wp_id)
            if overwrite:
                page.title = title
                page.slug = slug
                page.content = content
                page.excerpt = excerpt
                page.status = status
                page.wp_created_date = wp_created_date
                page.wp_modified_date = wp_modified_date
                page.save()
                self.stdout.write(f"  ✅ Updated page: {title}")
            else:
                self.stdout.write(f"  ⏭️  Skipped existing page: {title}")
                return 0
        except WordPressPage.DoesNotExist:
            WordPressPage.objects.create(
                wp_id=wp_id,
                title=title,
                slug=slug,
                content=content,
                excerpt=excerpt,
                status=status,
                wp_created_date=wp_created_date,
                wp_modified_date=wp_modified_date
            )
            self.stdout.write(f"  ✅ Created page: {title}")
        
        return 1

    def process_post(self, item, namespaces, wp_id, title, slug, content, excerpt, status,
                    wp_created_date, wp_modified_date, author_name, overwrite, extract_tickers, dry_run):
        """Process a WordPress post"""
        
        if dry_run:
            self.stdout.write(f"  Would import post: {title} (ID: {wp_id})")
            return 1
        
        try:
            post = WordPressPost.objects.get(wp_id=wp_id)
            if not overwrite:
                self.stdout.write(f"  ⏭️  Skipped existing post: {title}")
                return 0
        except WordPressPost.DoesNotExist:
            post = None
        
        # Create or update post
        if post:
            post.title = title
            post.slug = slug
            post.content = content
            post.excerpt = excerpt
            post.status = status
            post.author_name = author_name
            post.wp_created_date = wp_created_date
            post.wp_modified_date = wp_modified_date
            post.save()
            action = "Updated"
        else:
            post = WordPressPost.objects.create(
                wp_id=wp_id,
                title=title,
                slug=slug,
                content=content,
                excerpt=excerpt,
                status=status,
                author_name=author_name,
                wp_created_date=wp_created_date,
                wp_modified_date=wp_modified_date
            )
            action = "Created"
        
        # Process categories and tags
        self.process_post_taxonomies(item, namespaces, post)
        
        # Extract stock tickers if requested
        if extract_tickers:
            tickers = post.extract_stock_tickers()
            if tickers:
                self.stdout.write(f"    📈 Found tickers: {', '.join(tickers)}")
        
        self.stdout.write(f"  ✅ {action} post: {title}")
        return 1

    def process_post_taxonomies(self, item, namespaces, post):
        """Process categories and tags for a post"""
        
        # Process categories
        categories = item.findall('category[@domain="category"]')
        for cat in categories:
            cat_slug = cat.get('nicename')
            if cat_slug:
                try:
                    category = WordPressCategory.objects.get(slug=cat_slug)
                    post.categories.add(category)
                except WordPressCategory.DoesNotExist:
                    pass
        
        # Process tags
        tags = item.findall('category[@domain="post_tag"]')
        for tag in tags:
            tag_slug = tag.get('nicename')
            if tag_slug:
                try:
                    tag_obj = WordPressTag.objects.get(slug=tag_slug)
                    post.tags.add(tag_obj)
                except WordPressTag.DoesNotExist:
                    pass

    def process_attachment(self, item, namespaces, overwrite, dry_run):
        """Process WordPress media attachments"""
        
        wp_id_elem = item.find('wp:post_id', namespaces)
        if wp_id_elem is None:
            return 0
            
        wp_id = int(wp_id_elem.text)
        title = item.find('title').text or ""
        
        # Get attachment URL
        guid_elem = item.find('guid')
        url = guid_elem.text if guid_elem is not None else ""
        
        # Get filename from URL
        filename = os.path.basename(url) if url else ""
        
        # Get upload date
        upload_date_elem = item.find('wp:post_date', namespaces)
        try:
            wp_upload_date = parse_datetime(upload_date_elem.text) if upload_date_elem is not None else datetime.now()
        except:
            wp_upload_date = datetime.now()
        
        if dry_run:
            self.stdout.write(f"  Would import media: {title} (ID: {wp_id})")
            return 1
        
        try:
            media = WordPressMedia.objects.get(wp_id=wp_id)
            if not overwrite:
                return 0
        except WordPressMedia.DoesNotExist:
            media = None
        
        # Determine MIME type from filename
        mime_type = "application/octet-stream"
        if filename:
            ext = filename.lower().split('.')[-1] if '.' in filename else ""
            mime_types = {
                'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                'gif': 'image/gif', 'pdf': 'application/pdf', 'mp4': 'video/mp4'
            }
            mime_type = mime_types.get(ext, "application/octet-stream")
        
        if media:
            media.title = title
            media.filename = filename
            media.url = url
            media.mime_type = mime_type
            media.wp_upload_date = wp_upload_date
            media.save()
        else:
            WordPressMedia.objects.create(
                wp_id=wp_id,
                title=title,
                filename=filename,
                url=url,
                mime_type=mime_type,
                wp_upload_date=wp_upload_date
            )
        
        return 1

    def display_import_summary(self, result):
        """Display import summary"""
        self.stdout.write("\n📊 Import Summary:")
        self.stdout.write(f"  📝 Posts: {result['posts']}")
        self.stdout.write(f"  📄 Pages: {result['pages']}")
        self.stdout.write(f"  📂 Categories: {result['categories']}")
        self.stdout.write(f"  🏷️  Tags: {result['tags']}")
        self.stdout.write(f"  🖼️  Media: {result['media']}")
        self.stdout.write(f"  📎 Total items: {sum(result.values())}")
        self.stdout.write("\n✨ WordPress content is now seamlessly integrated with your stock scanner!")