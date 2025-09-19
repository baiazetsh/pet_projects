# weather/ models.py
from django.db import models
from django.utils import timezone
import json

class WeatherCache(models.Model):
    city = models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    data = models.TextField() # raw json
    
    def is_fresh(self, minutes=10):
        return (timezone.now() - self.created_at).total_seconds() < minutes * 60

    def as_dict(self):
        return json.loads(self.data)

