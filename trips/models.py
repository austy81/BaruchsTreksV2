from django.db import models

# Create your models here.

class Trip(models.Model):
    partition_key = models.CharField(max_length=100)
    row_key = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    length_hours = models.FloatField(default=0)
    parking_json = models.TextField(blank=True, null=True)  # Stored as JSON string
    high_point_json = models.TextField(blank=True, null=True)  # Stored as JSON string
    meters_ascend = models.IntegerField(default=0)
    meters_descend = models.IntegerField(default=0)
    uiaa_grade = models.CharField(max_length=50, blank=True, null=True)
    alpine_grade = models.CharField(max_length=50, blank=True, null=True)
    trip_class = models.CharField(max_length=50, blank=True, null=True)
    ferata_grade = models.CharField(max_length=50, blank=True, null=True)
    participants = models.TextField(blank=True, null=True)
    trip_completed_on = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def parking_coordinates(self):
        """Return parking coordinates as a tuple (latitude, longitude) if available"""
        import json
        if self.parking_json:
            try:
                data = json.loads(self.parking_json)
                return (data.get('Latitude'), data.get('Longtitude'))
            except:
                return None
        return None
    
    @property
    def high_point_coordinates(self):
        """Return high point coordinates as a tuple (latitude, longitude) if available"""
        import json
        if self.high_point_json:
            try:
                data = json.loads(self.high_point_json)
                return (data.get('Latitude'), data.get('Longtitude'))
            except:
                return None
        return None
