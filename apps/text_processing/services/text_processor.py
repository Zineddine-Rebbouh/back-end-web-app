# apps/text_processing/services/text_processor.py
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.normalize import (
    normalize_alef_maksura_ar,
    normalize_teh_marbuta_ar,
    normalize_alef_ar
)
from camel_tools.utils.dediac import dediac_ar
import re
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        self.stopwords = set()
        self.tokenizer = simple_word_tokenize

    def clean_text(self, text):
        if not text or not isinstance(text, str):
            return ""
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@[\w]+', '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'[^\u0600-\u06FF\s]', '', text)
        return text.strip()

    def normalize_text(self, text):
        if not text:
            return ""
        normalized = dediac_ar(text)
        normalized = normalize_alef_ar(normalized)
        normalized = normalize_alef_maksura_ar(normalized)
        normalized = normalize_teh_marbuta_ar(normalized)
        return normalized

    def tokenize_text(self, text):
        if not text:
            return []
        tokens = self.tokenizer(text)
        return [token for token in tokens if token not in self.stopwords]

    def process(self, raw_text):
        try:
            clean_text = self.clean_text(raw_text)
            normalized_text = self.normalize_text(clean_text)
            tokens = self.tokenize_text(normalized_text)
            return {
                'clean_text': clean_text,
                'normalized_text': normalized_text,
                'tokens': tokens,
                'word_count': len(tokens),
                'char_count': len(clean_text),
                'language_confidence': 0.95,
                'processing_metadata': {
                    'tools_used': ['camel-tools'],
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return None