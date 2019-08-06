from django.db import models

class ZomatoRestaurants(models.Model):
    id = models.AutoField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100)
    zomato_id = models.CharField(max_length=10, default=None)
    cuisines = models.TextField()
    featured_image = models.URLField(max_length=250)
    average_cost_for_two = models.FloatField(default=0.0)
    thumb = models.URLField(max_length=250)
    aggregate_rating = models.CharField(max_length=4)
    rating_text = models.CharField(max_length=30)
    votes = models.IntegerField()
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=None)
    long = models.DecimalField(max_digits=9, decimal_places=6, default=None)


class GoogleRestaurants(models.Model):
    id = models.AutoField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100)
    reference = models.CharField(max_length=100)
    types = models.TextField()
    google_place_id = models.CharField(max_length=40, default=None)
    rating = models.CharField(max_length=4)
    user_ratings_total = models.IntegerField()
    price_level = models.IntegerField(default=None, blank=True)
    vicinity = models.CharField(max_length=400)
    contact = models.CharField(max_length=100,default=None)
    website = models.URLField(max_length=250,default=None)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=None)
    long = models.DecimalField(max_digits=9, decimal_places=6, default=None)
    photo_ref = models.TextField(default=None)
    photo_url = models.TextField(default=None)
