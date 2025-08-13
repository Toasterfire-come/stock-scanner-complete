"""
Database Index Optimization for Stock Scanner
Provides intelligent database indexing and query analysis
"""

from django.core.management.base import BaseCommand
from django.db import connection, models
from django.apps import apps
import logging
from typing import Dict, List, Any
from django.utils import timezone

logger = logging.getLogger(__name__)

class DatabaseIndexAnalyzer:
    """
    Analyzes database performance and suggests optimal indexes
    """
    
    def __init__(self):
        self.connection = connection
        self.vendor = connection.vendor
    
    def analyze_missing_indexes(self) -> Dict[str, List[str]]:
        """Analyze and suggest missing indexes for optimal performance"""
        suggestions = {}
        
        # Stock model optimization
        suggestions['stocks_stock'] = [
            # Primary lookups
            "CREATE INDEX IF NOT EXISTS idx_stock_ticker ON stocks_stock(ticker);",
            "CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stocks_stock(symbol);",
            "CREATE INDEX IF NOT EXISTS idx_stock_exchange ON stocks_stock(exchange);",
            
            # Performance-critical fields
            "CREATE INDEX IF NOT EXISTS idx_stock_current_price ON stocks_stock(current_price);",
            "CREATE INDEX IF NOT EXISTS idx_stock_market_cap ON stocks_stock(market_cap);",
            "CREATE INDEX IF NOT EXISTS idx_stock_volume ON stocks_stock(volume);",
            "CREATE INDEX IF NOT EXISTS idx_stock_change_percent ON stocks_stock(change_percent);",
            "CREATE INDEX IF NOT EXISTS idx_stock_last_updated ON stocks_stock(last_updated);",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_stock_exchange_market_cap ON stocks_stock(exchange, market_cap);",
            "CREATE INDEX IF NOT EXISTS idx_stock_price_volume ON stocks_stock(current_price, volume);",
            "CREATE INDEX IF NOT EXISTS idx_stock_updated_price ON stocks_stock(last_updated, current_price);",
            
            # Search optimization
            "CREATE INDEX IF NOT EXISTS idx_stock_name_search ON stocks_stock(company_name);",
            "CREATE INDEX IF NOT EXISTS idx_stock_ticker_name ON stocks_stock(ticker, company_name);",
        ]
        
        # Portfolio optimization
        suggestions['stocks_userportfolio'] = [
            "CREATE INDEX IF NOT EXISTS idx_portfolio_user ON stocks_userportfolio(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_public ON stocks_userportfolio(is_public);",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_user_created ON stocks_userportfolio(user_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_return ON stocks_userportfolio(total_return_percent);",
        ]
        
        # Portfolio holdings optimization
        suggestions['stocks_portfolioholding'] = [
            "CREATE INDEX IF NOT EXISTS idx_holding_portfolio ON stocks_portfolioholding(portfolio_id);",
            "CREATE INDEX IF NOT EXISTS idx_holding_stock ON stocks_portfolioholding(stock_id);",
            "CREATE INDEX IF NOT EXISTS idx_holding_portfolio_stock ON stocks_portfolioholding(portfolio_id, stock_id);",
            "CREATE INDEX IF NOT EXISTS idx_holding_purchase_date ON stocks_portfolioholding(purchase_date);",
        ]
        
        # Stock alerts optimization
        suggestions['stocks_stockalert'] = [
            "CREATE INDEX IF NOT EXISTS idx_alert_user ON stocks_stockalert(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_alert_stock ON stocks_stockalert(stock_id);",
            "CREATE INDEX IF NOT EXISTS idx_alert_active ON stocks_stockalert(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_alert_user_active ON stocks_stockalert(user_id, is_active);",
            "CREATE INDEX IF NOT EXISTS idx_alert_triggered ON stocks_stockalert(triggered_at);",
        ]
        
        # Stock prices optimization
        suggestions['stocks_stockprice'] = [
            "CREATE INDEX IF NOT EXISTS idx_price_stock ON stocks_stockprice(stock_id);",
            "CREATE INDEX IF NOT EXISTS idx_price_timestamp ON stocks_stockprice(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_price_stock_timestamp ON stocks_stockprice(stock_id, timestamp);",
        ]
        
        # User profile optimization
        suggestions['stocks_userprofile'] = [
            "CREATE INDEX IF NOT EXISTS idx_profile_user ON stocks_userprofile(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_profile_username ON stocks_userprofile(username);",
            "CREATE INDEX IF NOT EXISTS idx_profile_created ON stocks_userprofile(created_at);",
        ]
        
        # Membership optimization
        suggestions['stocks_membership'] = [
            "CREATE INDEX IF NOT EXISTS idx_membership_user ON stocks_membership(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_membership_plan ON stocks_membership(plan);",
            "CREATE INDEX IF NOT EXISTS idx_membership_active ON stocks_membership(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_membership_expires ON stocks_membership(expires_at);",
        ]
        
        return suggestions
    
    def create_missing_indexes(self) -> Dict[str, Any]:
        """Create missing indexes for optimal performance"""
        results = {
            'created': [],
            'skipped': [],
            'errors': []
        }
        
        suggestions = self.analyze_missing_indexes()
        
        with connection.cursor() as cursor:
            for table, indexes in suggestions.items():
                for index_sql in indexes:
                    try:
                        cursor.execute(index_sql)
                        results['created'].append(index_sql)
                        logger.info(f"Created index: {index_sql}")
                    except Exception as e:
                        if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                            results['skipped'].append(index_sql)
                        else:
                            results['errors'].append({'sql': index_sql, 'error': str(e)})
                            logger.error(f"Failed to create index: {index_sql} - {e}")
        
        logger.info(f"Index creation complete: {len(results['created'])} created, {len(results['skipped'])} skipped, {len(results['errors'])} errors")
        return results
    
    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze query performance and suggest optimizations"""
        analysis = {
            'slow_queries': [],
            'index_usage': {},
            'recommendations': []
        }
        
        if self.vendor == 'mysql':
            analysis.update(self._analyze_mysql_performance())
        elif self.vendor == 'postgresql':
            analysis.update(self._analyze_postgresql_performance())
        
        return analysis
    
    def _analyze_mysql_performance(self) -> Dict[str, Any]:
        """MySQL-specific performance analysis"""
        analysis = {
            'slow_queries': [],
            'index_usage': {},
            'recommendations': []
        }
        
        try:
            with connection.cursor() as cursor:
                # Check slow query log status
                cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
                slow_log = cursor.fetchone()
                
                # Check index cardinality for stock table
                cursor.execute("""
                    SELECT TABLE_NAME, INDEX_NAME, CARDINALITY 
                    FROM information_schema.STATISTICS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME LIKE 'stocks_%'
                    ORDER BY TABLE_NAME, CARDINALITY DESC
                """)
                
                index_stats = cursor.fetchall()
                analysis['index_usage'] = {
                    'total_indexes': len(index_stats),
                    'details': [
                        {'table': row[0], 'index': row[1], 'cardinality': row[2]}
                        for row in index_stats
                    ]
                }
                
                # Check table status
                cursor.execute("SHOW TABLE STATUS LIKE 'stocks_%'")
                table_stats = cursor.fetchall()
                
                for table_stat in table_stats:
                    table_name = table_stat[0]
                    rows = table_stat[4]  # Rows column
                    data_length = table_stat[6]  # Data_length column
                    
                    if rows and rows > 10000:  # Large tables
                        analysis['recommendations'].append(
                            f"Table {table_name} has {rows} rows - ensure proper indexing"
                        )
                
        except Exception as e:
            logger.error(f"MySQL performance analysis failed: {e}")
        
        return analysis
    
    def _analyze_postgresql_performance(self) -> Dict[str, Any]:
        """PostgreSQL-specific performance analysis"""
        analysis = {
            'slow_queries': [],
            'index_usage': {},
            'recommendations': []
        }
        
        try:
            with connection.cursor() as cursor:
                # Check index usage statistics
                cursor.execute("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE schemaname = 'public' 
                    AND tablename LIKE 'stocks_%'
                    ORDER BY idx_tup_read DESC
                """)
                
                index_stats = cursor.fetchall()
                analysis['index_usage'] = {
                    'total_indexes': len(index_stats),
                    'details': [
                        {
                            'schema': row[0], 'table': row[1], 'index': row[2],
                            'reads': row[3], 'fetches': row[4]
                        }
                        for row in index_stats
                    ]
                }
                
                # Check table sizes
                cursor.execute("""
                    SELECT tablename, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup
                    FROM pg_stat_user_tables 
                    WHERE tablename LIKE 'stocks_%'
                    ORDER BY n_live_tup DESC
                """)
                
                table_stats = cursor.fetchall()
                for table_stat in table_stats:
                    table_name = table_stat[0]
                    live_tuples = table_stat[4]
                    
                    if live_tuples and live_tuples > 10000:
                        analysis['recommendations'].append(
                            f"Table {table_name} has {live_tuples} rows - ensure proper indexing"
                        )
                
        except Exception as e:
            logger.error(f"PostgreSQL performance analysis failed: {e}")
        
        return analysis
    
    def get_table_statistics(self) -> Dict[str, Any]:
        """Get comprehensive table statistics"""
        stats = {}
        
        try:
            with connection.cursor() as cursor:
                if self.vendor == 'mysql':
                    cursor.execute("""
                        SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH
                        FROM information_schema.TABLES 
                        WHERE TABLE_SCHEMA = DATABASE() 
                        AND TABLE_NAME LIKE 'stocks_%'
                    """)
                    
                    for row in cursor.fetchall():
                        stats[row[0]] = {
                            'rows': row[1],
                            'data_size': row[2],
                            'index_size': row[3],
                            'total_size': (row[2] or 0) + (row[3] or 0)
                        }
                
                elif self.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT 
                            tablename,
                            n_live_tup as rows,
                            pg_total_relation_size(schemaname||'.'||tablename) as total_size
                        FROM pg_stat_user_tables 
                        WHERE tablename LIKE 'stocks_%'
                    """)
                    
                    for row in cursor.fetchall():
                        stats[row[0]] = {
                            'rows': row[1],
                            'total_size': row[2],
                            'data_size': row[2],  # Simplified for PostgreSQL
                            'index_size': 0
                        }
        
        except Exception as e:
            logger.error(f"Failed to get table statistics: {e}")
        
        return stats
    
    def optimize_database(self) -> Dict[str, Any]:
        """Perform comprehensive database optimization"""
        results = {
            'indexes_created': 0,
            'indexes_skipped': 0,
            'errors': [],
            'performance_analysis': {},
            'table_stats': {},
            'recommendations': []
        }
        
        # Create missing indexes
        index_results = self.create_missing_indexes()
        results['indexes_created'] = len(index_results['created'])
        results['indexes_skipped'] = len(index_results['skipped'])
        results['errors'].extend(index_results['errors'])
        
        # Analyze performance
        results['performance_analysis'] = self.analyze_query_performance()
        
        # Get table statistics
        results['table_stats'] = self.get_table_statistics()
        
        # Generate recommendations
        results['recommendations'] = self._generate_optimization_recommendations(results)
        
        return results
    
    def _generate_optimization_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        
        # Check table sizes
        for table, stats in analysis_results['table_stats'].items():
            if stats.get('rows', 0) > 100000:
                recommendations.append(f"Consider partitioning {table} - {stats['rows']} rows")
            
            if stats.get('total_size', 0) > 100 * 1024 * 1024:  # > 100MB
                recommendations.append(f"Large table {table} - consider archiving old data")
        
        # Check index efficiency
        if analysis_results['indexes_created'] > 10:
            recommendations.append("Many indexes created - monitor query performance")
        
        # Database-specific recommendations
        if self.vendor == 'mysql':
            recommendations.extend([
                "Enable slow query log for performance monitoring",
                "Consider using InnoDB storage engine for all tables",
                "Configure appropriate buffer pool size for InnoDB"
            ])
        elif self.vendor == 'postgresql':
            recommendations.extend([
                "Enable pg_stat_statements for query analysis",
                "Consider VACUUM and ANALYZE for table maintenance",
                "Configure appropriate shared_buffers size"
            ])
        
        return recommendations

class DatabaseIndexManagementCommand(BaseCommand):
    """
    Django management command for database index optimization
    """
    help = 'Optimize database indexes for Stock Scanner'
    
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
    
    def handle(self, *args, **options):
        analyzer = DatabaseIndexAnalyzer()
        
        self.stdout.write("🔍 Starting database optimization analysis...")
        
        if options['analyze_only']:
            # Only perform analysis
            analysis = analyzer.analyze_query_performance()
            stats = analyzer.get_table_statistics()
            
            self.stdout.write("📊 Performance Analysis:")
            self.stdout.write(f"  - Index usage data collected")
            self.stdout.write(f"  - {len(stats)} tables analyzed")
            
            for table, table_stats in stats.items():
                self.stdout.write(f"  - {table}: {table_stats.get('rows', 0)} rows")
        
        else:
            # Perform full optimization
            results = analyzer.optimize_database()
            
            self.stdout.write("✅ Database optimization completed:")
            self.stdout.write(f"  - {results['indexes_created']} indexes created")
            self.stdout.write(f"  - {results['indexes_skipped']} indexes already existed")
            self.stdout.write(f"  - {len(results['errors'])} errors occurred")
            
            if results['errors']:
                self.stdout.write("❌ Errors:")
                for error in results['errors']:
                    self.stdout.write(f"  - {error['sql']}: {error['error']}")
            
            if results['recommendations']:
                self.stdout.write("💡 Recommendations:")
                for rec in results['recommendations']:
                    self.stdout.write(f"  - {rec}")

# Global analyzer instance
db_analyzer = DatabaseIndexAnalyzer()

def check_and_create_indexes():
    """
    Utility function to check and create missing indexes
    """
    try:
        results = db_analyzer.create_missing_indexes()
        logger.info(f"Index check complete: {len(results['created'])} created, {len(results['errors'])} errors")
        return results
    except Exception as e:
        logger.error(f"Index creation failed: {e}")
        return {'created': [], 'skipped': [], 'errors': [{'error': str(e)}]}

def get_database_optimization_status() -> Dict[str, Any]:
    """
    Get current database optimization status
    """
    try:
        stats = db_analyzer.get_table_statistics()
        analysis = db_analyzer.analyze_query_performance()
        
        return {
            'table_count': len(stats),
            'total_rows': sum(s.get('rows', 0) for s in stats.values()),
            'total_size_mb': sum(s.get('total_size', 0) for s in stats.values()) / (1024 * 1024),
            'index_usage': analysis.get('index_usage', {}),
            'recommendations': analysis.get('recommendations', []),
            'last_analyzed': timezone.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get optimization status: {e}")
        return {'error': str(e)}