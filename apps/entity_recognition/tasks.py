# apps/entity_recognition/tasks.py
from celery import shared_task
from .models import ExtractedEntity
from .services.ner_processor import NERProcessor
from apps.text_processing.models import ProcessedData
import logging

logger = logging.getLogger(__name__)

@shared_task
def apply_ner_to_processed_data(processed_data_id):
    """Apply NER to a single processed data item."""
    try:
        processed_data = ProcessedData.objects.get(id=processed_data_id)
        if processed_data.is_analyzed_for_entities:
            logger.info(f"ProcessedData ID {processed_data_id} already analyzed for entities")
            return True

        processor = NERProcessor()
        entities_count = processor.process_text(processed_data)

        logger.info(f"Applied NER to ProcessedData ID {processed_data_id}, found {entities_count} entities")
        return True

    except Exception as e:
        logger.error(f"Error applying NER to ProcessedData ID {processed_data_id}: {str(e)}")
        return False

@shared_task
def apply_ner_to_all_unanalyzed():
    """Apply NER to all unanalyzed processed data."""
    unanalyzed_data = ProcessedData.objects.filter(is_analyzed_for_entities=False)
    total_processed = 0

    for processed_data in unanalyzed_data:
        success = apply_ner_to_processed_data.delay(processed_data.id)
        if success:
            total_processed += 1

    logger.info(f"Applied NER to {total_processed} unanalyzed processed items")
    return f"Processed {total_processed} items"