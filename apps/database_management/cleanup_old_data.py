# apps/text_processing/management/commands/cleanup_old_data.py
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Delete RawData and ProcessedData older than 30 days'

    def handle(self, *args, **options):
        try:
            # Your MongoDB Atlas connection string
            connection_string = "mongodb://zinedinerabouh:drackjosh123@cluster2-shard-00-00.04b8z.mongodb.net:27017,cluster2-shard-00-01.04b8z.mongodb.net:27017,cluster2-shard-00-02.04b8z.mongodb.net:27017/?ssl=true&replicaSet=atlas-sruy91-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster2"
            client = MongoClient(connection_string)
            db = client['tendances_sportives_db']
            cutoff = datetime.now() - timedelta(days=30)

            # Delete old RawData
            raw_result = db['data_collection_rawdata'].delete_many({
                'created_at': {'$lt': cutoff}
            })
            logger.info(f"Deleted {raw_result.deleted_count} old RawData records")

            # Delete old ProcessedData
            processed_result = db['text_processing_processeddata'].delete_many({
                'processed_at': {'$lt': cutoff}
            })
            logger.info(f"Deleted {processed_result.deleted_count} old ProcessedData records")

            self.stdout.write(self.style.SUCCESS('Cleanup completed'))
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))