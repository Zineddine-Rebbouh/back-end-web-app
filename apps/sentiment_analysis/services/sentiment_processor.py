# apps/sentiment_analysis/services/sentiment_processor.py
from transformers import pipeline
import logging
from django.conf import settings
from ..models import SentimentAnalysis, EntitySentiment
from apps.text_processing.models import ProcessedData
from apps.entity_recognition.models import ExtractedEntity

logger = logging.getLogger(__name__)

class SentimentProcessor:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="aubmindlab/bert-base-arabertv02")

    def analyze_document_sentiment(self, text):
        """Analyze sentiment at document level."""
        if not text or not isinstance(text, str):
            return None

        try:
            result = self.sentiment_analyzer(text)[0]
            label_map = {
                'POSITIVE': 'POSITIVE' if result['label'] == 'POS' else 'NEGATIVE',
                'NEGATIVE': 'NEGATIVE' if result['label'] == 'NEG' else 'POSITIVE',
            }
            label = label_map.get(result['label'], 'NEUTRAL')
            score = result['score'] if label in ['POSITIVE', 'NEGATIVE'] else 0.0
            confidence = min(1.0, max(0.0, score * 1.5))  # Adjust confidence scaling

            return {
                'label': label,
                'score': score,
                'confidence': confidence,
                'emotion_analysis': {'general': label.lower()}
            }
        except Exception as e:
            logger.error(f"Error analyzing document sentiment: {str(e)}")
            return None

    def analyze_entity_sentiment(self, text, entity_text):
        """Analyze sentiment specifically for an entity within the text."""
        if not text or not entity_text:
            return None

        try:
            # Simple heuristic: check if entity text appears in document
            if entity_text.lower() in text.lower():
                doc_sentiment = self.analyze_document_sentiment(text)
                if doc_sentiment:
                    return {
                        'label': doc_sentiment['label'],
                        'score': doc_sentiment['score'],
                        'confidence': doc_sentiment['confidence'] * 0.9,  # Slightly lower for entity-specific
                        'aspect_sentiments': [{'aspect': 'general', 'sentiment': doc_sentiment['label']}]
                    }
            return None
        except Exception as e:
            logger.error(f"Error analyzing entity sentiment for {entity_text}: {str(e)}")
            return None

    def process_document(self, processed_data):
        """Process a ProcessedData instance and apply sentiment analysis."""
        try:
            text = processed_data.clean_text or processed_data.normalized_text

            # Document-level sentiment
            doc_sentiment = self.analyze_document_sentiment(text)
            if not doc_sentiment:
                logger.error(f"No sentiment analysis possible for ProcessedData ID: {processed_data.id}")
                return 0

            # Save document sentiment
            sentiment_analysis = SentimentAnalysis.objects.create(
                processed_data=processed_data,
                raw_data=processed_data.raw_data,
                label=doc_sentiment['label'],
                score=doc_sentiment['score'],
                confidence=doc_sentiment['confidence'],
                emotion_analysis=doc_sentiment['emotion_analysis'],
                model_version="arabert_v1"
            )

            # Entity-level sentiment
            entities = processed_data.entities.all()
            for entity in entities:
                entity_sentiment = self.analyze_entity_sentiment(text, entity.text)
                if entity_sentiment:
                    EntitySentiment.objects.create(
                        sentiment_analysis=sentiment_analysis,
                        entity=entity,
                        label=entity_sentiment['label'],
                        score=entity_sentiment['score'],
                        confidence=entity_sentiment['confidence'],
                        aspect_sentiments=entity_sentiment['aspect_sentiments']
                    )

            # Mark as analyzed
            processed_data.is_analyzed_for_sentiment = True
            processed_data.save()

            logger.info(f"Applied sentiment analysis to ProcessedData ID: {processed_data.id}, found {len(entities)} entity sentiments")
            return len(entities) + 1  # Include document sentiment

        except Exception as e:
            logger.error(f"Error processing sentiment for ProcessedData ID {processed_data.id}: {str(e)}")
            return 0