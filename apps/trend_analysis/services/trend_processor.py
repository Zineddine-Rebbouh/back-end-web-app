# apps/trend_analysis/services/trend_processor.py
from collections import Counter
import logging
from django.utils import timezone
from django.db.models import Count
from ..models import Topic, Trend, AnalyticsResult
from apps.data_collection.models import RawData
from apps.entity_recognition.models import ExtractedEntity
from apps.sentiment_analysis.models import SentimentAnalysis
from datetime import timedelta

logger = logging.getLogger(__name__)

class TrendProcessor:
    def __init__(self):
        self.time_window = timedelta(days=1)  # Analyze trends over the last 24 hours

    def detect_topics(self):
        """Detect topics based on hashtags, keywords, and entities."""
        # Fetch recent raw data
        start_time = timezone.now() - self.time_window
        recent_data = RawData.objects.filter(collected_at__gte=start_time)

        # Aggregate hashtags
        hashtag_counts = Counter()
        for data in recent_data:
            hashtag_counts.update(data.hashtags)

        # Create or update topics
        for hashtag, count in hashtag_counts.most_common(5):  # Top 5 hashtags
            if count > 10:  # Minimum threshold for a topic
                topic, created = Topic.objects.get_or_create(
                    name=hashtag,
                    defaults={
                        'keywords': [hashtag],
                        'description': f"Discussion around {hashtag}",
                        'main_entities': self.get_related_entities(hashtag),
                        'metadata': {'tweet_count': count}
                    }
                )
                if not created:
                    topic.metadata['tweet_count'] = count
                    topic.last_updated = timezone.now()
                    topic.save()

        return Topic.objects.filter(last_updated__gte=start_time)

    def get_related_entities(self, hashtag):
        """Get entities related to a hashtag."""
        entities = ExtractedEntity.objects.filter(raw_data__hashtags__contains=[hashtag])
        return list(entities.values('catalog_entity__entity_id', 'catalog_entity__name')[:5])

    def analyze_trends(self, topic):
        """Analyze trends for a given topic."""
        start_time = timezone.now() - self.time_window
        related_data = RawData.objects.filter(hashtags__contains=[topic.name], collected_at__gte=start_time)

        # Calculate metrics
        tweet_count = related_data.count()
        sentiment_dist = SentimentAnalysis.objects.filter(
            raw_data__in=related_data
        ).aggregate(
            positive=Count('id', filter=models.Q(label__in=['POSITIVE', 'VERY_POSITIVE'])),
            neutral=Count('id', filter=models.Q(label='NEUTRAL')),
            negative=Count('id', filter=models.Q(label__in=['NEGATIVE', 'VERY_NEGATIVE']))
        )

        # Determine trend status
        status = 'emerging' if tweet_count < 50 else 'peaking' if tweet_count < 200 else 'declining'

        # Influential sources
        influential = related_data.order_by('-likes', '-shares')[:3].values_list('source_id', flat=True)

        # Create or update trend
        trend, created = Trend.objects.get_or_create(
            topic=topic,
            name=f"{topic.name} Trend",
            defaults={
                'description': f"Trend related to {topic.name}",
                'trend_metrics': {'tweet_count': tweet_count, 'growth_rate': 0},  # Add growth rate logic if needed
                'sentiment_distribution': sentiment_dist,
                'influential_sources': list(influential),
                'status': status
            }
        )
        if not created:
            trend.trend_metrics = {'tweet_count': tweet_count, 'growth_rate': 0}
            trend.sentiment_distribution = sentiment_dist
            trend.influential_sources = list(influential)
            trend.status = status
            trend.last_updated = timezone.now()
            trend.save()
        trend.sample_content.set(related_data[:5])  # Add sample tweets

        return trend

    def process_trends(self):
        """Process all trends and save analytics."""
        topics = self.detect_topics()
        trends = []

        for topic in topics:
            trend = self.analyze_trends(topic)
            trends.append(trend)

            # Save analytics result
            AnalyticsResult.objects.create(
                analysis_type='volume',
                time_period_start=timezone.now() - self.time_window,
                time_period_end=timezone.now(),
                data_points={'tweet_count': trend.trend_metrics['tweet_count']},
                insights=[f"Trend {trend.name} has {trend.trend_metrics['tweet_count']} tweets"],
                related_trends=[trend.id],
                metadata={'topic': topic.name}
            )

        logger.info(f"Processed {len(trends)} trends")
        return len(trends)