"""
Django management command for intelligent cache management
Usage: python manage.py clear_cache [--type=all] [--pattern=key_pattern]
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache, caches
from django.utils import timezone
import logging
import re

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Intelligent cache management for Stock Scanner'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['all', 'stock', 'query', 'session', 'api'],
            default='all',
            help='Type of cache to clear (default: all)'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Clear cache keys matching this pattern (regex supported)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleared without actually clearing'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show cache statistics before and after clearing'
        )

    def handle(self, *args, **options):
        """Execute cache management operations"""
        
        self.stdout.write("🧹 Starting Stock Scanner Cache Management...")
        self.stdout.write(f"⏰ Started at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            if options['stats']:
                self._show_cache_stats("Before clearing:")
            
            if options['pattern']:
                self._clear_by_pattern(options['pattern'], options['dry_run'])
            else:
                self._clear_by_type(options['type'], options['dry_run'])
            
            if options['stats'] and not options['dry_run']:
                self._show_cache_stats("After clearing:")
                
            self.stdout.write("✅ Cache management completed!")
                
        except Exception as e:
            logger.error(f"Cache management failed: {e}")
            raise CommandError(f"Cache management failed: {e}")

    def _clear_by_type(self, cache_type, dry_run=False):
        """Clear cache by type"""
        
        if cache_type == 'all':
            self._clear_all_caches(dry_run)
        elif cache_type == 'stock':
            self._clear_stock_cache(dry_run)
        elif cache_type == 'query':
            self._clear_query_cache(dry_run)
        elif cache_type == 'session':
            self._clear_session_cache(dry_run)
        elif cache_type == 'api':
            self._clear_api_cache(dry_run)

    def _clear_all_caches(self, dry_run=False):
        """Clear all cache types"""
        
        self.stdout.write("🧹 Clearing all caches...")
        
        cache_operations = [
            ("Default cache", lambda: self._clear_default_cache(dry_run)),
            ("Query cache", lambda: self._clear_specific_cache('query_cache', dry_run)),
            ("Session cache", lambda: self._clear_specific_cache('sessions', dry_run)),
        ]
        
        total_cleared = 0
        for cache_name, operation in cache_operations:
            try:
                cleared = operation()
                total_cleared += cleared
                self.stdout.write(f"  ✅ {cache_name}: {cleared} items")
            except Exception as e:
                self.stdout.write(f"  ❌ {cache_name}: Error - {e}")
        
        if not dry_run:
            self.stdout.write(f"🗑️  Total items cleared: {total_cleared}")
        else:
            self.stdout.write(f"🔍 Would clear {total_cleared} items")

    def _clear_default_cache(self, dry_run=False):
        """Clear the default cache"""
        
        if dry_run:
            # For dry run, we can't get exact count without implementation-specific methods
            self.stdout.write("  🔍 Would clear default cache")
            return 1
        else:
            cache.clear()
            return 1

    def _clear_specific_cache(self, cache_name, dry_run=False):
        """Clear a specific named cache"""
        
        try:
            specific_cache = caches[cache_name]
            if dry_run:
                self.stdout.write(f"  🔍 Would clear {cache_name} cache")
                return 1
            else:
                specific_cache.clear()
                return 1
        except Exception as e:
            logger.warning(f"Could not clear {cache_name} cache: {e}")
            return 0

    def _clear_stock_cache(self, dry_run=False):
        """Clear stock-related cache entries"""
        
        self.stdout.write("📈 Clearing stock cache...")
        
        stock_patterns = [
            r'stock_.*',
            r'ticker_.*',
            r'market_.*',
            r'price_.*',
            r'.*stock.*'
        ]
        
        total_cleared = 0
        for pattern in stock_patterns:
            cleared = self._clear_by_pattern(pattern, dry_run, silent=True)
            total_cleared += cleared
        
        if not dry_run:
            self.stdout.write(f"📈 Stock cache cleared: {total_cleared} items")
        else:
            self.stdout.write(f"📈 Would clear {total_cleared} stock cache items")
        
        return total_cleared

    def _clear_query_cache(self, dry_run=False):
        """Clear query cache"""
        
        self.stdout.write("🔍 Clearing query cache...")
        
        try:
            query_cache = caches['query_cache']
            if dry_run:
                self.stdout.write("  🔍 Would clear query cache")
                return 1
            else:
                query_cache.clear()
                self.stdout.write("  ✅ Query cache cleared")
                return 1
        except KeyError:
            self.stdout.write("  ℹ️  Query cache not configured")
            return 0
        except Exception as e:
            self.stdout.write(f"  ❌ Error clearing query cache: {e}")
            return 0

    def _clear_session_cache(self, dry_run=False):
        """Clear session cache"""
        
        self.stdout.write("👤 Clearing session cache...")
        
        try:
            session_cache = caches['sessions']
            if dry_run:
                self.stdout.write("  🔍 Would clear session cache")
                return 1
            else:
                session_cache.clear()
                self.stdout.write("  ✅ Session cache cleared")
                return 1
        except KeyError:
            self.stdout.write("  ℹ️  Session cache not configured")
            return 0
        except Exception as e:
            self.stdout.write(f"  ❌ Error clearing session cache: {e}")
            return 0

    def _clear_api_cache(self, dry_run=False):
        """Clear API response cache"""
        
        self.stdout.write("🌐 Clearing API cache...")
        
        api_patterns = [
            r'api_.*',
            r'response_.*',
            r'.*_api_.*',
            r'pagination_.*'
        ]
        
        total_cleared = 0
        for pattern in api_patterns:
            cleared = self._clear_by_pattern(pattern, dry_run, silent=True)
            total_cleared += cleared
        
        if not dry_run:
            self.stdout.write(f"🌐 API cache cleared: {total_cleared} items")
        else:
            self.stdout.write(f"🌐 Would clear {total_cleared} API cache items")
        
        return total_cleared

    def _clear_by_pattern(self, pattern, dry_run=False, silent=False):
        """Clear cache entries matching a pattern"""
        
        if not silent:
            self.stdout.write(f"🔍 Clearing cache entries matching pattern: {pattern}")
        
        try:
            # Note: This is a simplified implementation
            # In production, you might need Redis-specific commands for pattern matching
            compiled_pattern = re.compile(pattern)
            
            # For Django's default cache, we can't easily list keys
            # This would work better with Redis backend
            if hasattr(cache, 'keys'):
                # Redis backend
                matching_keys = [key for key in cache.keys('*') if compiled_pattern.match(key)]
                if dry_run:
                    if not silent:
                        self.stdout.write(f"  🔍 Would clear {len(matching_keys)} keys")
                    return len(matching_keys)
                else:
                    for key in matching_keys:
                        cache.delete(key)
                    if not silent:
                        self.stdout.write(f"  ✅ Cleared {len(matching_keys)} keys")
                    return len(matching_keys)
            else:
                # Fallback for non-Redis backends
                if not silent:
                    self.stdout.write("  ℹ️  Pattern matching not supported with current cache backend")
                return 0
                
        except Exception as e:
            if not silent:
                self.stdout.write(f"  ❌ Error clearing pattern {pattern}: {e}")
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0

    def _show_cache_stats(self, title):
        """Show cache statistics"""
        
        self.stdout.write(f"\n📊 {title}")
        
        # Try to get cache statistics
        try:
            # This would work with Redis
            if hasattr(cache, 'get_stats'):
                stats = cache.get_stats()
                self.stdout.write(f"  📈 Cache hits: {stats.get('hits', 'N/A')}")
                self.stdout.write(f"  📉 Cache misses: {stats.get('misses', 'N/A')}")
                self.stdout.write(f"  🗂️  Keys in cache: {stats.get('keys', 'N/A')}")
            elif hasattr(cache, 'keys'):
                # Redis backend
                key_count = len(cache.keys('*'))
                self.stdout.write(f"  🗂️  Keys in cache: {key_count}")
            else:
                self.stdout.write("  ℹ️  Cache statistics not available")
                
            # Check different cache types
            for cache_name in ['default', 'query_cache', 'sessions']:
                try:
                    specific_cache = caches[cache_name]
                    if hasattr(specific_cache, 'keys'):
                        key_count = len(specific_cache.keys('*'))
                        self.stdout.write(f"  📦 {cache_name}: {key_count} keys")
                except:
                    pass
                    
        except Exception as e:
            self.stdout.write(f"  ❌ Error getting cache stats: {e}")

    def _estimate_cache_size(self):
        """Estimate cache memory usage"""
        
        try:
            if hasattr(cache, 'info'):
                # Redis info
                info = cache.info()
                memory_usage = info.get('used_memory_human', 'N/A')
                self.stdout.write(f"  💾 Memory usage: {memory_usage}")
            else:
                self.stdout.write("  💾 Memory usage information not available")
        except Exception as e:
            logger.debug(f"Could not get cache size info: {e}")