"""
Signal Handlers for Cognitive AI
Auto-process DataSource uploads
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from explainable_ai.models import DataSource
from .ingestion_pipeline import get_ingestion_pipeline

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DataSource)
def process_data_source(sender, instance, created, **kwargs):
    """
    Automatically process DataSource when created or updated
    
    Args:
        sender: The model class (DataSource)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    # Only process if it's a new data source and it's active
    if not created or not instance.is_active:
        return
    
    try:
        logger.info(f"Auto-processing DataSource: {instance.id} - {instance.title}")
        
        pipeline = get_ingestion_pipeline()
        source_id = f"DataSource_{instance.id}"
        
        # Process based on source type
        if instance.source_type == 'pdf' and instance.file:
            # Process PDF file
            pdf_path = instance.file.path
            result = pipeline.process_pdf_file(pdf_path, source_id)
            
            if result['success']:
                # Update summary if empty
                if not instance.summary:
                    topics = ', '.join(result.get('key_topics', []))
                    instance.summary = f"Auto-extracted topics: {topics}"
                    instance.save(update_fields=['summary'])
                
                logger.info(f"Successfully processed PDF: {instance.title} - {result['atoms_created']} atoms created")
            else:
                logger.error(f"Failed to process PDF {instance.title}: {result.get('error')}")
        
        elif instance.source_type == 'url' and instance.url:
            # For URLs, we'd need to fetch content first
            # This is a placeholder for future implementation
            logger.info(f"URL processing not yet implemented for: {instance.url}")
        
        elif instance.source_type == 'document' and instance.summary:
            # Process summary text
            result = pipeline.process_text(instance.summary, source_id)
            
            if result['success']:
                logger.info(f"Successfully processed text: {instance.title} - {result['atoms_created']} atoms created")
            else:
                logger.error(f"Failed to process text {instance.title}: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"Error in auto-processing DataSource {instance.id}: {e}")


def register_signals():
    """
    Register all signal handlers
    Call this in apps.py ready() method
    """
    # Signals are auto-connected via @receiver decorator
    logger.info("Cognitive AI signal handlers registered")
