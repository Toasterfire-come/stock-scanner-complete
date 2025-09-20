class StocksRouter:
    """Route read/write for stock-related apps to the 'stocks' database when configured."""

    app_label_for_stocks = { 'news', 'stocks' }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.app_label_for_stocks:
            return 'stocks'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.app_label_for_stocks:
            return 'stocks'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.app_label_for_stocks:
            return db == 'stocks'
        return db == 'default'

