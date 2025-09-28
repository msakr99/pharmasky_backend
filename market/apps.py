# market/apps.py
from django.apps import AppConfig


class MarketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market'
    verbose_name = 'Market Management'
    
    def ready(self):
        # Import signals to register them
        import market.signals
