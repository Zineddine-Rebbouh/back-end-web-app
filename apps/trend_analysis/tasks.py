# apps/trend_analysis/tasks.py
from celery import shared_task
from .services.trend_processor import TrendProcessor
import logging

logger = logging.getLogger(__name__)

@shared_task
def analyze_trends():
    """Analyze trends from all recent data."""
    try:
        processor = TrendProcessor()
        trend_count = processor.process_trends()

        logger.info(f"Analyzed and processed {trend_count} trends")
        return f"Processed {trend_count} trends"

    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        return False