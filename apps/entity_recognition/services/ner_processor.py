# apps/entity_recognition/services/ner_processor.py
import stanza
import logging
from django.conf import settings
from ..models import EntityCatalog, ExtractedEntity
from apps.text_processing.models import ProcessedData

logger = logging.getLogger(__name__)

class NERProcessor:
    def __init__(self):
        self.nlp = stanza.Pipeline(lang='ar', processors='tokenize,ner', use_gpu=False)  # Adjust for your setup
        self.valid_types = {t[0] for t in EntityCatalog.ENTITY_TYPES}  # Set of valid entity types

    def extract_entities(self, text):
        """Extract entities from processed text using Stanza, filtering for valid types."""
        if not text or not isinstance(text, str):
            return []

        doc = self.nlp(text)
        entities = []

        for sentence in doc.sentences:
            for ent in sentence.ents:
                # Map Stanza entity types to our ENTITY_TYPES (simplified mapping)
                mapped_type = self.map_stanza_type(ent.type)
                if mapped_type in self.valid_types:
                    entities.append({
                        'text': ent.text,
                        'type': mapped_type,
                        'start_char': ent.start_char,
                        'end_char': ent.end_char,
                        'confidence': 0.9  # Default confidence; adjust based on model output
                    })

        return entities

    def map_stanza_type(self, stanza_type):
        """Map Stanza entity types to our custom types."""
        type_mapping = {
            'PERSON': 'PLAYER',  # Assume persons are players
            'ORGANIZATION': 'TEAM',  # Assume organizations are teams
            'EVENT': 'COMPETITION',  # Assume events are competitions
            # Add more mappings as needed
        }
        return type_mapping.get(stanza_type, 'PLAYER')  # Default to PLAYER if unknown

    def link_to_catalog(self, entity_text, entity_type):
        """Link extracted entity to EntityCatalog or create new if not found."""
        normalized = entity_text.lower().strip()
        catalog_entity = EntityCatalog.objects.filter(normalized_name=normalized, type=entity_type).first()

        if not catalog_entity:
            # Create new entity if not found
            catalog_entity = EntityCatalog.objects.create(
                entity_id=f"ent_{len(EntityCatalog.objects.all())+1}",
                name=entity_text,
                normalized_name=normalized,
                type=entity_type,
                sport="general",  # Adjust based on context or add logic
                metadata={'source': 'automatic'}
            )

        return catalog_entity

    def process_text(self, processed_data):
        """Process a ProcessedData instance and extract entities."""
        try:
            # Use cleaned or normalized text for NER
            text = processed_data.clean_text or processed_data.normalized_text

            # Extract entities
            entities = self.extract_entities(text)

            # Save each entity
            for entity in entities:
                extracted_entity = ExtractedEntity.objects.create(
                    processed_data=processed_data,
                    raw_data=processed_data.raw_data,
                    text=entity['text'],
                    normalized=entity['text'].lower().strip(),
                    entity_type=entity['type'],
                    start_char=entity['start_char'],
                    end_char=entity['end_char'],
                    confidence=entity['confidence'],
                    catalog_entity=self.link_to_catalog(entity['text'], entity['type']),
                    model_version="stanza_v1"
                )

            # Mark as analyzed
            processed_data.is_analyzed_for_entities = True
            processed_data.save()

            logger.info(f"Extracted {len(entities)} entities from ProcessedData ID: {processed_data.id}")
            return len(entities)

        except Exception as e:
            logger.error(f"Error processing NER for ProcessedData ID {processed_data.id}: {str(e)}")
            return 0