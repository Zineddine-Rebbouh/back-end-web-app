# apps/entity_recognition/models.py
from django.db import models
from django.db.models import JSONField  # Updated import
from apps.text_processing.models import ProcessedData
from apps.data_collection.models import RawData
from django.utils import timezone

class EntityCatalog(models.Model):
    ENTITY_TYPES = (
        ('PLAYER', 'Player'),
        ('TEAM', 'Team'),
        ('COMPETITION', 'Competition'),
    )
    entity_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    aliases = models.JSONField(default=list, blank=True)  # Updated (assuming ArrayField, adjust if needed)
    metadata = JSONField(default=dict)  # Updated
    sport = models.CharField(max_length=50)
    external_references = JSONField(default=dict, blank=True)  # Updated
    image_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['sport']),
            models.Index(fields=['normalized_name']),
            models.Index(fields=['entity_id']),
        ]
        verbose_name_plural = "Entity catalog"
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class ExtractedEntity(models.Model):
    processed_data = models.ForeignKey(ProcessedData, on_delete=models.CASCADE, related_name='entities')
    raw_data = models.ForeignKey(RawData, on_delete=models.CASCADE, related_name='entities')
    text = models.CharField(max_length=255)
    normalized = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=20, choices=EntityCatalog.ENTITY_TYPES)
    start_char = models.IntegerField()
    end_char = models.IntegerField()
    confidence = models.FloatField()
    catalog_entity = models.ForeignKey(EntityCatalog, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentions')
    metadata = JSONField(default=dict, blank=True)  # Updated
    extracted_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=50, default="stanza_v1")
    
    class Meta:
        indexes = [
            models.Index(fields=['entity_type']),
            models.Index(fields=['normalized']),
            models.Index(fields=['extracted_at']),
            models.Index(fields=['processed_data', 'raw_data']),
        ]
    
    def __str__(self):
        return f"{self.text} ({self.entity_type})"

class EntityRelationship(models.Model):
    RELATIONSHIP_TYPES = (
        ('PLAYS_FOR', 'Plays For'),
        ('COMPETES_IN', 'Competes In'),
        ('COMPETES_AGAINST', 'Competes Against'),
    )
    entity1 = models.ForeignKey(EntityCatalog, on_delete=models.CASCADE, related_name='relationships_as_source')
    entity2 = models.ForeignKey(EntityCatalog, on_delete=models.CASCADE, related_name='relationships_as_target')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    confidence = models.FloatField()
    extracted_from = models.ForeignKey(ProcessedData, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('entity1', 'entity2', 'relationship')
        indexes = [
            models.Index(fields=['relationship']),
            models.Index(fields=['extracted_from']),
        ]
    
    def __str__(self):
        return f"{self.entity1.name} {self.get_relationship_display()} {self.entity2.name}"