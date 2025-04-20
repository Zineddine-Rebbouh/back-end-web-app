# apps/data_collection/tasks.py
from celery import shared_task
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
from apps.data_collection.models import RawData, DataSource
from pymongo import MongoClient
import logging
import time
import random
from datetime import datetime

logger = logging.getLogger(__name__)

def get_youtube_datasource():
    """Fetch active YouTube DataSource using pymongo to bypass djongo."""
    try:
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        sources = db['data_collection_datasource'].find({"is_active": True, "source_type": "youtube"})
        return list(sources)
    except Exception as e:
        logger.error(f"Error querying DataSource with pymongo: {str(e)}")
        return []

@shared_task
def collect_youtube_data():
    """Collect YouTube comments using YouTube Data API v3 and save to RawData."""
    try:
        # Initialize YouTube client
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        
        # Get active YouTube DataSource
        sources = get_youtube_datasource()
        if not sources:
            # Fallback to default keywords if no DataSource found
            logger.warning("No active YouTube DataSource found, using default keywords")
            sources = [{
                "collection_rules": {
                    "keywords": ["رياضة", "كرة_القدم", "كرة_السلة", "تنس", "ملاكمة", "كرة_الطائرة"],
                    "max_videos": 10,
                    "max_comments": 50
                }
            }]

        total_comments = 0
        for source in sources:
            keywords = source['collection_rules'].get('keywords', [
                'رياضة', 'كرة_القدم', 'كرة_السلة', 'تنس', 'ملاكمة', 'كرة_الطائرة'
            ])
            max_videos = source['collection_rules'].get('max_videos', 10)
            max_comments_per_video = source['collection_rules'].get('max_comments', 50)

            for query in keywords:
                logger.info(f"Searching YouTube videos for query: {query}")
                
                # Search for videos
                try:
                    search_response = youtube.search().list(
                        q=query,
                        type='video',
                        part='id',
                        maxResults=max_videos,
                        relevanceLanguage='ar'
                    ).execute()
                    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
                    logger.info(f"Found {len(video_ids)} videos for query: {query}")
                except HttpError as e:
                    logger.error(f"Error searching videos for {query}: {str(e)}")
                    continue

                # Collect comments for each video
                for video_id in video_ids:
                    logger.info(f"Collecting comments for video: {video_id}")
                    comments = []
                    try:
                        # Initial comment request
                        request = youtube.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            maxResults=50,
                            textFormat='plainText'
                        )
                        response = request.execute()

                        # Process comments
                        for item in response['items']:
                            comment = item['snippet']['topLevelComment']['snippet']
                            comments.append({
                                'text': comment['textDisplay'],
                                'likes': comment.get('likeCount', 0),
                                'published_at': comment['publishedAt'],
                                'author': comment['authorDisplayName']
                            })

                        # Paginate comments
                        while len(comments) < max_comments_per_video and 'nextPageToken' in response:
                            request = youtube.commentThreads().list(
                                part='snippet',
                                videoId=video_id,
                                pageToken=response['nextPageToken'],
                                maxResults=50,
                                textFormat='plainText'
                            )
                            response = request.execute()
                            for item in response['items']:
                                comment = item['snippet']['topLevelComment']['snippet']
                                comments.append({
                                    'text': comment['textDisplay'],
                                    'likes': comment.get('likeCount', 0),
                                    'published_at': comment['publishedAt'],
                                    'author': comment['authorDisplayName']
                                })
                            if len(comments) >= max_comments_per_video:
                                break

                        # Save comments to RawData
                        for comment in comments:
                            try:
                                obj, created = RawData.objects.get_or_create(
                                    source='youtube',
                                    source_id=f"{video_id}_{hash(comment['text'])}",
                                    defaults={
                                        'content': comment['text'],
                                        'author_id': '',
                                        'author_name': comment['author'],
                                        'author_followers': 0,
                                        'author_verified': False,
                                        'likes': comment['likes'],
                                        'shares': 0,
                                        'language': 'ar',
                                        'hashtags': [f"#{query}"],
                                        'created_at': datetime.strptime(comment['published_at'], '%Y-%m-%dT%H:%M:%SZ'),
                                        'is_processed': False
                                    }
                                )
                                if created:
                                    logger.info(f"Created new comment {video_id}_{hash(comment['text'])} in RawData")
                                else:
                                    logger.info(f"Comment {video_id}_{hash(comment['text'])} already exists in RawData")
                                total_comments += 1
                            except Exception as e:
                                logger.error(f"Error saving comment for video {video_id}: {str(e)}")

                        logger.info(f"Collected {len(comments)} comments for video: {video_id}")
                        time.sleep(random.randint(1, 2))

                    except HttpError as e:
                        logger.error(f"Error fetching comments for video {video_id}: {str(e)}")
                        continue

                time.sleep(random.randint(2, 5))

        return f"Collected {total_comments} new YouTube comments"
    except Exception as e:
        logger.error(f"Error in collect_youtube_data: {str(e)}")
        raise