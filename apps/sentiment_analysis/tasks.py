# apps/sentiment_analysis/tasks.py
from celery import shared_task
from .models import SentimentAnalysis
from .services.sentiment_processor import SentimentProcessor
from apps.text_processing.models import ProcessedData
import logging

logger = logging.getLogger(__name__)

@shared_task
def apply_sentiment_to_processed_data(processed_data_id):
    """Apply sentiment analysis to a single processed data item."""
    try:
        processed_data = ProcessedData.objects.get(id=processed_data_id)
        if processed_data.is_analyzed_for_sentiment:
            logger.info(f"ProcessedData ID {processed_data_id} already analyzed for sentiment")
            return True

        processor = SentimentProcessor()
        entities_count = processor.process_document(processed_data)

        logger.info(f"Applied sentiment to ProcessedData ID {processed_data_id}, found {entities_count} sentiments")
        return True

    except Exception as e:
        logger.error(f"Error applying sentiment to ProcessedData ID {processed_data_id}: {str(e)}")
        return False

@shared_task
def apply_sentiment_to_all_unanalyzed():
    """Apply sentiment analysis to all unanalyzed ProcessedData instances."""
    from apps.text_processing.models import ProcessedData
    from .services.sentiment_processor import SentimentProcessor

    processor = SentimentProcessor()

    # Use a Djongo-compatible query
    unanalyzed_data = ProcessedData.objects.filter(is_analyzed_for_sentiment__exact=False)

    for processed_data in unanalyzed_data:
        try:
            entities_count = processor.process_document(processed_data)
            logger.info(f"Applied sentiment to ProcessedData ID {processed_data.id}, found {entities_count} sentiments")
        except Exception as e:
            logger.error(f"Error applying sentiment to ProcessedData ID {processed_data.id}: {str(e)}")