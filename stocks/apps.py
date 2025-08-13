from django.apps import AppConfig


class StocksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stocks'
    
    def ready(self):
        """
        Initialize all optimization systems when Django starts
        """
        # Import and initialize all optimization modules
        try:
            # Database resilience
            from .database_resilience import initialize_database_resilience
            initialize_database_resilience()
            
            # Memory optimization
            from .memory_optimization import initialize_memory_optimization
            initialize_memory_optimization()
            
            # Error handling
            from .enhanced_error_handling import initialize_error_handling
            initialize_error_handling()
            
            # Compression optimization
            from .compression_optimization import initialize_compression_optimization
            initialize_compression_optimization()
            
            # Graceful shutdown (already auto-initializes)
            
            # Import signals to ensure they're registered
            from . import signals
            
            print("✅ Stock Scanner optimization systems initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Error initializing optimization systems: {e}")
            # Don't crash the app if optimizations fail to load
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize optimization systems: {e}")
