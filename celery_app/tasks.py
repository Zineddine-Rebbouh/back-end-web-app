# celery_app/tasks.py
from celery import shared_task, chain
# from apps.data_collection.tasks import collect_twitter_data
from apps.data_collection.tasks import collect_youtube_data
from apps.text_processing.tasks import process_all_unprocessed_data
from apps.entity_recognition.tasks import apply_ner_to_all_unanalyzed
from apps.sentiment_analysis.tasks import apply_sentiment_to_all_unanalyzed
from apps.trend_analysis.tasks import analyze_trends
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_full_pipeline():
    """Run the full pipeline sequentially after midnight."""
    try:
        # Chain tasks in sequence
        pipeline = chain(
            # collect_twitter_data.s(),
            collect_youtube_data.s(),
            process_all_unprocessed_data.s(),
            apply_ner_to_all_unanalyzed.s(),
            apply_sentiment_to_all_unanalyzed.s(),
            analyze_trends.s()
        )
        result = pipeline.apply_async()

        logger.info("Started full pipeline rerun at midnight")
        return "Full pipeline scheduled successfully"

    except Exception as e:
        logger.error(f"Error scheduling full pipeline: {str(e)}")
        return False