# apps/text_processing/tasks.py
from celery import shared_task
from .services.text_processor import TextProcessor
from pymongo import MongoClient
from django.conf import settings
import logging
import json
from datetime import datetime
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

@shared_task
def process_raw_data(raw_data_id):
    """Process a single raw data item and save the processed result using pymongo."""
    try:
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        raw_data = db['data_collection_rawdata'].find_one({'_id': ObjectId(raw_data_id)})
        if not raw_data:
            logger.error(f"Raw data ID {raw_data_id} not found")
            return False
        
        processor = TextProcessor()
        result = processor.process(raw_data['content'])
        
        if result is None:
            logger.error(f"Failed to process raw data ID: {raw_data_id}")
            return False
        
        try:
            hashtags = json.loads(raw_data['hashtags'])
            hashtags = [h.encode().decode('unicode_escape') for h in hashtags]
        except Exception as e:
            logger.warning(f"Failed to parse hashtags for ID {raw_data_id}: {str(e)}")
            hashtags = []
        
        processed_data = {
            'raw_data': raw_data_id,
            'clean_text': result['clean_text'],
            'normalized_text': result['normalized_text'],
            'tokens': result['tokens'],
            'word_count': result['word_count'],
            'char_count': result['char_count'],
            'language_confidence': result['language_confidence'],
            'processing_metadata': result['processing_metadata'],
            'is_valid': True,
            'processed_at': datetime.now(),
            'is_analyzed_for_entities': False,
            'is_analyzed_for_sentiment': False,
            'entities': [],
            'sentiment': None,
            'hashtags': hashtags
        }
        
        db['text_processing_processeddata'].update_one(
            {'raw_data': raw_data_id},
            {'$set': processed_data},
            upsert=True
        )
        
        db['data_collection_rawdata'].update_one(
            {'_id': ObjectId(raw_data_id)},
            {'$set': {'is_processed': True}}
        )
        
        logger.info(f"Processed data for RawData ID: {raw_data_id}")
        return True
    except Exception as e:
        logger.error(f"Error processing raw data ID {raw_data_id}: {str(e)}")
        return False

@shared_task
def process_all_unprocessed_data():
    """Process all unprocessed raw data using pymongo."""
    try:
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        unprocessed_data = db['data_collection_rawdata'].find({'is_processed': False})
        total_processed = 0
        
        for raw_data in unprocessed_data:
            try:
                raw_data_id = str(raw_data['_id'])
                success = process_raw_data.delay(raw_data_id)
                if success:
                    total_processed += 1
            except Exception as e:
                logger.error(f"Error queuing raw data ID {raw_data['_id']}: {str(e)}")
        
        logger.info(f"Queued {total_processed} unprocessed items for processing")
        return f"Queued {total_processed} items"
    except Exception as e:
        logger.error(f"Error in process_all_unprocessed_data: {str(e)}")
        raise