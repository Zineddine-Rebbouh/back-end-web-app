# apps/data_collection/services/twitter_scraper.py
import asyncio
from twikit import Client, TooManyRequests
from django.conf import settings
import logging
import random
import certifi
import os
import time
from datetime import datetime
from ..models import RawData

# os.environ["SSL_CERT_FILE"] = certifi.where()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SPORTS_HASHTAGS = [
    "#رياضة", "#كرة_القدم", "#كرة_السلة", "#تنس", "#ملاكمة", "#كرة_الطائرة",
]

class TwitterScraper:
    def __init__(self, credentials=None):
        self.client = Client(language='en-US', user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.credentials = credentials or {
            'username': settings.TWITTER_USERNAME,
            'email': settings.TWITTER_EMAIL,
            'password': settings.TWITTER_PASSWORD,
        }
        self.cookies_file = 'cookies.json'

    async def authenticate_client(self):
        """Authenticate using cookies first, fallback to login only if necessary."""
        if os.path.exists(self.cookies_file):
            logger.info("Loading cookies from cookies.json")
            self.client.load_cookies(self.cookies_file)
            try:
                user = await self.client.get_user_by_screen_name(self.credentials['username'])
                logger.info(f"Authentication successful. User ID: {user.id}, Username: {user.screen_name}")
                return
            except Exception as e:
                logger.warning(f"Cookies invalid or expired: {str(e)}. Attempting fresh login.")
        
        logger.info(f"Attempting login with username: {self.credentials['username']}")
        try:
            await self.client.login(
                auth_info_1=self.credentials['username'],
                auth_info_2=self.credentials['email'],
                password=self.credentials['password']
            )
            self.client.save_cookies(self.cookies_file)
            logger.info("Logged in and saved new cookies to cookies.json")
        except Exception as e:
            logger.error(f"Login failed: {str(e)}", exc_info=True)
            raise Exception(f"Failed to authenticate to Twitter/X: {str(e)}")

    async def get_tweets(self, tweets, query, max_results=100):
        """Fetch initial or next batch of tweets with a random delay."""
        if tweets is None:
            logger.info(f"Fetching initial tweets for query: {query}")
            tweets = await self.client.search_tweet(query=query, count=max_results, product='Latest')
        else:
            wait_time = random.randint(5, 10)
            logger.info(f"Waiting {wait_time} seconds before fetching next batch for {query}")
            time.sleep(wait_time)
            logger.info(f"Fetching next batch of tweets for query: {query}")
            tweets = await tweets.next()
        return tweets

    async def search_tweets_with_backoff(self, query, max_results=100, max_retries=5):
        """Search for tweets with rate limit handling and Arabic filtering."""
        tweets = None
        collected_tweets = []
        retries = 0
        
        while len(collected_tweets) < max_results and retries < max_retries:
            try:
                tweets = await self.get_tweets(tweets, query=query, max_results=max_results)
                if not tweets:
                    logger.warning(f"No more tweets found for query: {query}")
                    break
                
                arabic_tweets = [tweet for tweet in tweets if tweet.lang == 'ar']
                collected_tweets.extend(arabic_tweets)
                logger.info(f"Collected {len(collected_tweets)} Arabic tweets for query: {query}")
                if len(tweets) < max_results:
                    logger.info(f"Reached end of available tweets for {query}")
                    break
                
            except TooManyRequests:
                retries += 1
                wait_time = min(15 * 60, 2 ** retries * 60)
                logger.warning(f"Rate limit hit for {query}. Waiting {wait_time} seconds (Retry {retries}/{max_retries})")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Error fetching tweets for {query}: {str(e)}")
                retries += 1
                if retries >= max_retries:
                    logger.error(f"Max retries reached for query: {query}")
                    break
                time.sleep(30)
        
        return collected_tweets[:max_results]

    async def collect_tweets(self, hashtags, results_per_hashtag=100):
        """Collect tweets for hashtags and save to RawData."""
        results = {}
        for hashtag in hashtags:
            logger.info(f"Starting collection for hashtag: {hashtag}")
            tweets = await self.search_tweets_with_backoff(hashtag, max_results=results_per_hashtag)
            results[hashtag] = tweets

            for tweet in tweets:
                self.save_tweet_to_model(tweet, hashtag)

            logger.info(f"Processed {len(tweets)} Arabic tweets for {hashtag}")
            time.sleep(5)
        
        return results

    def save_tweet_to_model(self, tweet, hashtag):
        """Save tweet to RawData model."""
        try:
            obj, created = RawData.objects.get_or_create(
                source='twitter',
                source_id=str(tweet.id),
                defaults={
                    'content': tweet.text,
                    'author_id': str(tweet.user.id),
                    'author_name': tweet.user.screen_name,
                    'author_followers': tweet.user.followers_count if hasattr(tweet.user, 'followers_count') else 0,
                    'author_verified': tweet.user.verified if hasattr(tweet.user, 'verified') else False,
                    'likes': tweet.favorite_count,
                    'shares': tweet.retweet_count,
                    'language': tweet.lang,
                    'hashtags': [hashtag],
                    'created_at': datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y'),
                    'is_processed': False
                }
            )
            if created:
                logger.info(f"Created new tweet {tweet.id} in RawData")
            else:
                logger.info(f"Tweet {tweet.id} already exists in RawData")
        except Exception as e:
            logger.error(f"Failed to save tweet {tweet.id}: {str(e)}", exc_info=True)
            raise

    async def run(self):
        """Run the scraper."""
        await self.authenticate_client()
        return await self.collect_tweets(SPORTS_HASHTAGS)