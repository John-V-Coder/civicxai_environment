"""
Cognitive AI App Configuration
"""
from django.apps import AppConfig


class CognitiveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cognitive'
    verbose_name = 'Cognitive AI'
    
    def ready(self):
        """
        Called when Django starts
        Register signal handlers here
        """
        # Import signals to register them (use direct import to avoid __init__ cascade)
        from cognitive.core.signals import register_signals
        register_signals()
