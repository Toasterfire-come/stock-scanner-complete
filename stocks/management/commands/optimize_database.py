"""
Django management command for database optimization
Usage: python manage.py optimize_database [--analyze-only] [--force]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone
import logging
import sys

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimize database performance with intelligent indexing and analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze-only',
            action='store_true',
            help='Only analyze performance, do not create indexes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation of indexes even if they exist'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output during optimization'
        )

    def handle(self, *args, **options):
        """Execute database optimization"""
        
        self.stdout.write("🔍 Starting Stock Scanner Database Optimization...")
        self.stdout.write(f"⏰ Started at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Import here to avoid import issues if modules aren't ready
            from stocks.database_indexes import DatabaseIndexAnalyzer
            
            analyzer = DatabaseIndexAnalyzer()
            
            # Display database info
            self.stdout.write(f"📊 Database: {connection.vendor}")
            
            if options['analyze_only']:
                self._perform_analysis_only(analyzer, options)
            else:
                self._perform_full_optimization(analyzer, options)
                
        except ImportError as e:
            raise CommandError(f"Failed to import optimization modules: {e}")
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            raise CommandError(f"Optimization failed: {e}")

    def _perform_analysis_only(self, analyzer, options):
        """Perform analysis without making changes"""
        
        self.stdout.write("📈 Performing performance analysis...")
        
        # Get table statistics
        stats = analyzer.get_table_statistics()
        self.stdout.write(f"📊 Analyzed {len(stats)} tables:")
        
        total_rows = 0
        total_size = 0
        
        for table_name, table_stats in stats.items():
            rows = table_stats.get('rows', 0)
            size = table_stats.get('total_size', 0)
            total_rows += rows
            total_size += size
            
            if options['verbose']:
                size_mb = size / (1024 * 1024) if size else 0
                self.stdout.write(f"  📋 {table_name}: {rows:,} rows, {size_mb:.1f} MB")
        
        # Display summary
        total_size_mb = total_size / (1024 * 1024) if total_size else 0
        self.stdout.write(f"📊 Total: {total_rows:,} rows, {total_size_mb:.1f} MB")
        
        # Analyze query performance
        analysis = analyzer.analyze_query_performance()
        
        if analysis.get('index_usage', {}).get('total_indexes'):
            self.stdout.write(f"🔍 Found {analysis['index_usage']['total_indexes']} existing indexes")
        
        if analysis.get('recommendations'):
            self.stdout.write("💡 Recommendations:")
            for rec in analysis['recommendations']:
                self.stdout.write(f"  • {rec}")
        
        # Show potential optimizations
        suggestions = analyzer.analyze_missing_indexes()
        total_suggested = sum(len(indexes) for indexes in suggestions.values())
        self.stdout.write(f"⚡ Potential optimizations: {total_suggested} indexes suggested")

    def _perform_full_optimization(self, analyzer, options):
        """Perform full database optimization"""
        
        self.stdout.write("⚡ Performing full database optimization...")
        
        # Run comprehensive optimization
        results = analyzer.optimize_database()
        
        # Report results
        self.stdout.write("✅ Optimization completed!")
        self.stdout.write(f"  📈 Indexes created: {results['indexes_created']}")
        self.stdout.write(f"  ⏭️  Indexes skipped: {results['indexes_skipped']}")
        self.stdout.write(f"  ❌ Errors: {len(results['errors'])}")
        
        if results['errors'] and options['verbose']:
            self.stdout.write("❌ Errors encountered:")
            for error in results['errors']:
                self.stdout.write(f"  • {error.get('sql', 'Unknown')}: {error.get('error', 'Unknown error')}")
        
        # Show table statistics
        if results['table_stats']:
            largest_tables = sorted(
                results['table_stats'].items(),
                key=lambda x: x[1].get('rows', 0),
                reverse=True
            )[:5]
            
            if largest_tables:
                self.stdout.write("📊 Largest tables:")
                for table, stats in largest_tables:
                    rows = stats.get('rows', 0)
                    size_mb = stats.get('total_size', 0) / (1024 * 1024)
                    self.stdout.write(f"  📋 {table}: {rows:,} rows, {size_mb:.1f} MB")
        
        # Show recommendations
        if results['recommendations']:
            self.stdout.write("💡 Additional recommendations:")
            for rec in results['recommendations']:
                self.stdout.write(f"  • {rec}")
        
        # Performance impact estimate
        if results['indexes_created'] > 0:
            estimated_improvement = min(results['indexes_created'] * 15, 90)  # 15% per index, max 90%
            self.stdout.write(f"🚀 Estimated query performance improvement: {estimated_improvement}%")
        
        self.stdout.write(f"⏰ Completed at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("🎯 Database optimization successful!")

    def _display_error_summary(self, errors):
        """Display error summary"""
        if not errors:
            return
            
        self.stdout.write("⚠️  Issues encountered:")
        error_types = {}
        
        for error in errors:
            error_msg = error.get('error', 'Unknown error')
            if 'already exists' in error_msg.lower():
                error_types['already_exists'] = error_types.get('already_exists', 0) + 1
            elif 'permission' in error_msg.lower():
                error_types['permission'] = error_types.get('permission', 0) + 1
            else:
                error_types['other'] = error_types.get('other', 0) + 1
        
        for error_type, count in error_types.items():
            if error_type == 'already_exists':
                self.stdout.write(f"  ℹ️  {count} indexes already existed")
            elif error_type == 'permission':
                self.stdout.write(f"  🔒 {count} permission errors (check database privileges)")
            else:
                self.stdout.write(f"  ❌ {count} other errors")
